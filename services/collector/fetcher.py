"""
HTTP fetcher with exponential backoff, rate limiting, and caching.
"""

import asyncio
import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import aiohttp


@dataclass
class FetchResult:
    """Result of a fetch operation"""
    content: str | bytes
    url: str
    status_code: int
    headers: Dict[str, str]
    fetched_at: datetime
    from_cache: bool = False


@dataclass
class CacheEntry:
    """Cached response with TTL"""
    result: FetchResult
    expires_at: datetime


class Fetcher:
    """
    Async HTTP fetcher with:
    - Exponential backoff on failures
    - Per-domain rate limiting
    - Response caching with TTL
    - Custom headers per source
    """

    def __init__(
        self,
        default_timeout: int = 30,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        cache_ttl_minutes: int = 5,
        rate_limit_per_second: float = 2.0,
    ):
        self.default_timeout = default_timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.cache_ttl_minutes = cache_ttl_minutes
        self.rate_limit_per_second = rate_limit_per_second

        # In-memory cache
        self._cache: Dict[str, CacheEntry] = {}

        # Rate limiting: track last request time per domain
        self._last_request: Dict[str, float] = {}

        # Default headers
        self._default_headers = {
            'User-Agent': 'FaultWatch/2.0 (https://fault.watch; data collection)',
            'Accept': 'application/json, text/html, application/xml, */*',
        }

        # Session will be created on first use
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.default_timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._default_headers,
            )
        return self._session

    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL for rate limiting"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    async def _wait_for_rate_limit(self, domain: str):
        """Wait if needed to respect rate limit"""
        if domain in self._last_request:
            elapsed = time.time() - self._last_request[domain]
            min_interval = 1.0 / self.rate_limit_per_second
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
        self._last_request[domain] = time.time()

    def _get_cache_key(self, url: str, headers: Dict[str, str]) -> str:
        """Generate cache key from URL and relevant headers"""
        key_content = f"{url}:{sorted(headers.items())}"
        return hashlib.md5(key_content.encode()).hexdigest()

    def _check_cache(self, cache_key: str) -> Optional[FetchResult]:
        """Check if valid cached response exists"""
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if datetime.utcnow() < entry.expires_at:
                result = entry.result
                result.from_cache = True
                return result
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
        return None

    def _store_cache(self, cache_key: str, result: FetchResult):
        """Store response in cache"""
        expires_at = datetime.utcnow() + timedelta(minutes=self.cache_ttl_minutes)
        self._cache[cache_key] = CacheEntry(result=result, expires_at=expires_at)

    def _clean_cache(self):
        """Remove expired cache entries"""
        now = datetime.utcnow()
        expired = [k for k, v in self._cache.items() if v.expires_at < now]
        for k in expired:
            del self._cache[k]

    async def fetch(
        self,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict] = None,
        timeout: Optional[int] = None,
        use_cache: bool = True,
    ) -> FetchResult:
        """
        Fetch URL with retries and exponential backoff.

        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, etc.)
            headers: Additional headers
            data: Form data for POST
            json_data: JSON data for POST
            timeout: Override default timeout
            use_cache: Whether to use caching (GET only)

        Returns:
            FetchResult with content and metadata

        Raises:
            Exception after max retries exceeded
        """
        headers = headers or {}
        merged_headers = {**self._default_headers, **headers}

        # Check cache for GET requests
        if use_cache and method.upper() == 'GET':
            cache_key = self._get_cache_key(url, merged_headers)
            cached = self._check_cache(cache_key)
            if cached:
                return cached

        domain = self._get_domain(url)
        session = await self._get_session()

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                # Respect rate limit
                await self._wait_for_rate_limit(domain)

                # Make request
                async with session.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    data=data,
                    json=json_data,
                    timeout=aiohttp.ClientTimeout(total=timeout or self.default_timeout),
                ) as response:

                    content = await response.read()

                    # Try to decode as text
                    try:
                        content = content.decode('utf-8')
                    except UnicodeDecodeError:
                        pass  # Keep as bytes

                    result = FetchResult(
                        content=content,
                        url=str(response.url),
                        status_code=response.status,
                        headers=dict(response.headers),
                        fetched_at=datetime.utcnow(),
                        from_cache=False,
                    )

                    # Check for success
                    if 200 <= response.status < 300:
                        # Store in cache for GET requests
                        if use_cache and method.upper() == 'GET':
                            self._store_cache(cache_key, result)
                        return result

                    # Non-retryable status codes
                    if response.status in [400, 401, 403, 404]:
                        return result

                    # Retryable errors (5xx, 429)
                    last_exception = Exception(f"HTTP {response.status}: {url}")

            except asyncio.TimeoutError as e:
                last_exception = e
            except aiohttp.ClientError as e:
                last_exception = e

            # Exponential backoff
            if attempt < self.max_retries - 1:
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                await asyncio.sleep(delay)

        # All retries exhausted
        raise last_exception or Exception(f"Failed to fetch {url} after {self.max_retries} attempts")

    async def fetch_json(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict:
        """Convenience method to fetch and parse JSON"""
        import json
        result = await self.fetch(url, headers=headers, **kwargs)
        if isinstance(result.content, bytes):
            return json.loads(result.content.decode('utf-8'))
        return json.loads(result.content)

    async def fetch_xml(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """Convenience method to fetch and parse XML"""
        from xml.etree import ElementTree
        result = await self.fetch(url, headers=headers, **kwargs)
        content = result.content
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return ElementTree.fromstring(content)

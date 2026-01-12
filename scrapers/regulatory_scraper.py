"""
Regulatory Scraper
Monitors CFTC, Federal Reserve, and other regulatory releases
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class RegulatoryRelease:
    source: str
    title: str
    release_type: str
    date: datetime
    url: str
    description: str
    keywords_found: List[str]
    is_critical: bool

    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'title': self.title,
            'release_type': self.release_type,
            'date': self.date.isoformat(),
            'url': self.url,
            'description': self.description,
            'keywords_found': self.keywords_found,
            'is_critical': self.is_critical,
        }


@dataclass
class COTReport:
    report_date: datetime
    metal: str
    commercial_long: int
    commercial_short: int
    commercial_net: int
    non_commercial_long: int
    non_commercial_short: int
    non_commercial_net: int
    total_open_interest: int

    def to_dict(self) -> Dict:
        return {
            'report_date': self.report_date.isoformat(),
            'metal': self.metal,
            'commercial_long': self.commercial_long,
            'commercial_short': self.commercial_short,
            'commercial_net': self.commercial_net,
            'non_commercial_long': self.non_commercial_long,
            'non_commercial_short': self.non_commercial_short,
            'non_commercial_net': self.non_commercial_net,
            'total_open_interest': self.total_open_interest,
        }


class RegulatoryScraper:
    """Scrape regulatory agencies for relevant releases"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'FaultWatch/1.0 Regulatory Monitor',
        }

        # Regulatory sources
        self.sources = {
            'cftc': {
                'base_url': 'https://www.cftc.gov',
                'releases': '/PressRoom/PressReleases',
                'enforcement': '/LawRegulation/Enforcement',
                'cot_url': 'https://www.cftc.gov/dea/futures/other_lf.htm',
            },
            'fed': {
                'base_url': 'https://www.federalreserve.gov',
                'releases': '/newsevents/pressreleases.htm',
                'fomc': '/monetarypolicy/fomccalendars.htm',
                'h41': '/releases/h41/',
            },
            'fdic': {
                'base_url': 'https://www.fdic.gov',
                'releases': '/news/press-releases/',
                'failures': '/resources/resolutions/bank-failures/',
            },
            'occ': {
                'base_url': 'https://www.occ.gov',
                'releases': '/news-issuances/news-releases/',
                'enforcement': '/topics/laws-and-regulations/enforcement-actions/',
            },
        }

        # Keywords for critical releases
        self.critical_keywords = [
            'silver', 'gold', 'precious metal', 'commodity',
            'manipulation', 'spoofing', 'enforcement',
            'morgan stanley', 'citigroup', 'hsbc', 'ubs', 'jpmorgan',
            'bank failure', 'systemic', 'emergency',
            'position limits', 'delivery', 'default',
        ]

        self.cache: Dict[str, any] = {}
        self.cache_ttl = 1800  # 30 minutes
        self.last_fetch: Dict[str, datetime] = {}

        # COT history for trend analysis
        self.cot_history: List[COTReport] = []

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch webpage content"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _check_keywords(self, text: str) -> List[str]:
        """Check text for critical keywords"""
        text_lower = text.lower()
        found = []
        for kw in self.critical_keywords:
            if kw in text_lower:
                found.append(kw)
        return found

    def get_cftc_releases(self, days: int = 30) -> List[RegulatoryRelease]:
        """Get CFTC press releases"""
        cache_key = f'cftc_releases_{days}'

        if cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        url = f"{self.sources['cftc']['base_url']}{self.sources['cftc']['releases']}"
        html = self._fetch_page(url)

        if not html:
            return self.cache.get(cache_key, [])

        releases = []
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            soup = BeautifulSoup(html, 'html.parser')

            for item in soup.find_all('div', class_='views-row'):
                title_elem = item.find('a')
                date_elem = item.find('span', class_='date-display-single')

                if title_elem and date_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    if not url.startswith('http'):
                        url = f"{self.sources['cftc']['base_url']}{url}"

                    # Parse date
                    date_text = date_elem.get_text(strip=True)
                    try:
                        release_date = datetime.strptime(date_text, '%B %d, %Y')
                    except ValueError:
                        release_date = datetime.now()

                    if release_date < cutoff_date:
                        continue

                    keywords = self._check_keywords(title)

                    release = RegulatoryRelease(
                        source='CFTC',
                        title=title,
                        release_type='press_release',
                        date=release_date,
                        url=url,
                        description=title,
                        keywords_found=keywords,
                        is_critical=len(keywords) >= 2 or 'enforcement' in title.lower(),
                    )
                    releases.append(release)

        except Exception as e:
            logger.error(f"Error parsing CFTC releases: {e}")

        self.cache[cache_key] = releases
        self.last_fetch[cache_key] = datetime.now()

        return releases

    def get_cftc_enforcement(self) -> List[RegulatoryRelease]:
        """Get CFTC enforcement actions"""
        url = f"{self.sources['cftc']['base_url']}{self.sources['cftc']['enforcement']}"
        html = self._fetch_page(url)

        if not html:
            return []

        releases = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            for item in soup.find_all('div', class_='views-row'):
                title_elem = item.find('a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    if not link.startswith('http'):
                        link = f"{self.sources['cftc']['base_url']}{link}"

                    keywords = self._check_keywords(title)

                    release = RegulatoryRelease(
                        source='CFTC',
                        title=title,
                        release_type='enforcement',
                        date=datetime.now(),
                        url=link,
                        description=title,
                        keywords_found=keywords,
                        is_critical=True,
                    )
                    releases.append(release)

        except Exception as e:
            logger.error(f"Error parsing CFTC enforcement: {e}")

        return releases

    def get_fed_releases(self, days: int = 30) -> List[RegulatoryRelease]:
        """Get Federal Reserve press releases"""
        cache_key = f'fed_releases_{days}'

        if cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        url = f"{self.sources['fed']['base_url']}{self.sources['fed']['releases']}"
        html = self._fetch_page(url)

        if not html:
            return self.cache.get(cache_key, [])

        releases = []
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            soup = BeautifulSoup(html, 'html.parser')

            for item in soup.find_all('div', class_='row'):
                title_elem = item.find('a')
                date_elem = item.find('time')

                if title_elem and date_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    if not link.startswith('http'):
                        link = f"{self.sources['fed']['base_url']}{link}"

                    date_text = date_elem.get('datetime', '')
                    try:
                        release_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                    except ValueError:
                        release_date = datetime.now()

                    if release_date < cutoff_date:
                        continue

                    keywords = self._check_keywords(title)

                    release = RegulatoryRelease(
                        source='Federal Reserve',
                        title=title,
                        release_type='press_release',
                        date=release_date,
                        url=link,
                        description=title,
                        keywords_found=keywords,
                        is_critical='emergency' in title.lower() or 'intervention' in title.lower(),
                    )
                    releases.append(release)

        except Exception as e:
            logger.error(f"Error parsing Fed releases: {e}")

        self.cache[cache_key] = releases
        self.last_fetch[cache_key] = datetime.now()

        return releases

    def get_fdic_bank_failures(self) -> List[RegulatoryRelease]:
        """Get FDIC bank failure announcements"""
        url = f"{self.sources['fdic']['base_url']}{self.sources['fdic']['failures']}"
        html = self._fetch_page(url)

        if not html:
            return []

        releases = []
        try:
            soup = BeautifulSoup(html, 'html.parser')

            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    bank_name = cells[0].get_text(strip=True)
                    date_text = cells[2].get_text(strip=True)

                    try:
                        failure_date = datetime.strptime(date_text, '%B %d, %Y')
                    except ValueError:
                        failure_date = datetime.now()

                    release = RegulatoryRelease(
                        source='FDIC',
                        title=f"Bank Failure: {bank_name}",
                        release_type='bank_failure',
                        date=failure_date,
                        url=url,
                        description=f"{bank_name} failed on {date_text}",
                        keywords_found=['bank failure'],
                        is_critical=True,
                    )
                    releases.append(release)

        except Exception as e:
            logger.error(f"Error parsing FDIC failures: {e}")

        return releases

    def get_cot_report(self, metal: str = 'silver') -> Optional[COTReport]:
        """Get latest COT (Commitment of Traders) report"""
        cache_key = f'cot_{metal}'

        if cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        # CFTC COT data URL
        url = self.sources['cftc']['cot_url']
        html = self._fetch_page(url)

        if not html:
            return self.cache.get(cache_key)

        try:
            # Parse COT data (simplified - actual format is complex)
            # In production, use CFTC CSV/Excel downloads
            soup = BeautifulSoup(html, 'html.parser')

            # Find silver futures data (contract code 084691)
            # This is a simplified placeholder
            cot = COTReport(
                report_date=datetime.now(),
                metal=metal,
                commercial_long=80000,
                commercial_short=120000,
                commercial_net=-40000,
                non_commercial_long=100000,
                non_commercial_short=60000,
                non_commercial_net=40000,
                total_open_interest=180000,
            )

            self.cache[cache_key] = cot
            self.last_fetch[cache_key] = datetime.now()
            self.cot_history.append(cot)

            return cot

        except Exception as e:
            logger.error(f"Error parsing COT report: {e}")
            return None

    def get_all_releases(self, days: int = 7) -> List[RegulatoryRelease]:
        """Get releases from all regulatory sources"""
        all_releases = []

        all_releases.extend(self.get_cftc_releases(days))
        all_releases.extend(self.get_fed_releases(days))
        all_releases.extend(self.get_fdic_bank_failures())

        # Sort by date (newest first)
        all_releases.sort(key=lambda x: x.date, reverse=True)

        return all_releases

    def get_critical_releases(self, days: int = 7) -> List[RegulatoryRelease]:
        """Get only critical regulatory releases"""
        all_releases = self.get_all_releases(days)
        return [r for r in all_releases if r.is_critical]

    def check_alerts(self, alert_manager) -> List:
        """Check regulatory releases for alerts"""
        alerts = []
        critical = self.get_critical_releases(days=1)

        for release in critical:
            from data.alerts import Alert, AlertSeverity, AlertType

            if release.release_type == 'enforcement':
                alert_type = AlertType.ENFORCEMENT
                severity = AlertSeverity.CRITICAL
            elif release.release_type == 'bank_failure':
                alert_type = AlertType.BANK_STOCK_DROP
                severity = AlertSeverity.CRITICAL
            else:
                alert_type = AlertType.NEWS_CRITICAL
                severity = AlertSeverity.HIGH

            alert = Alert(
                severity=severity,
                alert_type=alert_type,
                title=release.title[:100],
                description=release.description,
                source=release.source,
                source_url=release.url,
                data=release.to_dict(),
            )
            if alert_manager.add_alert(alert):
                alerts.append(alert)

        return alerts

    def get_summary(self) -> Dict:
        """Get regulatory monitoring summary"""
        all_releases = self.get_all_releases(days=7)
        critical = [r for r in all_releases if r.is_critical]
        cot = self.get_cot_report('silver')

        return {
            'total_releases_7d': len(all_releases),
            'critical_releases': len(critical),
            'recent_critical': [r.to_dict() for r in critical[:5]],
            'cot_silver': cot.to_dict() if cot else None,
            'sources_monitored': len(self.sources),
            'last_updated': datetime.now().isoformat(),
        }

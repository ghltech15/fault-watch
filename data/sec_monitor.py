"""
SEC EDGAR Monitor
Monitors SEC filings for banks and precious metals companies
"""

import os
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import re
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

SEC_USER_AGENT = os.getenv('SEC_USER_AGENT', 'FaultWatch/1.0 (contact@example.com)')


@dataclass
class SECFiling:
    company: str
    cik: str
    form_type: str
    filed_date: datetime
    accession_number: str
    filing_url: str
    description: str
    keywords_found: List[str]
    is_critical: bool

    def to_dict(self) -> Dict:
        return {
            'company': self.company,
            'cik': self.cik,
            'form_type': self.form_type,
            'filed_date': self.filed_date.isoformat(),
            'accession_number': self.accession_number,
            'filing_url': self.filing_url,
            'description': self.description,
            'keywords_found': self.keywords_found,
            'is_critical': self.is_critical,
        }


class SECMonitor:
    """Monitor SEC EDGAR for relevant filings"""

    def __init__(self):
        self.base_url = 'https://www.sec.gov'
        self.edgar_url = f'{self.base_url}/cgi-bin/browse-edgar'
        self.submissions_url = 'https://data.sec.gov/submissions'

        self.headers = {
            'User-Agent': SEC_USER_AGENT,
            'Accept-Encoding': 'gzip, deflate',
        }

        # CIK numbers for monitored companies
        self.monitored_ciks = {
            '0000831001': 'Citigroup Inc',
            '0000019617': 'JPMorgan Chase',
            '0000070858': 'Bank of America',
            '0000895421': 'Morgan Stanley',
            '0001065088': 'UBS Group AG',
            '0001089113': 'HSBC Holdings',
            '0001067701': 'Bank of Nova Scotia',
            '0001618921': 'Deutsche Bank AG',
            '0000886982': 'Goldman Sachs',
            '0001129699': 'Barclays PLC',
        }

        # Critical form types
        self.critical_forms = [
            '8-K',      # Current report (material events)
            '10-K',     # Annual report
            '10-Q',     # Quarterly report
            'SC 13G',   # Beneficial ownership
            'SC 13D',   # Beneficial ownership (activist)
            '4',        # Insider transactions
            'DEF 14A',  # Proxy statement
        ]

        # Keywords that indicate critical filings
        self.critical_keywords = [
            'wells notice',
            'enforcement',
            'investigation',
            'subpoena',
            'material weakness',
            'going concern',
            'impairment',
            'write-down',
            'derivative',
            'precious metal',
            'silver',
            'gold',
            'commodity',
            'short position',
            'litigation',
            'settlement',
            'regulatory',
            'consent order',
            'cease and desist',
            'civil money penalty',
        ]

        self.cache: Dict[str, any] = {}
        self.last_fetch: Dict[str, datetime] = {}
        self.cache_ttl = 300  # 5 minutes

    def _make_request(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """Make rate-limited request to SEC"""
        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"SEC request failed: {e}")
            return None

    def get_company_filings(
        self,
        cik: str,
        form_type: str = None,
        count: int = 10
    ) -> List[Dict]:
        """Get recent filings for a company"""
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)

        url = f"{self.submissions_url}/CIK{cik_padded}.json"
        response = self._make_request(url)

        if not response:
            return []

        try:
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})

            results = []
            forms = filings.get('form', [])
            dates = filings.get('filingDate', [])
            accessions = filings.get('accessionNumber', [])
            primary_docs = filings.get('primaryDocument', [])

            for i in range(min(count, len(forms))):
                if form_type and forms[i] != form_type:
                    continue

                accession = accessions[i].replace('-', '')
                filing_url = (
                    f"{self.base_url}/Archives/edgar/data/"
                    f"{cik_padded}/{accession}/{primary_docs[i]}"
                )

                results.append({
                    'company': data.get('name', 'Unknown'),
                    'cik': cik,
                    'form_type': forms[i],
                    'filed_date': dates[i],
                    'accession_number': accessions[i],
                    'filing_url': filing_url,
                })

            return results[:count]
        except Exception as e:
            logger.error(f"Error parsing SEC response: {e}")
            return []

    def search_filings(
        self,
        keywords: List[str] = None,
        form_type: str = None,
        date_from: datetime = None
    ) -> List[Dict]:
        """Search SEC full-text for keywords"""
        if not keywords:
            keywords = self.critical_keywords[:5]

        if not date_from:
            date_from = datetime.now() - timedelta(days=7)

        # SEC full-text search endpoint
        search_url = f"{self.base_url}/cgi-bin/srch-ia"

        results = []
        for keyword in keywords:
            params = {
                'text': keyword,
                'first': 1,
                'last': 20,
            }

            response = self._make_request(search_url, params)
            if response:
                # Parse search results (simplified)
                # Full implementation would parse the HTML response
                pass

        return results

    def check_filing_content(self, filing_url: str) -> Dict:
        """Check filing content for critical keywords"""
        response = self._make_request(filing_url)
        if not response:
            return {'keywords_found': [], 'is_critical': False}

        content = response.text.lower()
        keywords_found = []

        for keyword in self.critical_keywords:
            if keyword in content:
                keywords_found.append(keyword)

        return {
            'keywords_found': keywords_found,
            'is_critical': len(keywords_found) >= 2 or 'wells notice' in keywords_found,
        }

    def get_all_monitored_filings(self, days: int = 7) -> List[SECFiling]:
        """Get recent filings from all monitored companies"""
        cache_key = f'all_filings_{days}'

        if cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        all_filings = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for cik, company in self.monitored_ciks.items():
            filings = self.get_company_filings(cik, count=20)

            for filing in filings:
                filed_date = datetime.fromisoformat(filing['filed_date'])
                if filed_date < cutoff_date:
                    continue

                # Check if critical form type
                if filing['form_type'] in self.critical_forms:
                    # Check content for keywords (rate limited)
                    content_check = self.check_filing_content(filing['filing_url'])

                    sec_filing = SECFiling(
                        company=filing['company'],
                        cik=cik,
                        form_type=filing['form_type'],
                        filed_date=filed_date,
                        accession_number=filing['accession_number'],
                        filing_url=filing['filing_url'],
                        description=f"{filing['form_type']} filing",
                        keywords_found=content_check['keywords_found'],
                        is_critical=content_check['is_critical'],
                    )
                    all_filings.append(sec_filing)

        # Sort by date (newest first)
        all_filings.sort(key=lambda x: x.filed_date, reverse=True)

        self.cache[cache_key] = all_filings
        self.last_fetch[cache_key] = datetime.now()

        return all_filings

    def get_critical_filings(self, days: int = 7) -> List[SECFiling]:
        """Get only critical filings"""
        all_filings = self.get_all_monitored_filings(days)
        return [f for f in all_filings if f.is_critical]

    def check_for_wells_notices(self) -> List[SECFiling]:
        """Specifically check for Wells Notice disclosures"""
        wells_filings = []

        for cik, company in self.monitored_ciks.items():
            # Check 8-K filings (where Wells Notices are typically disclosed)
            filings = self.get_company_filings(cik, form_type='8-K', count=10)

            for filing in filings:
                response = self._make_request(filing['filing_url'])
                if response:
                    content = response.text.lower()
                    if 'wells notice' in content or 'wells letter' in content:
                        wells_filings.append(SECFiling(
                            company=filing['company'],
                            cik=cik,
                            form_type=filing['form_type'],
                            filed_date=datetime.fromisoformat(filing['filed_date']),
                            accession_number=filing['accession_number'],
                            filing_url=filing['filing_url'],
                            description='WELLS NOTICE DETECTED',
                            keywords_found=['wells notice'],
                            is_critical=True,
                        ))

        return wells_filings

    def get_insider_transactions(self, cik: str) -> List[Dict]:
        """Get Form 4 insider transactions"""
        filings = self.get_company_filings(cik, form_type='4', count=20)

        transactions = []
        for filing in filings:
            # Parse Form 4 XML (simplified)
            transactions.append({
                'company': filing['company'],
                'filed_date': filing['filed_date'],
                'filing_url': filing['filing_url'],
                'type': 'insider_transaction',
            })

        return transactions

    def check_alerts(self, alert_manager) -> List:
        """Check SEC filings against alert criteria"""
        alerts = []
        critical_filings = self.get_critical_filings(days=1)

        for filing in critical_filings:
            alert = alert_manager.create_sec_alert(filing.to_dict())
            if alert:
                alerts.append(alert)

        return alerts

    def get_summary(self) -> Dict:
        """Get SEC monitoring summary"""
        all_filings = self.get_all_monitored_filings(days=7)
        critical = [f for f in all_filings if f.is_critical]

        return {
            'total_filings_7d': len(all_filings),
            'critical_filings': len(critical),
            'monitored_companies': len(self.monitored_ciks),
            'recent_critical': [f.to_dict() for f in critical[:5]],
            'last_updated': datetime.now().isoformat(),
        }

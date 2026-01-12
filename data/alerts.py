"""
Alert System
Generates and manages alerts from all data sources
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json


class AlertSeverity(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5


class AlertType(Enum):
    SEC_FILING = 'sec_filing'
    WELLS_NOTICE = 'wells_notice'
    ENFORCEMENT = 'enforcement'
    PRICE_SPIKE = 'price_spike'
    PRICE_CRASH = 'price_crash'
    BANK_STOCK_DROP = 'bank_stock_drop'
    FED_REPO_SPIKE = 'fed_repo_spike'
    INVENTORY_DROP = 'inventory_drop'
    DELIVERY_FAILURE = 'delivery_failure'
    NEWS_CRITICAL = 'news_critical'
    SOCIAL_VIRAL = 'social_viral'
    INSIDER_SELLING = 'insider_selling'
    TRADING_HALT = 'trading_halt'
    NATIONALIZATION = 'nationalization'
    DEADLINE_WARNING = 'deadline_warning'
    PREMIUM_SPIKE = 'premium_spike'
    CREDIT_STRESS = 'credit_stress'


class Alert:
    def __init__(
        self,
        severity: AlertSeverity,
        alert_type: AlertType,
        title: str,
        description: str,
        source: str,
        source_url: Optional[str] = None,
        related_entity: Optional[str] = None,
        data: Optional[Dict] = None,
    ):
        self.id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{alert_type.value}"
        self.severity = severity
        self.alert_type = alert_type
        self.title = title
        self.description = description
        self.source = source
        self.source_url = source_url
        self.related_entity = related_entity
        self.data = data or {}
        self.timestamp = datetime.now()
        self.acknowledged = False
        self.notified = False

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'severity': self.severity.name,
            'severity_level': self.severity.value,
            'type': self.alert_type.value,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'source_url': self.source_url,
            'related_entity': self.related_entity,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'acknowledged': self.acknowledged,
            'notified': self.notified,
        }

    def __repr__(self):
        return f"Alert({self.severity.name}: {self.title})"


class AlertManager:
    """Manages alert generation and storage"""

    def __init__(self, max_alerts: int = 500):
        self.alerts: List[Alert] = []
        self.max_alerts = max_alerts
        self.thresholds = {
            'silver_price_spike_pct': 5,
            'silver_price_crash_pct': -5,
            'bank_stock_drop_pct': -7,
            'bank_stock_warning_pct': -3,
            'fed_repo_spike_billion': 20,
            'comex_inventory_drop_pct': -10,
            'premium_spike_pct': 15,
        }

    def add_alert(self, alert: Alert) -> bool:
        """Add new alert, returns True if added (not duplicate)"""
        # Check for duplicates (same type and entity within last hour)
        one_hour_ago = datetime.now().timestamp() - 3600
        for existing in self.alerts:
            if (existing.alert_type == alert.alert_type and
                existing.related_entity == alert.related_entity and
                existing.timestamp.timestamp() > one_hour_ago):
                return False  # Duplicate

        self.alerts.append(alert)

        # Sort by severity and timestamp
        self.alerts.sort(
            key=lambda x: (x.severity.value, -x.timestamp.timestamp())
        )

        # Trim old alerts if over limit
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[:self.max_alerts]

        return True

    def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None,
        unacknowledged_only: bool = False,
        limit: int = 50,
        hours: int = 24,
    ) -> List[Dict]:
        """Get alerts with optional filters"""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        filtered = [a for a in self.alerts if a.timestamp.timestamp() > cutoff]

        if severity:
            filtered = [a for a in filtered if a.severity == severity]

        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]

        if unacknowledged_only:
            filtered = [a for a in filtered if not a.acknowledged]

        return [a.to_dict() for a in filtered[:limit]]

    def get_critical_alerts(self, limit: int = 10) -> List[Dict]:
        """Get only critical and high severity alerts"""
        return self.get_alerts(limit=limit, hours=24)

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark alert as acknowledged"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def mark_notified(self, alert_id: str) -> bool:
        """Mark alert as notified"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.notified = True
                return True
        return False

    def check_price_alerts(
        self,
        current_price: float,
        previous_price: float,
        asset: str = 'silver'
    ) -> Optional[Alert]:
        """Check for price-based alerts"""
        if previous_price == 0:
            return None

        pct_change = ((current_price - previous_price) / previous_price) * 100

        if pct_change >= self.thresholds['silver_price_spike_pct']:
            alert = Alert(
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.PRICE_SPIKE,
                title=f"{asset.upper()} PRICE SPIKE: +{pct_change:.1f}%",
                description=f"{asset} jumped from ${previous_price:.2f} to ${current_price:.2f}",
                source='Price Monitor',
                related_entity=asset,
                data={
                    'current': current_price,
                    'previous': previous_price,
                    'change_pct': pct_change
                },
            )
            if self.add_alert(alert):
                return alert

        elif pct_change <= self.thresholds['silver_price_crash_pct']:
            alert = Alert(
                severity=AlertSeverity.MEDIUM,
                alert_type=AlertType.PRICE_CRASH,
                title=f"{asset.upper()} PRICE DROP: {pct_change:.1f}%",
                description=f"{asset} dropped from ${previous_price:.2f} to ${current_price:.2f}",
                source='Price Monitor',
                related_entity=asset,
                data={
                    'current': current_price,
                    'previous': previous_price,
                    'change_pct': pct_change
                },
            )
            if self.add_alert(alert):
                return alert

        return None

    def check_bank_stock_alerts(
        self,
        ticker: str,
        bank_name: str,
        current_price: float,
        previous_price: float
    ) -> Optional[Alert]:
        """Check for bank stock alerts"""
        if previous_price == 0:
            return None

        pct_change = ((current_price - previous_price) / previous_price) * 100

        if pct_change <= self.thresholds['bank_stock_drop_pct']:
            alert = Alert(
                severity=AlertSeverity.CRITICAL,
                alert_type=AlertType.BANK_STOCK_DROP,
                title=f"{ticker} STOCK CRASHING: {pct_change:.1f}%",
                description=f"{bank_name} dropped from ${previous_price:.2f} to ${current_price:.2f}",
                source='Stock Monitor',
                related_entity=ticker,
                data={
                    'current': current_price,
                    'previous': previous_price,
                    'change_pct': pct_change
                },
            )
            if self.add_alert(alert):
                return alert

        elif pct_change <= self.thresholds['bank_stock_warning_pct']:
            alert = Alert(
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.BANK_STOCK_DROP,
                title=f"{ticker} UNDER PRESSURE: {pct_change:.1f}%",
                description=f"{bank_name} down {abs(pct_change):.1f}% today",
                source='Stock Monitor',
                related_entity=ticker,
                data={
                    'current': current_price,
                    'previous': previous_price,
                    'change_pct': pct_change
                },
            )
            if self.add_alert(alert):
                return alert

        return None

    def check_fed_repo_alerts(self, repo_amount_billion: float) -> Optional[Alert]:
        """Check for Fed repo alerts"""
        if repo_amount_billion >= self.thresholds['fed_repo_spike_billion']:
            severity = (AlertSeverity.CRITICAL if repo_amount_billion >= 50
                       else AlertSeverity.HIGH)
            alert = Alert(
                severity=severity,
                alert_type=AlertType.FED_REPO_SPIKE,
                title=f"FED REPO SPIKE: ${repo_amount_billion:.1f}B",
                description=f"Federal Reserve repo operations at ${repo_amount_billion:.1f} billion",
                source='Fed Monitor',
                data={'amount_billion': repo_amount_billion},
            )
            if self.add_alert(alert):
                return alert
        return None

    def check_comex_alerts(
        self,
        registered_oz: float,
        previous_registered_oz: float,
        coverage_ratio: float
    ) -> Optional[Alert]:
        """Check for COMEX inventory alerts"""
        if previous_registered_oz > 0:
            pct_change = ((registered_oz - previous_registered_oz) /
                         previous_registered_oz) * 100

            if pct_change <= self.thresholds['comex_inventory_drop_pct']:
                alert = Alert(
                    severity=AlertSeverity.HIGH,
                    alert_type=AlertType.INVENTORY_DROP,
                    title=f"COMEX DRAIN: {pct_change:.1f}%",
                    description=f"COMEX registered silver dropped {abs(pct_change):.1f}%",
                    source='COMEX Monitor',
                    data={
                        'current_oz': registered_oz,
                        'previous_oz': previous_registered_oz,
                        'change_pct': pct_change
                    },
                )
                if self.add_alert(alert):
                    return alert

        if coverage_ratio >= 3:
            alert = Alert(
                severity=AlertSeverity.CRITICAL,
                alert_type=AlertType.DELIVERY_FAILURE,
                title=f"COMEX COVERAGE CRITICAL: {coverage_ratio:.1f}x",
                description=f"Paper claims are {coverage_ratio:.1f}x physical inventory",
                source='COMEX Monitor',
                data={'coverage_ratio': coverage_ratio},
            )
            if self.add_alert(alert):
                return alert

        return None

    def create_sec_alert(self, filing_data: Dict) -> Optional[Alert]:
        """Create alert from SEC filing"""
        keywords = filing_data.get('keywords_found', [])
        is_wells = 'wells' in str(keywords).lower()

        alert = Alert(
            severity=AlertSeverity.CRITICAL if is_wells else AlertSeverity.HIGH,
            alert_type=AlertType.WELLS_NOTICE if is_wells else AlertType.SEC_FILING,
            title=f"SEC FILING: {filing_data.get('bank', 'Unknown')}",
            description=f"Keywords: {', '.join(keywords[:5])}",
            source='SEC EDGAR',
            source_url=filing_data.get('filing_url'),
            related_entity=filing_data.get('bank'),
            data=filing_data,
        )
        if self.add_alert(alert):
            return alert
        return None

    def create_news_alert(
        self,
        title: str,
        description: str,
        source: str,
        url: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        related_entity: Optional[str] = None
    ) -> Optional[Alert]:
        """Create alert from news article"""
        alert = Alert(
            severity=severity,
            alert_type=AlertType.NEWS_CRITICAL,
            title=title,
            description=description,
            source=source,
            source_url=url,
            related_entity=related_entity,
        )
        if self.add_alert(alert):
            return alert
        return None

    def create_social_alert(
        self,
        title: str,
        description: str,
        platform: str,
        url: str,
        engagement: int
    ) -> Optional[Alert]:
        """Create alert from viral social post"""
        alert = Alert(
            severity=AlertSeverity.LOW,
            alert_type=AlertType.SOCIAL_VIRAL,
            title=title,
            description=description,
            source=f'Social: {platform}',
            source_url=url,
            data={'engagement': engagement},
        )
        if self.add_alert(alert):
            return alert
        return None

    def get_summary(self) -> Dict:
        """Get alert summary statistics"""
        now = datetime.now()
        last_24h = [a for a in self.alerts
                   if (now - a.timestamp).total_seconds() < 86400]

        return {
            'total_alerts': len(self.alerts),
            'last_24h': len(last_24h),
            'critical': len([a for a in last_24h
                           if a.severity == AlertSeverity.CRITICAL]),
            'high': len([a for a in last_24h
                        if a.severity == AlertSeverity.HIGH]),
            'unacknowledged': len([a for a in last_24h if not a.acknowledged]),
            'by_type': {
                t.value: len([a for a in last_24h if a.alert_type == t])
                for t in AlertType
            },
        }

    def export_alerts(self, filepath: str):
        """Export alerts to JSON file"""
        with open(filepath, 'w') as f:
            json.dump([a.to_dict() for a in self.alerts], f, indent=2)

    def clear_old_alerts(self, hours: int = 48):
        """Clear alerts older than specified hours"""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        self.alerts = [a for a in self.alerts
                      if a.timestamp.timestamp() > cutoff]

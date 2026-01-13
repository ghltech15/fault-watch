"""
Tests for scoring engines.

Tests the three-score system:
- Funding Stress (0-100)
- Enforcement Heat (0-100)
- Deliverability Stress (0-100)
- Composite Risk (0-10)
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4


class TestFundingStress:
    """Tests for funding stress scoring"""

    def test_funding_stress_import(self):
        """Verify funding stress module imports"""
        from packages.core.scoring.funding import (
            calculate_funding_stress,
            FundingScore,
            FundingIndicators,
        )
        assert calculate_funding_stress is not None

    def test_funding_stress_zero_inputs(self):
        """Zero inputs should give low score"""
        from packages.core.scoring.funding import (
            calculate_funding_stress,
            FundingIndicators,
        )

        indicators = FundingIndicators()
        result = calculate_funding_stress(indicators)

        assert result.score >= 0
        assert result.score <= 100

    def test_funding_stress_high_spreads(self):
        """High credit spreads should increase score"""
        from packages.core.scoring.funding import (
            calculate_funding_stress,
            FundingIndicators,
        )

        indicators = FundingIndicators(
            hy_spread=800,  # Very high HY spread
            ig_spread=200,
            ted_spread=1.5,
        )
        result = calculate_funding_stress(indicators)

        assert result.score >= 40, f"High spreads should give score >= 40, got {result.score}"
        assert len(result.drivers) > 0, "Should have driver explanations"

    def test_funding_stress_levels(self):
        """Test stress level categorization"""
        from packages.core.scoring.funding import get_funding_level

        assert get_funding_level(90) == "CRISIS"
        assert get_funding_level(70) == "SEVERE"
        assert get_funding_level(50) == "ELEVATED"
        assert get_funding_level(30) == "MODERATE"
        assert get_funding_level(10) == "NORMAL"


class TestEnforcementHeat:
    """Tests for enforcement heat scoring"""

    def test_enforcement_heat_import(self):
        """Verify enforcement heat module imports"""
        from packages.core.scoring.enforcement import (
            calculate_enforcement_heat,
            EnforcementScore,
        )
        assert calculate_enforcement_heat is not None

    def test_enforcement_heat_no_events(self):
        """No events should give zero score"""
        from packages.core.scoring.enforcement import calculate_enforcement_heat

        result = calculate_enforcement_heat(entity_id=None, events=[])

        assert result.score == 0
        assert result.drivers == []

    def test_enforcement_heat_with_events(self):
        """Events should increase score"""
        from packages.core.scoring.enforcement import (
            calculate_enforcement_heat,
            EnforcementEvent,
        )

        # Use same entity_id for event and calculation
        entity_id = uuid4()

        events = [
            EnforcementEvent(
                event_type='wells_notice',
                source_name='SEC',
                observed_at=datetime.utcnow() - timedelta(days=5),
                payload={'entity': 'Test Bank', 'action_type': 'wells_notice'},
                entity_id=entity_id,
            ),
        ]

        result = calculate_enforcement_heat(entity_id=entity_id, events=events)

        assert result.score > 0, "Events should increase score"
        assert result.actions_30d == 1


class TestDeliverabilityStress:
    """Tests for deliverability stress scoring"""

    def test_deliverability_stress_import(self):
        """Verify deliverability stress module imports"""
        from packages.core.scoring.deliverability import (
            calculate_deliverability_stress,
            DeliverabilityScore,
            DeliverabilityIndicators,
            ComexIndicators,
            DealerIndicators,
        )
        assert calculate_deliverability_stress is not None

    def test_deliverability_stress_normal(self):
        """Normal conditions should give low score"""
        from packages.core.scoring.deliverability import (
            calculate_deliverability_stress,
            DeliverabilityIndicators,
            ComexIndicators,
            DealerIndicators,
        )

        indicators = DeliverabilityIndicators(
            comex=ComexIndicators(
                coverage_ratio=1.5,  # Normal
                days_of_supply=50,   # Plenty
            ),
            dealers=DealerIndicators(
                avg_premium_pct=5,   # Normal
                out_of_stock_rate=5, # Low
            ),
        )
        result = calculate_deliverability_stress(indicators)

        assert result.score < 30, f"Normal conditions should give score < 30, got {result.score}"

    def test_deliverability_stress_critical(self):
        """Critical conditions should give high score"""
        from packages.core.scoring.deliverability import (
            calculate_deliverability_stress,
            DeliverabilityIndicators,
            ComexIndicators,
            DealerIndicators,
        )

        indicators = DeliverabilityIndicators(
            comex=ComexIndicators(
                coverage_ratio=10,    # Extreme
                days_of_supply=5,     # Critical
                delivery_notices_acceleration=100,  # Surging
            ),
            dealers=DealerIndicators(
                avg_premium_pct=50,   # Extreme
                out_of_stock_rate=70, # Severe shortage
            ),
        )
        result = calculate_deliverability_stress(indicators)

        assert result.score >= 70, f"Critical conditions should give score >= 70, got {result.score}"
        assert len(result.drivers) >= 3, "Should have multiple driver explanations"

    def test_price_multiplier(self):
        """Price should amplify, not drive, the score"""
        from packages.core.scoring.deliverability import (
            calculate_deliverability_stress,
            DeliverabilityIndicators,
            ComexIndicators,
            DealerIndicators,
        )

        base_indicators = DeliverabilityIndicators(
            comex=ComexIndicators(coverage_ratio=5, days_of_supply=15),
            dealers=DealerIndicators(avg_premium_pct=20),
        )

        # Without price
        result_no_price = calculate_deliverability_stress(base_indicators)

        # With high price
        base_indicators.silver_price = 100
        result_with_price = calculate_deliverability_stress(base_indicators)

        assert result_with_price.score >= result_no_price.score
        assert result_with_price.price_multiplier >= 1.0


class TestCompositeRisk:
    """Tests for composite risk scoring"""

    def test_composite_risk_import(self):
        """Verify composite risk module imports"""
        from packages.core.scoring.composite import (
            calculate_composite_risk,
            CompositeRisk,
            get_risk_level,
            get_risk_color,
        )
        assert calculate_composite_risk is not None

    def test_composite_risk_calculation(self):
        """Test basic composite calculation"""
        from packages.core.scoring.composite import quick_composite_assessment

        result = quick_composite_assessment(
            funding_score=50,
            enforcement_score=30,
            deliverability_score=40,
        )

        assert result.score >= 0
        assert result.score <= 10
        assert result.funding_component == 5.0  # 50/10
        assert result.enforcement_component == 3.0  # 30/10
        assert result.deliverability_component == 4.0  # 40/10

    def test_cascade_trigger_level_1(self):
        """Test level 1 cascade (2+ high)"""
        from packages.core.scoring.composite import quick_composite_assessment

        # Two scores >= 50 should trigger level 1 cascade
        result = quick_composite_assessment(
            funding_score=60,
            enforcement_score=55,
            deliverability_score=20,
        )

        assert result.cascade_triggered
        assert result.cascade_level == 1

    def test_cascade_trigger_level_2(self):
        """Test level 2 cascade (1 extreme + 2 high)"""
        from packages.core.scoring.composite import quick_composite_assessment

        # One score >= 70 and two >= 50 should trigger level 2
        result = quick_composite_assessment(
            funding_score=80,
            enforcement_score=60,
            deliverability_score=55,
        )

        assert result.cascade_triggered
        assert result.cascade_level == 2

    def test_risk_levels(self):
        """Test risk level labels"""
        from packages.core.scoring.composite import get_risk_level

        assert get_risk_level(0.5) == "STABLE"
        assert get_risk_level(2.0) == "MONITOR"
        assert get_risk_level(3.0) == "WATCH"
        assert get_risk_level(5.0) == "WARNING"
        assert get_risk_level(7.0) == "DANGER"
        assert get_risk_level(9.0) == "CRISIS"

    def test_risk_colors(self):
        """Test risk color coding"""
        from packages.core.scoring.composite import get_risk_color

        assert get_risk_color(0.5) == "green"
        assert get_risk_color(9.0) == "darkred"


class TestScoringIntegration:
    """Integration tests for full scoring pipeline"""

    def test_full_scoring_pipeline(self):
        """Test complete scoring flow from indicators to composite"""
        from packages.core.scoring.funding import FundingIndicators, calculate_funding_stress
        from packages.core.scoring.enforcement import calculate_enforcement_heat
        from packages.core.scoring.deliverability import (
            DeliverabilityIndicators,
            ComexIndicators,
            DealerIndicators,
            calculate_deliverability_stress,
        )
        from packages.core.scoring.composite import calculate_composite_risk

        # Calculate all three scores
        funding = calculate_funding_stress(FundingIndicators(hy_spread=500, ted_spread=0.5))
        enforcement = calculate_enforcement_heat(entity_id=None, events=[])
        deliverability = calculate_deliverability_stress(
            DeliverabilityIndicators(
                comex=ComexIndicators(coverage_ratio=3, days_of_supply=20),
                dealers=DealerIndicators(avg_premium_pct=15),
            )
        )

        # Calculate composite
        composite = calculate_composite_risk(funding, enforcement, deliverability)

        assert composite.score >= 0
        assert composite.score <= 10
        assert 'funding_drivers' in composite.explain
        assert 'enforcement_drivers' in composite.explain
        assert 'deliverability_drivers' in composite.explain


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

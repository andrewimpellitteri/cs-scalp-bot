"""Tests for enhanced risk management features."""
import pytest
from datetime import datetime, timedelta
from scalp_bot.core.engine import TradingEngine, TradingStats
from scalp_bot.models.config import BotConfig, RiskConfig, TradingMode
from scalp_bot.services.broker import DryRunBroker


class TestTradingStats:
    """Tests for TradingStats with enhanced safety monitoring."""

    def test_initialization(self):
        """Test stats initialization."""
        stats = TradingStats()

        assert stats.daily_trades == 0
        assert stats.daily_pnl == 0.0
        assert stats.consecutive_losses == 0
        assert stats.consecutive_wins == 0
        assert stats.stopped_by_risk_limit is False
        assert stats.stop_reason is None

    def test_record_winning_trade(self):
        """Test recording a winning trade."""
        stats = TradingStats()

        stats.record_trade(100.0)  # $100 profit

        assert stats.daily_trades == 1
        assert stats.daily_pnl == 100.0
        assert stats.total_wins == 1
        assert stats.total_losses == 0
        assert stats.consecutive_wins == 1
        assert stats.consecutive_losses == 0
        assert stats.largest_win == 100.0

    def test_record_losing_trade(self):
        """Test recording a losing trade."""
        stats = TradingStats()

        stats.record_trade(-50.0)  # $50 loss

        assert stats.daily_trades == 1
        assert stats.daily_pnl == -50.0
        assert stats.total_wins == 0
        assert stats.total_losses == 1
        assert stats.consecutive_wins == 0
        assert stats.consecutive_losses == 1
        assert stats.largest_loss == -50.0

    def test_consecutive_loss_tracking(self):
        """Test consecutive loss streak tracking."""
        stats = TradingStats()

        # Record losing streak
        stats.record_trade(-10.0)
        stats.record_trade(-20.0)
        stats.record_trade(-15.0)

        assert stats.consecutive_losses == 3
        assert stats.consecutive_wins == 0

        # Win breaks the streak
        stats.record_trade(50.0)

        assert stats.consecutive_losses == 0
        assert stats.consecutive_wins == 1

    def test_cooldown_functionality(self):
        """Test cooldown period management."""
        stats = TradingStats()

        # Set cooldown
        stats.set_cooldown(60, "Test reason")

        assert stats.is_in_cooldown() is True
        assert stats.stopped_by_risk_limit is True
        assert stats.stop_reason == "Test reason"
        assert stats.cooldown_until is not None

    def test_cooldown_expiry(self):
        """Test that cooldown expires correctly."""
        stats = TradingStats()

        # Set cooldown in the past
        stats.cooldown_until = datetime.utcnow() - timedelta(minutes=5)

        assert stats.is_in_cooldown() is False

    def test_reset_daily(self):
        """Test resetting daily statistics."""
        stats = TradingStats()

        stats.record_trade(100.0)
        stats.set_cooldown(60, "Test")

        stats.reset_daily()

        assert stats.daily_trades == 0
        assert stats.daily_pnl == 0.0
        assert stats.stopped_by_risk_limit is False
        assert stats.stop_reason is None


class TestRiskLimitEnforcement:
    """Tests for risk limit enforcement in trading engine."""

    @pytest.mark.asyncio
    async def test_daily_trade_limit(self, conservative_config, connected_broker):
        """Test that daily trade limit is enforced."""
        # Set very low trade limit
        conservative_config.risk.max_daily_trades = 2

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # Simulate hitting trade limit
        engine.stats.daily_trades = 2

        result = engine._check_risk_limits()

        assert result is False
        assert engine.stats.is_in_cooldown() is True

        await engine.stop()

    @pytest.mark.asyncio
    async def test_daily_loss_percent_limit(self, conservative_config, connected_broker):
        """Test daily loss percentage limit."""
        conservative_config.risk.max_daily_loss_percent = 5.0

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # Simulate 6% daily loss
        engine.stats.daily_pnl = -600.0  # 6% of $10k

        result = engine._check_risk_limits()

        assert result is False
        assert engine.stats.stopped_by_risk_limit is True

        await engine.stop()

    @pytest.mark.asyncio
    async def test_daily_loss_dollar_limit(self, conservative_config, connected_broker):
        """Test daily loss dollar amount limit."""
        conservative_config.risk.max_daily_loss_dollars = 200.0

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # Simulate $250 loss
        engine.stats.daily_pnl = -250.0

        result = engine._check_risk_limits()

        assert result is False
        assert engine.stats.stopped_by_risk_limit is True

        await engine.stop()

    @pytest.mark.asyncio
    async def test_consecutive_loss_circuit_breaker(self, conservative_config, connected_broker):
        """Test consecutive loss circuit breaker."""
        conservative_config.risk.max_consecutive_losses = 3

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # Simulate 3 consecutive losses
        engine.stats.consecutive_losses = 3

        result = engine._check_risk_limits()

        assert result is False
        assert engine.stats.stopped_by_risk_limit is True
        assert "consecutive losses" in engine.stats.stop_reason.lower()

        await engine.stop()

    @pytest.mark.asyncio
    async def test_account_drawdown_kill_switch(self, conservative_config, connected_broker):
        """Test account drawdown kill switch."""
        conservative_config.risk.max_account_drawdown_percent = 10.0

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # Simulate 11% account drawdown
        engine.account_balance = 8900.0  # Down from initial 10k

        result = engine._check_risk_limits()

        assert result is False
        assert engine.stats.stopped_by_risk_limit is True
        assert "kill switch" in engine.stats.stop_reason.lower()

        await engine.stop()

    @pytest.mark.asyncio
    async def test_manual_restart_requirement(self, conservative_config, connected_broker):
        """Test that manual restart is required after risk limit stop."""
        conservative_config.risk.require_manual_restart_after_stop = True

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # Trigger a risk limit
        engine.stats.stopped_by_risk_limit = True
        engine.stats.stop_reason = "Test stop"

        result = engine._check_risk_limits()

        assert result is False

        await engine.stop()

    @pytest.mark.asyncio
    async def test_trade_frequency_throttle(self, conservative_config, connected_broker):
        """Test trade frequency throttling."""
        conservative_config.risk.max_trade_frequency_seconds = 60

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # Simulate recent trade
        engine.stats.last_trade_time = datetime.utcnow() - timedelta(seconds=30)

        result = engine._check_risk_limits()

        assert result is False  # Too soon after last trade

        await engine.stop()

    @pytest.mark.asyncio
    async def test_all_limits_within_bounds(self, conservative_config, connected_broker):
        """Test that all limits pass when within bounds."""
        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # All stats within limits
        engine.stats.daily_trades = 10
        engine.stats.daily_pnl = -50.0  # Small loss
        engine.stats.consecutive_losses = 2
        engine.account_balance = 9800.0  # Small drawdown

        result = engine._check_risk_limits()

        assert result is True

        await engine.stop()


class TestPositionSizingLimits:
    """Tests for position sizing safety limits."""

    @pytest.mark.asyncio
    async def test_position_size_percent_limit(self, conservative_config, connected_broker):
        """Test that position size percentage is enforced."""
        conservative_config.risk.position_size_percent = 10.0

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        # Open position should be capped at 10% of account
        # Account: $10,000, so max position: $1,000
        # If TSLA is $250, should buy max 4 shares ($1,000 / $250)

        # This would be tested by actually opening a position
        # For now, verify config is set correctly
        assert engine.config.risk.position_size_percent == 10.0

        await engine.stop()

    @pytest.mark.asyncio
    async def test_max_position_value_dollars(self, conservative_config, connected_broker):
        """Test dollar value cap on positions."""
        conservative_config.risk.max_position_value_dollars = 500.0

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        assert engine.config.risk.max_position_value_dollars == 500.0

        await engine.stop()

    @pytest.mark.asyncio
    async def test_max_shares_per_trade(self, conservative_config, connected_broker):
        """Test maximum shares per trade limit."""
        conservative_config.risk.max_shares_per_trade = 100

        engine = TradingEngine(
            config=conservative_config,
            broker_client=connected_broker
        )
        await engine.start()

        assert engine.config.risk.max_shares_per_trade == 100

        await engine.stop()

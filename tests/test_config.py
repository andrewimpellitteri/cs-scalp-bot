"""Tests for configuration models."""
import pytest
from scalp_bot.models.config import (
    BotConfig,
    StrategyConfig,
    RiskConfig,
    TradingMode,
)


class TestStrategyConfig:
    """Tests for StrategyConfig model."""

    def test_default_values(self):
        """Test default strategy configuration values."""
        config = StrategyConfig()

        assert config.entry_drop_percent == 0.5
        assert config.entry_timeframe_minutes == 5
        assert config.profit_target_percent == 0.3
        assert config.stop_loss_percent == 0.4
        assert config.use_trailing_stop is False
        assert config.avoid_first_minutes == 30
        assert config.avoid_last_minutes == 30
        assert config.close_positions_at_eod is True

    def test_custom_values(self):
        """Test custom strategy configuration."""
        config = StrategyConfig(
            entry_drop_percent=1.0,
            profit_target_percent=0.5,
            stop_loss_percent=0.6,
            use_trailing_stop=True,
        )

        assert config.entry_drop_percent == 1.0
        assert config.profit_target_percent == 0.5
        assert config.stop_loss_percent == 0.6
        assert config.use_trailing_stop is True

    def test_validation_constraints(self):
        """Test that validation constraints are enforced."""
        # Should not allow negative percentages
        with pytest.raises(Exception):
            StrategyConfig(entry_drop_percent=-1.0)

        # Should not allow values too high
        with pytest.raises(Exception):
            StrategyConfig(entry_drop_percent=11.0)  # Max is 10.0


class TestRiskConfig:
    """Tests for RiskConfig model."""

    def test_default_values(self):
        """Test default risk configuration values."""
        config = RiskConfig()

        assert config.position_size_percent == 10.0
        assert config.max_positions == 1
        assert config.max_daily_loss_percent == 5.0
        assert config.max_daily_trades == 100
        assert config.max_trade_frequency_seconds == 30
        assert config.max_consecutive_losses == 5
        assert config.max_account_drawdown_percent == 10.0
        assert config.require_manual_restart_after_stop is True

    def test_conservative_settings(self):
        """Test conservative risk settings."""
        config = RiskConfig(
            position_size_percent=5.0,
            max_daily_loss_percent=3.0,
            max_daily_loss_dollars=150.0,
            max_consecutive_losses=3,
            max_account_drawdown_percent=5.0,
        )

        assert config.position_size_percent == 5.0
        assert config.max_daily_loss_percent == 3.0
        assert config.max_daily_loss_dollars == 150.0
        assert config.max_consecutive_losses == 3
        assert config.max_account_drawdown_percent == 5.0

    def test_position_limits(self):
        """Test position size and count limits."""
        config = RiskConfig(
            max_position_value_dollars=1000.0,
            max_shares_per_trade=100,
            max_positions=2,
        )

        assert config.max_position_value_dollars == 1000.0
        assert config.max_shares_per_trade == 100
        assert config.max_positions == 2

    def test_validation_hard_caps(self):
        """Test that hard caps are enforced."""
        # Position size cannot exceed 50%
        with pytest.raises(Exception):
            RiskConfig(position_size_percent=51.0)

        # Daily loss cannot exceed 20%
        with pytest.raises(Exception):
            RiskConfig(max_daily_loss_percent=21.0)

        # Drawdown cannot exceed 30%
        with pytest.raises(Exception):
            RiskConfig(max_account_drawdown_percent=31.0)

        # Max positions cannot exceed 5
        with pytest.raises(Exception):
            RiskConfig(max_positions=6)


class TestBotConfig:
    """Tests for BotConfig model."""

    def test_default_values(self):
        """Test default bot configuration."""
        config = BotConfig()

        assert config.trading_mode == TradingMode.DRY_RUN
        assert config.symbols == ["TSLA"]
        assert isinstance(config.strategy, StrategyConfig)
        assert isinstance(config.risk, RiskConfig)
        assert config.schwab_app_key is None
        assert config.schwab_app_secret is None

    def test_trading_mode_checks(self):
        """Test trading mode helper methods."""
        dry_run_config = BotConfig(trading_mode=TradingMode.DRY_RUN)
        assert dry_run_config.is_dry_run() is True
        assert dry_run_config.is_live() is False

        live_config = BotConfig(trading_mode=TradingMode.LIVE)
        assert live_config.is_dry_run() is False
        assert live_config.is_live() is True

    def test_symbols_uppercase_validation(self):
        """Test that symbols are converted to uppercase."""
        config = BotConfig(symbols=["tsla", "nvda"])
        assert config.symbols == ["TSLA", "NVDA"]

    def test_nested_configuration(self):
        """Test configuration with nested strategy and risk configs."""
        config = BotConfig(
            trading_mode=TradingMode.DRY_RUN,
            symbols=["TSLA", "NVDA"],
            strategy=StrategyConfig(
                entry_drop_percent=0.7,
                profit_target_percent=0.4,
            ),
            risk=RiskConfig(
                position_size_percent=5.0,
                max_daily_loss_percent=3.0,
            ),
        )

        assert config.trading_mode == TradingMode.DRY_RUN
        assert config.symbols == ["TSLA", "NVDA"]
        assert config.strategy.entry_drop_percent == 0.7
        assert config.risk.position_size_percent == 5.0

"""Configuration models for the scalping bot."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class TradingMode(str, Enum):
    """Trading mode enum."""
    DRY_RUN = "dry_run"
    LIVE = "live"
    BACKTEST = "backtest"


class StrategyConfig(BaseModel):
    """Strategy configuration for entry/exit signals."""

    # Entry settings
    entry_drop_percent: float = Field(
        default=0.5,
        description="Buy when price drops this % from recent high",
        ge=0.0,
        le=10.0
    )
    entry_timeframe_minutes: int = Field(
        default=5,
        description="Timeframe to measure price drop (minutes)",
        ge=1,
        le=60
    )

    # Exit settings - profit target
    profit_target_percent: float = Field(
        default=0.3,
        description="Sell when profit reaches this %",
        ge=0.0,
        le=10.0
    )

    # Exit settings - stop loss
    stop_loss_percent: float = Field(
        default=0.4,
        description="Sell when loss reaches this %",
        ge=0.0,
        le=10.0
    )

    # Trailing stop (optional)
    use_trailing_stop: bool = Field(
        default=False,
        description="Use trailing stop instead of fixed profit target"
    )
    trailing_stop_percent: float = Field(
        default=0.2,
        description="Trail by this % from peak",
        ge=0.0,
        le=10.0
    )

    # Time-based rules
    avoid_first_minutes: int = Field(
        default=30,
        description="Avoid trading first N minutes after market open",
        ge=0,
        le=60
    )
    avoid_last_minutes: int = Field(
        default=30,
        description="Avoid trading last N minutes before market close",
        ge=0,
        le=60
    )
    close_positions_at_eod: bool = Field(
        default=True,
        description="Close all positions before market close"
    )


class RiskConfig(BaseModel):
    """Risk management configuration with multiple safety layers."""

    # Position sizing
    position_size_percent: float = Field(
        default=10.0,
        description="Percentage of account balance to use per trade",
        ge=1.0,
        le=50.0  # Hard cap at 50% - never risk more than half on one trade
    )
    max_position_value_dollars: Optional[float] = Field(
        default=None,
        description="Maximum dollar value per position (overrides % if lower)",
        ge=100.0,
        le=100000.0
    )
    max_positions: int = Field(
        default=1,
        description="Maximum number of concurrent positions",
        ge=1,
        le=5  # Reduced from 10 - safer for scalping
    )

    # Daily limits
    max_daily_loss_percent: Optional[float] = Field(
        default=5.0,
        description="Stop trading if daily loss exceeds this %",
        ge=0.0,
        le=20.0  # Hard cap at 20% daily loss
    )
    max_daily_loss_dollars: Optional[float] = Field(
        default=None,
        description="Stop trading if daily loss exceeds this $ amount",
        ge=0.0,
        le=50000.0
    )
    max_daily_trades: Optional[int] = Field(
        default=100,
        description="Maximum trades per day",
        ge=1,
        le=500  # Increased for scalping but still reasonable
    )

    # Safety checks
    max_trade_frequency_seconds: int = Field(
        default=30,
        description="Minimum seconds between trades",
        ge=1,
        le=300
    )

    # Circuit breakers (CRITICAL SAFETY)
    max_consecutive_losses: int = Field(
        default=5,
        description="Stop trading after this many losses in a row",
        ge=1,
        le=20
    )
    max_account_drawdown_percent: float = Field(
        default=10.0,
        description="KILL SWITCH: Stop trading if account drops this % from starting balance",
        ge=1.0,
        le=30.0
    )

    # Order limits (prevent fat finger errors)
    max_shares_per_trade: Optional[int] = Field(
        default=None,
        description="Hard limit on number of shares per trade (safety check)",
        ge=1,
        le=10000
    )

    # Cool-down period after hitting limits
    cooldown_after_daily_loss_minutes: int = Field(
        default=60,
        description="Minutes to wait before allowing restart after hitting daily loss",
        ge=0,
        le=1440  # Max 24 hours
    )

    # Emergency stop flag
    require_manual_restart_after_stop: bool = Field(
        default=True,
        description="Require manual restart if bot stops due to risk limits"
    )


class BotConfig(BaseModel):
    """Main bot configuration."""

    # Trading settings
    trading_mode: TradingMode = Field(
        default=TradingMode.DRY_RUN,
        description="Trading mode: dry_run, live, or backtest"
    )

    symbols: List[str] = Field(
        default=["TSLA"],
        description="List of symbols to trade"
    )

    strategy: StrategyConfig = Field(
        default_factory=StrategyConfig,
        description="Strategy configuration"
    )

    risk: RiskConfig = Field(
        default_factory=RiskConfig,
        description="Risk management configuration"
    )

    # Schwab API settings
    schwab_app_key: Optional[str] = Field(
        default=None,
        description="Schwab API app key"
    )
    schwab_app_secret: Optional[str] = Field(
        default=None,
        description="Schwab API app secret"
    )
    schwab_token_path: str = Field(
        default="./data/tokens.json",
        description="Path to store Schwab API tokens"
    )

    # Database settings
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/trades.db",
        description="Database URL for trade history"
    )

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, v):
        """Ensure symbols are uppercase."""
        return [s.upper() for s in v]

    def is_dry_run(self) -> bool:
        """Check if bot is in dry run mode."""
        return self.trading_mode == TradingMode.DRY_RUN

    def is_live(self) -> bool:
        """Check if bot is in live mode."""
        return self.trading_mode == TradingMode.LIVE

    def is_backtest(self) -> bool:
        """Check if bot is in backtest mode."""
        return self.trading_mode == TradingMode.BACKTEST

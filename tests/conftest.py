"""Pytest configuration and fixtures."""
import pytest
from datetime import datetime
from scalp_bot.models.config import BotConfig, StrategyConfig, RiskConfig, TradingMode
from scalp_bot.models.trade import Trade, Position, TradeAction, TradeStatus
from scalp_bot.services.broker import DryRunBroker
from scalp_bot.core.engine import TradingEngine
from scalp_bot.core.strategy import ScalpingStrategy


@pytest.fixture
def default_config():
    """Default bot configuration for testing."""
    return BotConfig()


@pytest.fixture
def conservative_config():
    """Conservative configuration for testing risk limits."""
    return BotConfig(
        trading_mode=TradingMode.DRY_RUN,
        symbols=["TSLA"],
        strategy=StrategyConfig(
            entry_drop_percent=0.5,
            profit_target_percent=0.3,
            stop_loss_percent=0.4,
        ),
        risk=RiskConfig(
            position_size_percent=5.0,
            max_positions=1,
            max_daily_loss_percent=3.0,
            max_daily_loss_dollars=150.0,
            max_daily_trades=50,
            max_consecutive_losses=3,
            max_account_drawdown_percent=5.0,
        ),
    )


@pytest.fixture
def dry_run_broker():
    """Dry run broker with initial balance."""
    return DryRunBroker(initial_balance=10000.0)


@pytest.fixture
async def connected_broker(dry_run_broker):
    """Connected dry run broker."""
    await dry_run_broker.connect()
    return dry_run_broker


@pytest.fixture
def strategy_config():
    """Default strategy configuration."""
    return StrategyConfig()


@pytest.fixture
def scalping_strategy(strategy_config):
    """Scalping strategy instance."""
    return ScalpingStrategy(strategy_config)


@pytest.fixture
def risk_config():
    """Default risk configuration."""
    return RiskConfig()


@pytest.fixture
async def trading_engine(default_config, connected_broker):
    """Trading engine with connected broker."""
    engine = TradingEngine(config=default_config, broker_client=connected_broker)
    await engine.start()
    yield engine
    if engine.is_running:
        await engine.stop()


@pytest.fixture
def sample_trade():
    """Sample buy trade."""
    return Trade(
        symbol="TSLA",
        action=TradeAction.BUY,
        quantity=10,
        price=250.0,
        is_dry_run=True,
    )


@pytest.fixture
def sample_position():
    """Sample open position."""
    return Position(
        symbol="TSLA",
        quantity=10,
        entry_price=250.0,
        entry_timestamp=datetime.utcnow(),
        status=TradeStatus.OPEN,
    )


@pytest.fixture
def filled_buy_trade():
    """Filled buy trade."""
    return Trade(
        symbol="TSLA",
        action=TradeAction.BUY,
        quantity=10,
        price=250.0,
        filled_quantity=10,
        filled_price=250.05,
        filled_timestamp=datetime.utcnow(),
        status=TradeStatus.OPEN,
        is_dry_run=True,
    )


@pytest.fixture
def filled_sell_trade():
    """Filled sell trade."""
    return Trade(
        symbol="TSLA",
        action=TradeAction.SELL,
        quantity=10,
        price=251.0,
        filled_quantity=10,
        filled_price=250.95,
        filled_timestamp=datetime.utcnow(),
        status=TradeStatus.CLOSED,
        is_dry_run=True,
    )

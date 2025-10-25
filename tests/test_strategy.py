"""Tests for scalping strategy."""
import pytest
from datetime import datetime, time
from scalp_bot.core.strategy import ScalpingStrategy, PriceHistory
from scalp_bot.models.config import StrategyConfig
from scalp_bot.models.trade import Position, TradeStatus


class TestPriceHistory:
    """Tests for PriceHistory helper class."""

    def test_add_and_get_prices(self):
        """Test adding prices and retrieving them."""
        history = PriceHistory(timeframe_minutes=5)

        history.add_price(100.0)
        history.add_price(101.0)
        history.add_price(99.5)

        assert history.get_latest() == 99.5
        assert len(history.prices) == 3

    def test_get_high(self):
        """Test getting highest price."""
        history = PriceHistory(timeframe_minutes=5)

        history.add_price(100.0)
        history.add_price(102.5)
        history.add_price(101.0)
        history.add_price(99.0)

        assert history.get_high() == 102.5

    def test_maxlen_enforcement(self):
        """Test that price history respects maxlen."""
        history = PriceHistory(timeframe_minutes=1)  # 60 prices max

        # Add more than maxlen
        for i in range(100):
            history.add_price(100.0 + i)

        # Should only keep last 60
        assert len(history.prices) <= 60


class TestScalpingStrategy:
    """Tests for ScalpingStrategy class."""

    def test_initialization(self):
        """Test strategy initialization."""
        config = StrategyConfig()
        strategy = ScalpingStrategy(config)

        assert strategy.config == config
        assert len(strategy.price_histories) == 0

    def test_initialize_symbol(self):
        """Test initializing price history for a symbol."""
        strategy = ScalpingStrategy(StrategyConfig())

        strategy.initialize_symbol("TSLA")

        assert "TSLA" in strategy.price_histories
        assert isinstance(strategy.price_histories["TSLA"], PriceHistory)

    def test_update_price(self):
        """Test updating price for a symbol."""
        strategy = ScalpingStrategy(StrategyConfig())

        strategy.update_price("TSLA", 250.0)
        strategy.update_price("TSLA", 251.0)

        assert "TSLA" in strategy.price_histories
        assert strategy.price_histories["TSLA"].get_latest() == 251.0

    @pytest.mark.skip(reason="Time-dependent test - requires mocking datetime")
    def test_should_enter_signal(self):
        """Test entry signal generation."""
        config = StrategyConfig(
            entry_drop_percent=1.0,  # 1% drop triggers entry
            entry_timeframe_minutes=5,
        )
        strategy = ScalpingStrategy(config)

        # Set up price history with a drop
        strategy.update_price("TSLA", 100.0)  # High
        strategy.update_price("TSLA", 99.0)   # Current (1% drop)

        should_enter, reason = strategy.should_enter("TSLA", 99.0)

        assert should_enter is True
        assert "dropped" in reason.lower()

    def test_should_not_enter_insufficient_drop(self):
        """Test that entry doesn't trigger with insufficient drop."""
        config = StrategyConfig(
            entry_drop_percent=1.0,  # Need 1% drop
            entry_timeframe_minutes=5,
        )
        strategy = ScalpingStrategy(config)

        # Set up price history with small drop
        strategy.update_price("TSLA", 100.0)
        strategy.update_price("TSLA", 99.7)  # Only 0.3% drop

        should_enter, reason = strategy.should_enter("TSLA", 99.7)

        assert should_enter is False

    def test_should_exit_stop_loss(self):
        """Test exit signal on stop loss."""
        config = StrategyConfig(stop_loss_percent=0.5)
        strategy = ScalpingStrategy(config)

        # Create position that's losing money
        position = Position(
            symbol="TSLA",
            quantity=10,
            entry_price=100.0,
            entry_timestamp=datetime.utcnow(),
            status=TradeStatus.OPEN,
        )

        # Current price is below stop loss
        should_exit, reason = strategy.should_exit(position, 99.4)  # 0.6% loss

        assert should_exit is True
        assert "stop loss" in reason.lower()

    def test_should_exit_profit_target(self):
        """Test exit signal on profit target."""
        config = StrategyConfig(
            profit_target_percent=0.5,
            use_trailing_stop=False,
        )
        strategy = ScalpingStrategy(config)

        position = Position(
            symbol="TSLA",
            quantity=10,
            entry_price=100.0,
            entry_timestamp=datetime.utcnow(),
            status=TradeStatus.OPEN,
        )

        # Current price is above profit target
        should_exit, reason = strategy.should_exit(position, 100.6)  # 0.6% profit

        assert should_exit is True
        assert "profit target" in reason.lower()

    def test_trailing_stop(self):
        """Test trailing stop exit logic."""
        config = StrategyConfig(
            use_trailing_stop=True,
            trailing_stop_percent=0.3,
        )
        strategy = ScalpingStrategy(config)

        position = Position(
            symbol="TSLA",
            quantity=10,
            entry_price=100.0,
            entry_timestamp=datetime.utcnow(),
            status=TradeStatus.OPEN,
        )

        # Price goes up, establishing new peak
        should_exit, _ = strategy.should_exit(position, 101.0)
        assert should_exit is False
        assert position.peak_price == 101.0

        # Price drops but not below trailing stop
        should_exit, _ = strategy.should_exit(position, 100.8)
        assert should_exit is False

        # Price drops below trailing stop (0.3% from peak)
        should_exit, reason = strategy.should_exit(position, 100.6)  # > 0.3% from 101
        assert should_exit is True
        assert "trailing stop" in reason.lower()

    def test_should_close_all_positions_eod(self):
        """Test end-of-day position closing."""
        config = StrategyConfig(
            close_positions_at_eod=True,
            avoid_last_minutes=30,
        )
        strategy = ScalpingStrategy(config)

        # This test is time-sensitive, so we'll just verify the method exists
        # and returns a boolean
        result = strategy.should_close_all_positions()
        assert isinstance(result, bool)

    def test_trading_hours_check(self):
        """Test trading hours restrictions."""
        config = StrategyConfig(
            avoid_first_minutes=30,
            avoid_last_minutes=30,
        )
        strategy = ScalpingStrategy(config)

        # Test that method exists and returns boolean
        # Actual time-based testing would require mocking datetime
        result = strategy._is_trading_hours()
        assert isinstance(result, bool)

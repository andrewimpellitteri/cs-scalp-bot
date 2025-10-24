"""Scalping strategy implementation."""
import asyncio
from collections import deque
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
import logging

from ..models.config import StrategyConfig
from ..models.trade import Position

logger = logging.getLogger(__name__)


class PriceHistory:
    """Track price history for a symbol."""

    def __init__(self, timeframe_minutes: int):
        self.timeframe_minutes = timeframe_minutes
        self.prices: deque = deque(maxlen=timeframe_minutes * 60)  # 1 price per second
        self.timestamps: deque = deque(maxlen=timeframe_minutes * 60)

    def add_price(self, price: float, timestamp: Optional[datetime] = None) -> None:
        """Add a price to history."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.prices.append(price)
        self.timestamps.append(timestamp)

    def get_high(self, minutes: Optional[int] = None) -> Optional[float]:
        """Get highest price in the timeframe."""
        if not self.prices:
            return None

        if minutes is None:
            return max(self.prices)

        # Get high for specific time window
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        relevant_prices = [
            p for p, t in zip(self.prices, self.timestamps)
            if t >= cutoff_time
        ]
        return max(relevant_prices) if relevant_prices else None

    def get_latest(self) -> Optional[float]:
        """Get latest price."""
        return self.prices[-1] if self.prices else None


class ScalpingStrategy:
    """Scalping strategy implementation."""

    def __init__(self, config: StrategyConfig):
        self.config = config
        self.price_histories: Dict[str, PriceHistory] = {}

    def initialize_symbol(self, symbol: str) -> None:
        """Initialize price history for a symbol."""
        if symbol not in self.price_histories:
            self.price_histories[symbol] = PriceHistory(
                self.config.entry_timeframe_minutes
            )

    def update_price(self, symbol: str, price: float) -> None:
        """Update price history for a symbol."""
        self.initialize_symbol(symbol)
        self.price_histories[symbol].add_price(price)

    def should_enter(self, symbol: str, current_price: float) -> tuple[bool, Optional[str]]:
        """
        Determine if we should enter a position.

        Returns:
            tuple: (should_enter, reason)
        """
        # Check trading hours
        if not self._is_trading_hours():
            return False, "Outside trading hours"

        # Ensure we have price history
        if symbol not in self.price_histories:
            return False, "Insufficient price history"

        history = self.price_histories[symbol]
        recent_high = history.get_high(self.config.entry_timeframe_minutes)

        if recent_high is None:
            return False, "No recent high price"

        # Calculate drop from recent high
        drop_percent = ((recent_high - current_price) / recent_high) * 100

        if drop_percent >= self.config.entry_drop_percent:
            reason = f"Price dropped {drop_percent:.2f}% from recent high ${recent_high:.2f}"
            logger.info(f"Entry signal for {symbol}: {reason}")
            return True, reason

        return False, f"Drop {drop_percent:.2f}% < threshold {self.config.entry_drop_percent}%"

    def should_exit(
        self,
        position: Position,
        current_price: float
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if we should exit a position.

        Returns:
            tuple: (should_exit, reason)
        """
        # Calculate current P&L
        pnl, pnl_percent = position.calculate_unrealized_pnl(current_price)

        # Check stop loss
        if pnl_percent <= -self.config.stop_loss_percent:
            reason = f"Stop loss hit: {pnl_percent:.2f}%"
            logger.info(f"Exit signal for {position.symbol}: {reason}")
            return True, reason

        # Check profit target or trailing stop
        if self.config.use_trailing_stop:
            return self._check_trailing_stop(position, current_price, pnl_percent)
        else:
            return self._check_profit_target(position, current_price, pnl_percent)

    def _check_profit_target(
        self,
        position: Position,
        current_price: float,
        pnl_percent: float
    ) -> tuple[bool, Optional[str]]:
        """Check if profit target is reached."""
        if pnl_percent >= self.config.profit_target_percent:
            reason = f"Profit target hit: {pnl_percent:.2f}%"
            logger.info(f"Exit signal for {position.symbol}: {reason}")
            return True, reason
        return False, None

    def _check_trailing_stop(
        self,
        position: Position,
        current_price: float,
        pnl_percent: float
    ) -> tuple[bool, Optional[str]]:
        """Check trailing stop."""
        # Update peak price
        position.update_peak_price(current_price)

        # Calculate trailing stop price
        if position.peak_price:
            trailing_stop = position.peak_price * (
                1 - self.config.trailing_stop_percent / 100
            )
            position.trailing_stop_price = trailing_stop

            if current_price <= trailing_stop:
                reason = f"Trailing stop hit: ${current_price:.2f} <= ${trailing_stop:.2f}"
                logger.info(f"Exit signal for {position.symbol}: {reason}")
                return True, reason

        return False, None

    def _is_trading_hours(self) -> bool:
        """
        Check if current time is within allowed trading hours.

        Market hours: 9:30 AM - 4:00 PM ET
        """
        now = datetime.now().time()

        # Market open: 9:30 AM
        market_open = time(9, 30)
        trading_start = (
            datetime.combine(datetime.today(), market_open)
            + timedelta(minutes=self.config.avoid_first_minutes)
        ).time()

        # Market close: 4:00 PM
        market_close = time(16, 0)
        trading_end = (
            datetime.combine(datetime.today(), market_close)
            - timedelta(minutes=self.config.avoid_last_minutes)
        ).time()

        return trading_start <= now <= trading_end

    def should_close_all_positions(self) -> bool:
        """Check if we should close all positions (e.g., end of day)."""
        if not self.config.close_positions_at_eod:
            return False

        now = datetime.now().time()
        market_close = time(16, 0)

        # Close positions N minutes before market close
        close_time = (
            datetime.combine(datetime.today(), market_close)
            - timedelta(minutes=self.config.avoid_last_minutes)
        ).time()

        return now >= close_time

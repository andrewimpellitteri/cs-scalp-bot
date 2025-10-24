"""Trade and position models."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TradeStatus(str, Enum):
    """Trade status enum."""
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TradeAction(str, Enum):
    """Trade action enum."""
    BUY = "buy"
    SELL = "sell"


class Trade(BaseModel):
    """Trade model representing a single trade execution."""

    id: Optional[int] = None
    symbol: str
    action: TradeAction
    quantity: int
    price: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: TradeStatus = TradeStatus.PENDING

    # Filled information (from broker)
    filled_quantity: Optional[int] = None
    filled_price: Optional[float] = None
    filled_timestamp: Optional[datetime] = None

    # Order information
    order_id: Optional[str] = None
    is_dry_run: bool = False

    # P&L tracking
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None

    # Related position
    position_id: Optional[int] = None

    class Config:
        from_attributes = True


class Position(BaseModel):
    """Position model representing an open or closed position."""

    id: Optional[int] = None
    symbol: str
    quantity: int
    entry_price: float
    entry_timestamp: datetime

    # Current state
    current_price: Optional[float] = None
    status: TradeStatus = TradeStatus.OPEN

    # Exit information
    exit_price: Optional[float] = None
    exit_timestamp: Optional[datetime] = None

    # Strategy tracking
    peak_price: Optional[float] = None  # For trailing stop
    trailing_stop_price: Optional[float] = None

    # P&L
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_percent: Optional[float] = None
    realized_pnl: Optional[float] = None
    realized_pnl_percent: Optional[float] = None

    # Trade references
    entry_trade_id: Optional[int] = None
    exit_trade_id: Optional[int] = None

    class Config:
        from_attributes = True

    def calculate_unrealized_pnl(self, current_price: float) -> tuple[float, float]:
        """Calculate unrealized P&L based on current price."""
        self.current_price = current_price
        pnl = (current_price - self.entry_price) * self.quantity
        pnl_percent = ((current_price - self.entry_price) / self.entry_price) * 100
        self.unrealized_pnl = pnl
        self.unrealized_pnl_percent = pnl_percent
        return pnl, pnl_percent

    def calculate_realized_pnl(self, exit_price: float) -> tuple[float, float]:
        """Calculate realized P&L at exit."""
        pnl = (exit_price - self.entry_price) * self.quantity
        pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100
        self.realized_pnl = pnl
        self.realized_pnl_percent = pnl_percent
        return pnl, pnl_percent

    def update_peak_price(self, current_price: float) -> None:
        """Update peak price for trailing stop calculation."""
        if self.peak_price is None or current_price > self.peak_price:
            self.peak_price = current_price

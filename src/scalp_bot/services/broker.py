"""Broker client implementations for Schwab and dry-run mode."""
import asyncio
import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from ..models.trade import Trade, TradeAction, TradeStatus

logger = logging.getLogger(__name__)


class BrokerClient(ABC):
    """Abstract broker client interface."""

    @abstractmethod
    async def execute_trade(self, trade: Trade) -> Optional[Trade]:
        """Execute a trade."""
        pass

    @abstractmethod
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        pass

    @abstractmethod
    async def get_account_balance(self) -> Optional[float]:
        """Get account balance."""
        pass

    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[dict]:
        """Get current position for a symbol."""
        pass

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the broker."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the broker."""
        pass


class DryRunBroker(BrokerClient):
    """Dry run broker for testing without real trades."""

    def __init__(self, initial_balance: float = 10000.0):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions = {}
        self.connected = False

        # Simulated market data
        self.base_prices = {
            "TSLA": 250.0,
            "NVDA": 450.0,
            "AMD": 150.0,
        }

    async def connect(self) -> bool:
        """Connect to dry run broker."""
        logger.info("Connecting to dry run broker...")
        await asyncio.sleep(0.1)  # Simulate connection delay
        self.connected = True
        logger.info("Connected to dry run broker")
        return True

    async def disconnect(self) -> None:
        """Disconnect from dry run broker."""
        logger.info("Disconnecting from dry run broker...")
        self.connected = False

    async def execute_trade(self, trade: Trade) -> Optional[Trade]:
        """Execute a simulated trade."""
        if not self.connected:
            logger.error("Not connected to broker")
            trade.status = TradeStatus.FAILED
            return trade

        try:
            # Simulate execution delay
            await asyncio.sleep(0.05)

            # Get current price
            current_price = await self.get_current_price(trade.symbol)
            if current_price is None:
                trade.status = TradeStatus.FAILED
                return trade

            # Add some slippage (0.01% - 0.05%)
            slippage = random.uniform(0.0001, 0.0005)
            if trade.action == TradeAction.BUY:
                filled_price = current_price * (1 + slippage)
            else:
                filled_price = current_price * (1 - slippage)

            # Fill the trade
            trade.filled_quantity = trade.quantity
            trade.filled_price = filled_price
            trade.filled_timestamp = datetime.utcnow()
            trade.order_id = f"DRY_{datetime.utcnow().timestamp()}"

            # Update balance and positions
            if trade.action == TradeAction.BUY:
                cost = filled_price * trade.quantity
                if cost > self.balance:
                    logger.error(f"Insufficient balance: ${self.balance:.2f} < ${cost:.2f}")
                    trade.status = TradeStatus.FAILED
                    return trade

                self.balance -= cost
                self.positions[trade.symbol] = {
                    "quantity": trade.quantity,
                    "entry_price": filled_price,
                }
                trade.status = TradeStatus.OPEN
                logger.info(
                    f"[DRY RUN] BUY {trade.quantity} {trade.symbol} @ ${filled_price:.2f} "
                    f"| Balance: ${self.balance:.2f}"
                )

            else:  # SELL
                if trade.symbol not in self.positions:
                    logger.error(f"No position to sell for {trade.symbol}")
                    trade.status = TradeStatus.FAILED
                    return trade

                proceeds = filled_price * trade.quantity
                self.balance += proceeds

                # Calculate P&L
                position = self.positions[trade.symbol]
                pnl = (filled_price - position["entry_price"]) * trade.quantity
                pnl_percent = ((filled_price - position["entry_price"]) / position["entry_price"]) * 100

                trade.pnl = pnl
                trade.pnl_percent = pnl_percent
                trade.status = TradeStatus.CLOSED

                del self.positions[trade.symbol]

                logger.info(
                    f"[DRY RUN] SELL {trade.quantity} {trade.symbol} @ ${filled_price:.2f} "
                    f"| P&L: ${pnl:.2f} ({pnl_percent:.2f}%) | Balance: ${self.balance:.2f}"
                )

            return trade

        except Exception as e:
            logger.error(f"Error executing dry run trade: {e}", exc_info=True)
            trade.status = TradeStatus.FAILED
            return trade

    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get simulated current price."""
        if symbol not in self.base_prices:
            logger.warning(f"No base price for {symbol}")
            return None

        # Add random price movement (-0.5% to +0.5%)
        base_price = self.base_prices[symbol]
        volatility = random.uniform(-0.005, 0.005)
        current_price = base_price * (1 + volatility)

        return round(current_price, 2)

    async def get_account_balance(self) -> Optional[float]:
        """Get simulated account balance."""
        return self.balance

    async def get_position(self, symbol: str) -> Optional[dict]:
        """Get simulated position."""
        return self.positions.get(symbol)


class SchwabBroker(BrokerClient):
    """Schwab broker client using schwab-py library."""

    def __init__(self, app_key: str, app_secret: str, token_path: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.token_path = token_path
        self.client = None
        self.connected = False

    async def connect(self) -> bool:
        """Connect to Schwab API."""
        try:
            logger.info("Connecting to Schwab API...")

            # TODO: Implement actual Schwab API connection
            # This requires schwab-py library and OAuth setup
            # from schwab import auth, client
            # self.client = await auth.client_from_token_file(
            #     self.token_path,
            #     self.app_key,
            #     self.app_secret
            # )

            logger.warning("Schwab API integration not yet implemented")
            logger.warning("Please use DRY_RUN mode or implement Schwab connection")

            return False

        except Exception as e:
            logger.error(f"Failed to connect to Schwab API: {e}", exc_info=True)
            return False

    async def disconnect(self) -> None:
        """Disconnect from Schwab API."""
        if self.client:
            # TODO: Close Schwab client connection
            pass
        self.connected = False

    async def execute_trade(self, trade: Trade) -> Optional[Trade]:
        """Execute trade via Schwab API."""
        # TODO: Implement Schwab trade execution
        logger.error("Schwab trade execution not yet implemented")
        trade.status = TradeStatus.FAILED
        return trade

    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price from Schwab API."""
        # TODO: Implement Schwab price quotes
        logger.error("Schwab price quotes not yet implemented")
        return None

    async def get_account_balance(self) -> Optional[float]:
        """Get account balance from Schwab API."""
        # TODO: Implement Schwab account info
        logger.error("Schwab account info not yet implemented")
        return None

    async def get_position(self, symbol: str) -> Optional[dict]:
        """Get position from Schwab API."""
        # TODO: Implement Schwab position lookup
        logger.error("Schwab position lookup not yet implemented")
        return None


def create_broker_client(config) -> BrokerClient:
    """Factory function to create appropriate broker client."""
    if config.is_dry_run() or config.is_backtest():
        logger.info("Creating dry run broker")
        return DryRunBroker()

    elif config.is_live():
        if not config.schwab_app_key or not config.schwab_app_secret:
            logger.error("Schwab API credentials not configured")
            logger.warning("Falling back to dry run mode")
            return DryRunBroker()

        logger.info("Creating Schwab broker client")
        return SchwabBroker(
            app_key=config.schwab_app_key,
            app_secret=config.schwab_app_secret,
            token_path=config.schwab_token_path,
        )

    else:
        logger.warning(f"Unknown trading mode: {config.trading_mode}")
        return DryRunBroker()

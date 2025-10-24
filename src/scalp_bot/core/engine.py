"""Main trading engine orchestrating the bot."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..models.config import BotConfig
from ..models.trade import Position, Trade, TradeAction, TradeStatus
from .strategy import ScalpingStrategy

logger = logging.getLogger(__name__)


class TradingStats:
    """Track trading statistics."""

    def __init__(self):
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_trade_time: Optional[datetime] = None
        self.session_start = datetime.utcnow()
        self.total_wins = 0
        self.total_losses = 0

    def reset_daily(self) -> None:
        """Reset daily statistics."""
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.session_start = datetime.utcnow()

    def record_trade(self, pnl: float) -> None:
        """Record a completed trade."""
        self.daily_trades += 1
        self.daily_pnl += pnl
        self.last_trade_time = datetime.utcnow()

        if pnl > 0:
            self.total_wins += 1
        else:
            self.total_losses += 1


class TradingEngine:
    """Main trading engine."""

    def __init__(
        self,
        config: BotConfig,
        broker_client=None,  # Will be BrokerClient instance
        db_session=None,  # Will be database session
    ):
        self.config = config
        self.broker = broker_client
        self.db = db_session
        self.strategy = ScalpingStrategy(config.strategy)

        # State
        self.is_running = False
        self.positions: Dict[str, Position] = {}
        self.stats = TradingStats()

        # Account info
        self.account_balance = 0.0
        self.initial_balance = 0.0

    async def start(self) -> None:
        """Start the trading engine."""
        logger.info("Starting trading engine...")
        self.is_running = True

        try:
            # Initialize account balance
            await self._update_account_balance()
            self.initial_balance = self.account_balance

            # Initialize strategy for each symbol
            for symbol in self.config.symbols:
                self.strategy.initialize_symbol(symbol)

            logger.info(f"Trading engine started in {self.config.trading_mode} mode")
            logger.info(f"Watching symbols: {', '.join(self.config.symbols)}")
            logger.info(f"Account balance: ${self.account_balance:.2f}")

        except Exception as e:
            logger.error(f"Failed to start trading engine: {e}")
            self.is_running = False
            raise

    async def stop(self) -> None:
        """Stop the trading engine."""
        logger.info("Stopping trading engine...")
        self.is_running = False

        # Close all open positions if configured
        if self.config.strategy.close_positions_at_eod:
            await self.close_all_positions("Engine shutdown")

        logger.info("Trading engine stopped")

    async def run_iteration(self) -> None:
        """Run one iteration of the trading loop."""
        if not self.is_running:
            return

        try:
            # Check if we should close all positions
            if self.strategy.should_close_all_positions():
                await self.close_all_positions("End of day")
                return

            # Update account balance periodically
            await self._update_account_balance()

            # Check risk limits
            if not self._check_risk_limits():
                logger.warning("Risk limits exceeded, skipping iteration")
                return

            # Process each symbol
            for symbol in self.config.symbols:
                await self._process_symbol(symbol)

        except Exception as e:
            logger.error(f"Error in trading iteration: {e}", exc_info=True)

    async def _process_symbol(self, symbol: str) -> None:
        """Process a single symbol."""
        try:
            # Get current price
            current_price = await self._get_current_price(symbol)
            if current_price is None:
                logger.warning(f"Could not get price for {symbol}")
                return

            # Update strategy with current price
            self.strategy.update_price(symbol, current_price)

            # Check existing position for this symbol
            if symbol in self.positions:
                await self._manage_position(symbol, current_price)
            else:
                await self._check_entry(symbol, current_price)

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}", exc_info=True)

    async def _check_entry(self, symbol: str, current_price: float) -> None:
        """Check if we should enter a position."""
        # Check if we can open more positions
        if len(self.positions) >= self.config.risk.max_positions:
            return

        # Check entry signal
        should_enter, reason = self.strategy.should_enter(symbol, current_price)

        if should_enter:
            logger.info(f"Entry signal for {symbol}: {reason}")
            await self._open_position(symbol, current_price, reason)

    async def _manage_position(self, symbol: str, current_price: float) -> None:
        """Manage an existing position."""
        position = self.positions[symbol]

        # Update position with current price
        position.calculate_unrealized_pnl(current_price)

        # Check exit signal
        should_exit, reason = self.strategy.should_exit(position, current_price)

        if should_exit:
            logger.info(f"Exit signal for {symbol}: {reason}")
            await self._close_position(symbol, current_price, reason)

    async def _open_position(
        self,
        symbol: str,
        price: float,
        reason: str
    ) -> Optional[Position]:
        """Open a new position."""
        try:
            # Calculate position size
            position_value = self.account_balance * (
                self.config.risk.position_size_percent / 100
            )
            quantity = int(position_value / price)

            if quantity <= 0:
                logger.warning(f"Insufficient funds to open position in {symbol}")
                return None

            # Create buy trade
            trade = Trade(
                symbol=symbol,
                action=TradeAction.BUY,
                quantity=quantity,
                price=price,
                is_dry_run=self.config.is_dry_run(),
            )

            # Execute trade via broker
            executed_trade = await self._execute_trade(trade)

            if executed_trade and executed_trade.status == TradeStatus.OPEN:
                # Create position
                position = Position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=executed_trade.filled_price or price,
                    entry_timestamp=executed_trade.filled_timestamp or datetime.utcnow(),
                    entry_trade_id=executed_trade.id,
                    status=TradeStatus.OPEN,
                )

                self.positions[symbol] = position
                logger.info(
                    f"Opened position: {symbol} x{quantity} @ ${position.entry_price:.2f}"
                )

                # Save to database
                if self.db:
                    await self._save_position(position)

                return position

        except Exception as e:
            logger.error(f"Failed to open position for {symbol}: {e}", exc_info=True)

        return None

    async def _close_position(
        self,
        symbol: str,
        price: float,
        reason: str
    ) -> Optional[Trade]:
        """Close an existing position."""
        if symbol not in self.positions:
            logger.warning(f"No position to close for {symbol}")
            return None

        try:
            position = self.positions[symbol]

            # Create sell trade
            trade = Trade(
                symbol=symbol,
                action=TradeAction.SELL,
                quantity=position.quantity,
                price=price,
                position_id=position.id,
                is_dry_run=self.config.is_dry_run(),
            )

            # Execute trade
            executed_trade = await self._execute_trade(trade)

            if executed_trade and executed_trade.status == TradeStatus.CLOSED:
                # Update position
                exit_price = executed_trade.filled_price or price
                position.exit_price = exit_price
                position.exit_timestamp = executed_trade.filled_timestamp or datetime.utcnow()
                position.exit_trade_id = executed_trade.id
                position.status = TradeStatus.CLOSED

                # Calculate realized P&L
                pnl, pnl_percent = position.calculate_realized_pnl(exit_price)

                logger.info(
                    f"Closed position: {symbol} x{position.quantity} @ ${exit_price:.2f} "
                    f"| P&L: ${pnl:.2f} ({pnl_percent:.2f}%) | Reason: {reason}"
                )

                # Update stats
                self.stats.record_trade(pnl)

                # Save to database
                if self.db:
                    await self._save_position(position)

                # Remove from active positions
                del self.positions[symbol]

                return executed_trade

        except Exception as e:
            logger.error(f"Failed to close position for {symbol}: {e}", exc_info=True)

        return None

    async def close_all_positions(self, reason: str) -> None:
        """Close all open positions."""
        logger.info(f"Closing all positions: {reason}")

        symbols = list(self.positions.keys())
        for symbol in symbols:
            current_price = await self._get_current_price(symbol)
            if current_price:
                await self._close_position(symbol, current_price, reason)

    def _check_risk_limits(self) -> bool:
        """Check if we're within risk limits."""
        # Check daily trade limit
        if self.config.risk.max_daily_trades:
            if self.stats.daily_trades >= self.config.risk.max_daily_trades:
                logger.warning(
                    f"Daily trade limit reached: {self.stats.daily_trades}"
                )
                return False

        # Check daily loss limit
        if self.config.risk.max_daily_loss_percent:
            loss_percent = (self.stats.daily_pnl / self.initial_balance) * 100
            if loss_percent <= -self.config.risk.max_daily_loss_percent:
                logger.warning(
                    f"Daily loss limit exceeded: {loss_percent:.2f}%"
                )
                return False

        # Check trade frequency
        if self.stats.last_trade_time:
            time_since_last = datetime.utcnow() - self.stats.last_trade_time
            min_interval = timedelta(
                seconds=self.config.risk.max_trade_frequency_seconds
            )
            if time_since_last < min_interval:
                return False

        return True

    async def _execute_trade(self, trade: Trade) -> Optional[Trade]:
        """Execute a trade via the broker."""
        if self.broker:
            return await self.broker.execute_trade(trade)
        else:
            # Simulate execution for testing
            trade.status = TradeStatus.OPEN if trade.action == TradeAction.BUY else TradeStatus.CLOSED
            trade.filled_quantity = trade.quantity
            trade.filled_price = trade.price
            trade.filled_timestamp = datetime.utcnow()
            logger.info(f"[DRY RUN] Executed {trade.action} {trade.quantity} {trade.symbol} @ ${trade.price:.2f}")
            return trade

    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        if self.broker:
            return await self.broker.get_current_price(symbol)
        else:
            # For testing without broker
            logger.debug(f"No broker configured, cannot get price for {symbol}")
            return None

    async def _update_account_balance(self) -> None:
        """Update account balance from broker."""
        if self.broker:
            balance = await self.broker.get_account_balance()
            if balance is not None:
                self.account_balance = balance
        else:
            # Default balance for dry run
            if self.account_balance == 0:
                self.account_balance = 10000.0  # Default $10k for testing

    async def _save_position(self, position: Position) -> None:
        """Save position to database."""
        # TODO: Implement database save
        pass

    def get_status(self) -> dict:
        """Get current engine status."""
        return {
            "running": self.is_running,
            "mode": self.config.trading_mode,
            "symbols": self.config.symbols,
            "account_balance": self.account_balance,
            "positions": len(self.positions),
            "daily_trades": self.stats.daily_trades,
            "daily_pnl": self.stats.daily_pnl,
            "total_wins": self.stats.total_wins,
            "total_losses": self.stats.total_losses,
        }

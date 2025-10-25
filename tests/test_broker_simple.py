"""Simplified broker tests without random slippage issues."""
import pytest
from scalp_bot.services.broker import DryRunBroker, create_broker_client
from scalp_bot.models.trade import Trade, TradeAction, TradeStatus
from scalp_bot.models.config import BotConfig, TradingMode


class TestBrokerBasics:
    """Basic broker functionality tests."""

    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self):
        """Test basic connection lifecycle."""
        broker = DryRunBroker(initial_balance=10000.0)
        
        assert await broker.connect() is True
        assert broker.connected is True
        
        await broker.disconnect()
        assert broker.connected is False

    @pytest.mark.asyncio
    async def test_get_balance(self):
        """Test getting account balance."""
        broker = DryRunBroker(initial_balance=5000.0)
        await broker.connect()
        
        balance = await broker.get_account_balance()
        assert balance == 5000.0

    @pytest.mark.asyncio
    async def test_execute_trade_updates_balance(self):
        """Test that trades update balance."""
        broker = DryRunBroker(initial_balance=10000.0)
        await broker.connect()
        initial = broker.balance
        
        # Buy should decrease balance
        trade = Trade(
            symbol="TSLA",
            action=TradeAction.BUY,
            quantity=10,
            price=250.0,
            is_dry_run=True,
        )
        await broker.execute_trade(trade)
        
        assert broker.balance < initial

    @pytest.mark.asyncio
    async def test_insufficient_funds_rejected(self):
        """Test that trades fail with insufficient funds."""
        broker = DryRunBroker(initial_balance=1000.0)
        await broker.connect()
        
        trade = Trade(
            symbol="TSLA",
            action=TradeAction.BUY,
            quantity=100,  # Would cost $25,000
            price=250.0,
            is_dry_run=True,
        )
        
        executed = await broker.execute_trade(trade)
        assert executed.status == TradeStatus.FAILED

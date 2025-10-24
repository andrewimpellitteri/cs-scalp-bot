"""API routes for the scalping bot."""
import asyncio
import logging
from typing import Dict, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..models.config import BotConfig, TradingMode
from ..models.trade import Position

logger = logging.getLogger(__name__)

router = APIRouter()


class StartRequest(BaseModel):
    """Request to start the bot."""
    pass


class StopRequest(BaseModel):
    """Request to stop the bot."""
    pass


class ConfigUpdateRequest(BaseModel):
    """Request to update bot configuration."""
    config: BotConfig


class StatusResponse(BaseModel):
    """Bot status response."""
    running: bool
    mode: str
    symbols: List[str]
    account_balance: float
    positions: int
    daily_trades: int
    daily_pnl: float
    total_wins: int
    total_losses: int


@router.get("/status", response_model=StatusResponse)
async def get_status(request: Request):
    """Get current bot status."""
    engine = request.app.state.engine
    status = engine.get_status()
    return StatusResponse(**status)


@router.post("/start")
async def start_bot(request: Request):
    """Start the trading bot."""
    engine = request.app.state.engine

    if engine.is_running:
        raise HTTPException(status_code=400, detail="Bot is already running")

    try:
        await engine.start()

        # Start the trading loop
        async def trading_loop():
            while engine.is_running:
                try:
                    await engine.run_iteration()
                    await asyncio.sleep(1)  # Run every second
                except Exception as e:
                    logger.error(f"Error in trading loop: {e}", exc_info=True)
                    await asyncio.sleep(5)  # Wait before retrying

        # Create and store the task
        task = asyncio.create_task(trading_loop())
        request.app.state.engine_task = task

        return {"message": "Bot started successfully", "status": engine.get_status()}

    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_bot(request: Request):
    """Stop the trading bot."""
    engine = request.app.state.engine

    if not engine.is_running:
        raise HTTPException(status_code=400, detail="Bot is not running")

    try:
        await engine.stop()

        # Cancel the trading loop task if it exists
        if hasattr(request.app.state, "engine_task"):
            task = request.app.state.engine_task
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        return {"message": "Bot stopped successfully", "status": engine.get_status()}

    except Exception as e:
        logger.error(f"Failed to stop bot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config(request: Request):
    """Get current bot configuration."""
    engine = request.app.state.engine
    return engine.config


@router.put("/config")
async def update_config(config_update: ConfigUpdateRequest, request: Request):
    """Update bot configuration."""
    engine = request.app.state.engine

    if engine.is_running:
        raise HTTPException(
            status_code=400,
            detail="Cannot update config while bot is running. Stop the bot first."
        )

    try:
        # Update engine config
        engine.config = config_update.config

        # Recreate strategy with new config
        from ..core.strategy import ScalpingStrategy
        engine.strategy = ScalpingStrategy(config_update.config.strategy)

        # Recreate broker if trading mode changed
        if config_update.config.trading_mode != engine.config.trading_mode:
            from ..services.broker import create_broker_client

            # Disconnect old broker
            if hasattr(request.app.state, "broker"):
                await request.app.state.broker.disconnect()

            # Create new broker
            broker = create_broker_client(config_update.config)
            await broker.connect()
            engine.broker = broker
            request.app.state.broker = broker

        return {
            "message": "Configuration updated successfully",
            "config": engine.config
        }

    except Exception as e:
        logger.error(f"Failed to update config: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions(request: Request):
    """Get current positions."""
    engine = request.app.state.engine
    positions = [pos.dict() for pos in engine.positions.values()]
    return {"positions": positions}


@router.post("/positions/close-all")
async def close_all_positions(request: Request):
    """Close all open positions."""
    engine = request.app.state.engine

    if not engine.is_running:
        raise HTTPException(
            status_code=400,
            detail="Bot must be running to close positions"
        )

    try:
        await engine.close_all_positions("Manual close via API")
        return {
            "message": "All positions closed",
            "status": engine.get_status()
        }

    except Exception as e:
        logger.error(f"Failed to close positions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(request: Request):
    """Get trading statistics."""
    engine = request.app.state.engine
    stats = engine.stats

    return {
        "daily_trades": stats.daily_trades,
        "daily_pnl": stats.daily_pnl,
        "total_wins": stats.total_wins,
        "total_losses": stats.total_losses,
        "win_rate": (
            stats.total_wins / (stats.total_wins + stats.total_losses) * 100
            if (stats.total_wins + stats.total_losses) > 0
            else 0.0
        ),
        "session_start": stats.session_start.isoformat(),
        "last_trade_time": (
            stats.last_trade_time.isoformat()
            if stats.last_trade_time
            else None
        ),
    }


@router.post("/stats/reset")
async def reset_stats(request: Request):
    """Reset daily statistics."""
    engine = request.app.state.engine

    if engine.is_running:
        raise HTTPException(
            status_code=400,
            detail="Cannot reset stats while bot is running"
        )

    engine.stats.reset_daily()
    return {"message": "Statistics reset successfully"}

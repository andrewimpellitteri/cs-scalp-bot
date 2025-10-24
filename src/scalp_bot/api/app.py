"""FastAPI application for the scalping bot."""
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..core.engine import TradingEngine
from ..models.config import BotConfig
from ..services.broker import create_broker_client
from .routes import router

logger = logging.getLogger(__name__)

# Global engine instance
engine: TradingEngine = None
engine_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting application...")

    # Create data directory if it doesn't exist
    Path("./data").mkdir(exist_ok=True)

    # Initialize default config
    config = BotConfig()

    # Create broker client
    broker = create_broker_client(config)
    await broker.connect()

    # Create trading engine
    global engine
    engine = TradingEngine(config=config, broker_client=broker)

    # Store engine in app state
    app.state.engine = engine
    app.state.broker = broker

    logger.info("Application started")

    yield

    # Shutdown
    logger.info("Shutting down application...")

    if engine and engine.is_running:
        await engine.stop()

    if broker:
        await broker.disconnect()

    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Scalping Bot",
        description="Automated scalping trading bot for Charles Schwab",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Include API routes
    app.include_router(router, prefix="/api")

    # Setup templates
    templates_dir = Path(__file__).parent.parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    templates = Jinja2Templates(directory=str(templates_dir))

    # Setup static files
    static_dir = Path(__file__).parent.parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Root route - dashboard
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Render the main dashboard."""
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request}
        )

    return app

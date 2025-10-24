"""Scalping bot for automated trading."""
import logging

__version__ = "0.1.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    """Main entry point for the CLI."""
    import uvicorn
    from .api.app import create_app

    print(f"Starting Scalping Bot v{__version__}")
    print("Dashboard will be available at http://localhost:8000")
    print("Press Ctrl+C to stop")

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()

# Scalping Bot

An automated scalping trading bot for Charles Schwab with a web-based dashboard. Built with Python, FastAPI, and Docker.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **🚀 New User? Start with the [Complete Setup Guide](SETUP_GUIDE.md)** - No programming experience required!

## Features

- **Automated Trading**: Executes scalping strategies based on configurable parameters
- **Web Dashboard**: Monitor positions, P&L, and control the bot via a clean web interface
- **Dry Run Mode**: Test strategies with simulated trades before going live
- **Risk Management**: Built-in safeguards including daily loss limits, max trades, and position sizing
- **Docker Support**: Easy deployment and testing in isolated containers
- **Real-time Monitoring**: Live updates of positions, account balance, and trading statistics

## Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Complete installation instructions for non-technical users (macOS)
- **[Developer Guide](CLAUDE.md)** - Architecture, code structure, and development info
- **[Pre-Flight Checklist](PRE_FLIGHT_CHECKLIST.md)** - Safety checklist before going live
- **[Security Guide](SECURITY.md)** - Security best practices

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/andrewimpellitteri/cs-scalp-bot.git
   cd cs-scalp-bot
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Run the bot**
   ```bash
   uv run scalp-bot
   ```

4. **Access the dashboard**

   Open your browser to http://localhost:8000

## Docker Deployment

### Build and run with Docker Compose

```bash
# Build the image
docker-compose build

# Start the bot (in dry-run mode by default)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down
```

### Manual Docker build

```bash
# Build
docker build -t scalp-bot .

# Run
docker run -p 8000:8000 -v $(pwd)/data:/app/data scalp-bot
```

## Configuration

The bot can be configured through the web dashboard or by modifying the configuration directly.

### Key Configuration Options

#### Strategy Settings
- **Entry Drop %**: Buy when price drops this percentage from recent high
- **Entry Timeframe**: Time window to measure price drops (default: 5 minutes)
- **Profit Target %**: Sell when profit reaches this percentage
- **Stop Loss %**: Sell when loss reaches this percentage
- **Trailing Stop**: Optional trailing stop instead of fixed profit target

#### Risk Management
- **Position Size %**: Percentage of account to use per trade
- **Max Positions**: Maximum concurrent positions
- **Max Daily Loss %**: Auto-shutdown if daily loss exceeds this
- **Max Daily Trades**: Maximum number of trades per day
- **Trade Frequency**: Minimum seconds between trades

#### Trading Hours
- **Avoid First Minutes**: Skip trading N minutes after market open (default: 30)
- **Avoid Last Minutes**: Skip trading N minutes before market close (default: 30)
- **Close at EOD**: Automatically close all positions before market close

## Trading Modes

### Dry Run Mode (Default)
- Simulates trades without real money
- Uses simulated market data with realistic price movements
- Perfect for testing strategies and getting familiar with the bot
- No Schwab API credentials required

### Live Mode
- Executes real trades through Charles Schwab API
- Requires Schwab developer API credentials
- **Use with caution** - real money at risk!

## Schwab Account Setup

### CRITICAL: Use a Separate Account!

**⚠️ Never use your main Schwab account with the bot!**

Create a separate Schwab brokerage account for bot trading:

1. **Why it's important:**
   - Protects your main investments from any bot issues
   - Limits maximum loss to only what's in the test account
   - Makes performance tracking easier
   - Your main account stays completely untouched

2. **How to create a separate account (takes 10 minutes):**
   - Log in to Schwab.com with your existing account
   - Click "Open New Account" → "Individual Brokerage Account"
   - Complete the application (uses same login as main account)
   - Fund with small amount for testing ($1,000-$2,000 recommended)
   - Write down the new account number

3. **Example protection:**
   - Main account: $100,000 (never touched)
   - Bot test account: $2,000 (bot only trades here)
   - Maximum possible loss: Only the $2,000 in test account

See [SETUP_GUIDE.md](SETUP_GUIDE.md#step-3-set-up-a-separate-schwab-account-critical) for detailed instructions.

## Schwab API Setup (For Live Trading)

To use live trading, you'll need to set up the Schwab API:

1. **Apply for Schwab Developer Account**
   - Visit https://developer.schwab.com/
   - Create an account and apply for API access
   - Wait for approval (can take a few days)

2. **Create an App**
   - Create a new app in the Schwab developer portal
   - Note your App Key and App Secret

3. **Configure the Bot**
   - Set your credentials in the web dashboard or environment variables
   - `SCHWAB_APP_KEY`: Your app key
   - `SCHWAB_APP_SECRET`: Your app secret

4. **Authenticate**
   - The bot will guide you through OAuth authentication
   - Tokens are stored securely in `./data/tokens.json`

**Note**: The Schwab API integration is currently a placeholder. You'll need to implement the actual API calls using the `schwab-py` library or similar.

## Web Dashboard

The dashboard provides:

- **Status Panel**: Bot running state, trading mode, active symbols
- **Account Panel**: Balance, daily P&L, trade count
- **Performance Panel**: Open positions, wins/losses
- **Controls**: Start/stop bot, configure settings, close positions
- **Positions Table**: Real-time view of open positions with P&L

## Project Structure

```
scalp_bot/
├── src/scalp_bot/
│   ├── api/              # FastAPI application and routes
│   ├── core/             # Trading engine and strategy
│   ├── models/           # Data models (config, trades)
│   ├── services/         # Broker clients (Schwab, dry-run)
│   ├── templates/        # Web UI templates
│   └── static/           # Static assets (CSS, JS)
├── data/                 # Database and tokens (gitignored)
├── tests/                # Unit tests
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Safety Features

- **Daily Loss Limit**: Automatically stops trading if loss exceeds configured %
- **Max Trades**: Prevents over-trading with daily trade limits
- **Trade Frequency**: Enforces minimum time between trades
- **Position Limits**: Controls maximum concurrent positions
- **Trading Hours**: Avoids volatile open/close periods
- **Emergency Stop**: Manual stop button and close-all-positions feature

## Development

### Install dev dependencies

```bash
uv sync --group dev
```

### Run tests

```bash
uv run pytest
```

### Code formatting

```bash
uv run black src/
uv run ruff check src/
```

## Important Notes

- **Start in Dry Run**: Always test strategies in dry-run mode first
- **Test Account**: Use a separate Schwab account for testing
- **Monitor Closely**: Watch the bot closely when first running live
- **Risk Management**: Never risk more than you can afford to lose
- **Not Financial Advice**: This is educational software - use at your own risk

## Questions to Ask Before Configuring

Before going live, get answers to these questions:

1. **Entry/Exit**: Exact percentage drops for entry and profit targets?
2. **Stop Loss**: What stop-loss percentage?
3. **Position Sizing**: What % of account per trade?
4. **Risk Limits**: Max daily loss and max trades per day?
5. **Symbols**: Just TSLA or other stocks too?
6. **Trading Hours**: Any specific times to avoid?

See [CLAUDE.md](CLAUDE.md) for detailed questions to ask.

## Troubleshooting

### Bot won't start
- Check logs for errors
- Ensure port 8000 is not already in use
- Verify dependencies are installed: `uv sync`

### No trades executing
- Verify bot is running (check dashboard)
- Check if risk limits are hit (daily loss, max trades)
- Ensure you're within trading hours
- Check strategy parameters (entry conditions might be too strict)

### Docker issues
- Ensure Docker is running
- Check data directory permissions: `chmod -R 755 data/`
- View logs: `docker-compose logs -f`

## License

MIT License - see [LICENSE](LICENSE) file

## Disclaimer

This software is for educational purposes only. Trading stocks carries risk and you can lose money. The authors are not responsible for any financial losses incurred through use of this software. Always test thoroughly in dry-run mode and start with small amounts when going live.

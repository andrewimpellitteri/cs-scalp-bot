# Claude.md - Scalping Bot Documentation

## Project Overview

This is an automated scalping bot designed for day trading volatile stocks through Charles Schwab. Built for a non-technical user who wants to automate their manual scalping strategy.

### Key Requirements
- Day trades ~60 times per day
- Primarily trades volatile stocks (TSLA, etc.)
- Needs dry-run mode for testing before live trading
- Separate test account from main trading account
- Docker deployment for easy distribution
- Web interface for non-coders to operate

## Tech Stack

- **Language**: Python 3.10+
- **Package Manager**: uv (modern, fast Python package manager)
- **Web Framework**: FastAPI (for REST API and web UI)
- **Broker Integration**: Charles Schwab API via schwab-py library
- **Database**: SQLite with aiosqlite for trade history
- **Containerization**: Docker + Docker Compose
- **Frontend**: Vanilla JavaScript with Jinja2 templates

## Architecture

### Core Components

1. **Trading Engine** (`core/engine.py`)
   - Main orchestrator that runs the trading loop
   - Manages positions, account balance, and statistics
   - Enforces risk limits and safety checks
   - Coordinates between strategy and broker

2. **Strategy** (`core/strategy.py`)
   - Implements scalping logic (entry/exit signals)
   - Tracks price history for each symbol
   - Determines buy/sell signals based on configuration
   - Handles trading hours and time-based rules

3. **Broker Clients** (`services/broker.py`)
   - Abstract interface for broker operations
   - `DryRunBroker`: Simulates trades for testing
   - `SchwabBroker`: Real trading via Schwab API (stub for now)
   - Handles trade execution, price quotes, account info

4. **FastAPI Application** (`api/app.py`, `api/routes.py`)
   - REST API for controlling the bot
   - Serves the web dashboard
   - Endpoints: start/stop, config, status, positions, stats

5. **Data Models** (`models/`)
   - `BotConfig`: Main configuration with strategy and risk settings
   - `Trade`: Individual trade execution records
   - `Position`: Open/closed position tracking with P&L

### Trading Flow

1. User starts bot via web dashboard
2. Engine initializes with configured symbols
3. Main loop runs every second:
   - Fetch current prices for all symbols
   - Update strategy with latest prices
   - For each symbol:
     - If no position: check entry signals
     - If position exists: check exit signals (profit target, stop loss, trailing stop)
   - Execute trades as needed
   - Update statistics and UI
4. Risk checks at each iteration:
   - Daily loss limit
   - Max daily trades
   - Trade frequency throttling
   - Position limits

### Strategy Details

**Entry Logic**:
- Monitor price drops from recent high over a timeframe (e.g., 5 minutes)
- Enter when price drops >= configured percentage (e.g., 0.5%)
- Skip if outside trading hours or risk limits hit

**Exit Logic**:
- Fixed profit target: Sell at X% gain
- Stop loss: Sell at Y% loss
- Trailing stop (optional): Trail peak by Z% and sell on reversal
- End of day: Close all positions before market close

**Risk Management**:
- Position sizing: Use fixed % of account per trade
- Max positions: Limit concurrent positions
- Daily loss limit: Auto-shutdown if exceeded
- Trade frequency: Enforce minimum time between trades

## Configuration

All settings are adjustable via the web UI or config file:

### Strategy Settings
```python
entry_drop_percent: 0.5          # Buy when price drops 0.5%
entry_timeframe_minutes: 5        # Over 5-minute window
profit_target_percent: 0.3        # Sell at 0.3% profit
stop_loss_percent: 0.4            # Sell at 0.4% loss
use_trailing_stop: False          # Use trailing stop instead
trailing_stop_percent: 0.2        # Trail by 0.2% from peak
avoid_first_minutes: 30           # Skip first 30min after open
avoid_last_minutes: 30            # Skip last 30min before close
close_positions_at_eod: True      # Close all at EOD
```

### Risk Settings
```python
position_size_percent: 10.0       # Use 10% of account per trade
max_positions: 1                  # Only 1 position at a time
max_daily_loss_percent: 5.0       # Stop if lose 5% in a day
max_daily_trades: 100             # Max 100 trades per day
max_trade_frequency_seconds: 30   # Min 30 sec between trades
```

## Modes

### 1. Dry Run Mode (Default)
- Simulates trading with fake money
- Uses simulated price data (base prices with random volatility)
- No Schwab credentials required
- Perfect for testing and development
- Default account balance: $10,000

### 2. Live Mode
- Executes real trades via Schwab API
- **Requires Schwab developer credentials**
- Real money at risk
- Should only be used after thorough dry-run testing

### 3. Backtest Mode (TODO)
- Test strategy on historical data
- Not yet implemented

## Development Setup

### Using uv (recommended)

```bash
# Install dependencies
uv sync

# Run the bot
uv run scalp-bot

# Run with specific Python version
uv run --python 3.11 scalp-bot

# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run black src/
uv run ruff check src/
```

### Using Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## API Endpoints

### Status & Control
- `GET /api/status` - Get bot status (running, balance, P&L, etc.)
- `POST /api/start` - Start the trading bot
- `POST /api/stop` - Stop the trading bot

### Configuration
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration (bot must be stopped)

### Positions
- `GET /api/positions` - Get all open positions
- `POST /api/positions/close-all` - Close all positions immediately

### Statistics
- `GET /api/stats` - Get trading statistics
- `POST /api/stats/reset` - Reset daily statistics

## Web Dashboard

The dashboard is a single-page app that:
- Auto-refreshes every second
- Shows real-time status, balance, P&L
- Displays open positions with unrealized P&L
- Provides controls to start/stop and configure
- Has a modal for editing configuration
- Uses dark theme for easier viewing

Key UI elements:
- Status cards: Bot state, account info, performance
- Control panel: Start, stop, configure, close all
- Positions table: Live positions with P&L
- Config modal: Edit all strategy and risk parameters

## Questions to Ask Before Going Live

These questions need answers from the user's dad to properly configure the bot:

### Entry & Exit Strategy

1. **Entry signal**: What triggers a buy?
   - Price drop percentage from recent high?
   - What timeframe to measure the drop?
   - Any other indicators (volume, momentum)?

2. **Profit target**: When to sell for profit?
   - Fixed percentage gain?
   - Trailing stop from peak?
   - What percentage?

3. **Stop loss**: When to cut losses?
   - Fixed percentage loss?
   - How much?

4. **Time rules**: Any time-based restrictions?
   - Avoid first/last X minutes of market?
   - Close all positions at end of day?
   - Specific hours to avoid?

### Position Sizing & Risk

5. **Position sizing**: How much to risk per trade?
   - Fixed dollar amount?
   - Percentage of account?
   - Adjust based on volatility?

6. **Max loss**: Daily loss limit to stop trading?
   - Dollar amount?
   - Percentage of account?

7. **Max trades**: Hard limit on trades per day?
   - Prevent over-trading

### Stock Selection

8. **Watchlist**: Which stocks to trade?
   - Just TSLA?
   - Multiple stocks with same strategy?
   - Different parameters per stock?

### Account Info

9. **Schwab setup**:
   - Real-time data enabled?
   - API credentials obtained?
   - Separate test account balance?

10. **Testing plan**:
    - How long to dry-run before going live?
    - What metrics to evaluate success?

## Known Limitations & TODOs

### Current Limitations

1. **Schwab API Not Implemented**
   - `SchwabBroker` is a stub
   - Need to implement using schwab-py library
   - Requires OAuth flow for authentication

2. **No Database Persistence**
   - Trade history not saved to database yet
   - Position persistence not implemented
   - Statistics reset on restart

3. **No Backtesting**
   - Backtest mode not implemented
   - Would need historical price data

4. **Limited Price Data**
   - Dry-run mode uses simplified price simulation
   - Real market data would be better for testing

5. **No Alerts/Notifications**
   - No email/SMS alerts
   - No trade confirmations sent

### Future Enhancements

- [ ] Implement Schwab API integration
- [ ] Add database persistence for trades
- [ ] Implement backtesting with historical data
- [ ] Add email/SMS notifications
- [ ] Support for multiple strategies per symbol
- [ ] Paper trading with real market data
- [ ] Advanced charting in the UI
- [ ] Trade journal and analytics
- [ ] Support for other brokers (Alpaca, Interactive Brokers)
- [ ] Mobile-responsive UI
- [ ] WebSocket for real-time updates (instead of polling)
- [ ] Advanced risk metrics (Sharpe ratio, max drawdown)

## Testing Strategy

### Before Going Live

1. **Dry Run Testing** (1-2 weeks recommended)
   - Run in dry-run mode
   - Monitor for bugs and unexpected behavior
   - Verify strategy logic is correct
   - Ensure risk limits work properly

2. **Paper Trading with Real Data**
   - If possible, use real market data but simulated trades
   - More realistic than fully simulated prices

3. **Small Account Testing**
   - Start with very small position sizes
   - Verify trades execute correctly
   - Monitor for API issues or errors

4. **Gradual Scale-Up**
   - Slowly increase position sizes as confidence builds
   - Watch for any issues at higher volumes

### Safety Checklist

Before enabling live mode:
- [ ] Thoroughly tested in dry-run mode
- [ ] Verified all risk limits work
- [ ] Confirmed Schwab API credentials
- [ ] Set up separate test account
- [ ] Configured realistic position sizes
- [ ] Set conservative daily loss limits
- [ ] Tested emergency stop functionality
- [ ] Reviewed all strategy parameters
- [ ] Have plan to monitor actively at first

## Common Issues & Troubleshooting

### Bot Won't Start
- Check if port 8000 is already in use
- Verify all dependencies installed: `uv sync`
- Check logs for error messages

### No Trades Executing
- Verify bot is running (check /api/status)
- Check if within trading hours
- Verify risk limits not hit
- Check entry conditions not too strict
- Look at price history - might not have enough data yet

### Trades Executing Too Frequently
- Increase `max_trade_frequency_seconds`
- Increase `entry_drop_percent` threshold
- Reduce `entry_timeframe_minutes`

### Losses Exceeding Limits
- Verify `max_daily_loss_percent` is set
- Check if stop losses are too wide
- Review strategy parameters
- Consider reducing position size

### Docker Container Crashes
- Check logs: `docker-compose logs`
- Verify data directory permissions
- Ensure enough disk space

## Security Considerations

### API Credentials
- **Never commit** `tokens.json` or Schwab credentials to git
- Use environment variables for sensitive data
- Keep credentials in the `data/` directory (gitignored)

### Network Security
- Dashboard runs on all interfaces (0.0.0.0) by default
- Consider restricting to localhost only if not using Docker
- Use reverse proxy with HTTPS for production
- No authentication built-in - add if exposing to internet

### Financial Risk
- Start with small amounts
- Use separate test account
- Never risk more than you can afford to lose
- Monitor actively, especially at first
- This is educational software - not financial advice

## Contact & Support

For issues or questions:
1. Check this documentation
2. Review the code comments
3. Check the GitHub issues (if repo is public)
4. Test in dry-run mode first

## Disclaimer

This software is for educational purposes only. Trading stocks and options involves risk of loss. You are responsible for all trading decisions and any losses incurred. The authors make no guarantees about the performance or reliability of this software. Use at your own risk.

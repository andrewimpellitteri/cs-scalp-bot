# Pre-Flight Checklist - Before Going Live

**⚠️ CRITICAL: Complete this checklist BEFORE switching to live trading mode**

This checklist ensures you're ready to trade with real money. Print this out and check off each item.

---

## 1. Testing & Validation

### Dry-Run Testing
- [ ] Bot has run successfully in dry-run mode for at least **2 weeks**
- [ ] You've observed at least **100 simulated trades**
- [ ] The strategy is profitable in simulation (or you've adjusted parameters)
- [ ] You understand why trades are being executed
- [ ] No unexpected crashes or errors occurred
- [ ] Daily loss limits worked correctly when tested
- [ ] Max daily trades limit worked correctly
- [ ] Bot correctly avoided first/last 30 minutes of trading

### Strategy Validation
- [ ] Entry conditions make sense (not too aggressive, not too conservative)
- [ ] Profit targets are realistic for the stocks you're trading
- [ ] Stop losses are set appropriately (not too tight, not too wide)
- [ ] Position sizing is appropriate (recommend starting with 5-10% max)
- [ ] You've answered all configuration questions (see below)

---

## 2. Schwab Account Setup

### Account Configuration
- [ ] You have a **separate Charles Schwab account** for bot trading (not your main account)
- [ ] Account is funded with money **you can afford to lose**
- [ ] Account has real-time market data enabled (check with Schwab)
- [ ] Account has options/margin approved (if needed for your strategy)
- [ ] You know your account number

### API Access
- [ ] Applied for Schwab Developer account at https://developer.schwab.com/
- [ ] Developer account has been **approved** (can take 3-7 days)
- [ ] Created an app in the Schwab developer portal
- [ ] Have your App Key written down securely
- [ ] Have your App Secret written down securely
- [ ] **NEVER** shared or committed these credentials to GitHub/public places

---

## 3. Risk Management Configuration

### Position Limits
- [ ] **Position Size**: Set to ≤10% of account (recommend starting at 5%)
- [ ] **Max Positions**: Set to 1 initially (increase only after success)
- [ ] **Max Daily Trades**: Set to reasonable limit (50-100)

### Loss Protection
- [ ] **Max Daily Loss %**: Set to ≤5% of account value
- [ ] **Stop Loss %**: Configured and tested in dry-run
- [ ] **Profit Target %**: Realistic based on volatility
- [ ] You understand these limits will auto-stop the bot

### Emergency Plans
- [ ] You know how to click "Stop Bot" in the dashboard
- [ ] You know how to click "Close All Positions" in emergency
- [ ] You have Schwab's phone number handy: **1-800-435-4000**
- [ ] You know how to access Schwab's website to manually close trades

---

## 4. Strategy Parameters Finalized

Review and confirm all settings:

| Parameter | Your Value | Notes |
|-----------|-----------|-------|
| Entry Drop % | _______ % | When to buy |
| Entry Timeframe | _______ min | Time window for price drops |
| Profit Target % | _______ % | When to sell for profit |
| Stop Loss % | _______ % | When to sell for loss |
| Use Trailing Stop? | Yes / No | Alternative to fixed profit target |
| Trailing Stop % | _______ % | If using trailing stop |
| Position Size % | _______ % | Recommend 5-10% to start |
| Max Positions | _______ | Recommend 1 to start |
| Max Daily Loss % | _______ % | Recommend 3-5% |
| Max Daily Trades | _______ | Recommend 50-100 |
| Avoid First Minutes | _______ min | Recommend 30 |
| Avoid Last Minutes | _______ min | Recommend 30 |
| Close at EOD? | Yes / No | Recommend Yes |

---

## 5. Technical Setup

### System Requirements
- [ ] Mac is running macOS 10.15 or newer
- [ ] Docker Desktop is installed and **running** (whale icon in menu bar)
- [ ] Bot container is running: `docker-compose ps` shows "Up"
- [ ] Dashboard accessible at http://localhost:8000
- [ ] You can start/stop the bot from the dashboard
- [ ] All features work correctly (tested in dry-run)

### Monitoring Setup
- [ ] You have the dashboard bookmarked in your browser
- [ ] You know how to view logs: `docker-compose logs -f`
- [ ] You have notifications enabled on your Mac (for any browser alerts)
- [ ] Your Mac won't go to sleep during trading hours (System Settings → Energy)

---

## 6. Knowledge & Understanding

### Bot Behavior
- [ ] You understand the bot trades **automatically** once started
- [ ] You know it will execute trades **without asking you first**
- [ ] You understand trades happen in **seconds** (scalping is fast)
- [ ] You know the bot may make dozens of trades per day
- [ ] You understand some trades will lose money (that's normal)

### Market Understanding
- [ ] You know market hours: 9:30 AM - 4:00 PM ET (6:30 AM - 1:00 PM PT)
- [ ] You understand stocks can be volatile (especially TSLA, NVDA, etc.)
- [ ] You know about pattern day trading rules (need $25k for unlimited day trades)
- [ ] You understand slippage and commissions reduce profits

### Financial Risks
- [ ] You accept you could lose **all** the money in the trading account
- [ ] You're using money you **can afford to lose**
- [ ] You understand this is **not guaranteed income**
- [ ] You know the bot can have losing days, weeks, or months
- [ ] You won't blame the bot developers if you lose money

---

## 7. First Day Plan

### Before Market Open (Before 9:30 AM ET)
- [ ] Start Docker Desktop
- [ ] Start the bot: `docker-compose up -d`
- [ ] Open dashboard at http://localhost:8000
- [ ] Review all settings one more time
- [ ] Switch to **Live Mode** in configuration
- [ ] Take a deep breath

### At Market Open (9:30 AM ET)
- [ ] **Wait 30 minutes** (bot should skip this automatically)
- [ ] At 10:00 AM ET, click "Start Bot"
- [ ] Watch the dashboard **continuously** for the first hour
- [ ] Keep Schwab's website open to verify trades

### During the Day
- [ ] Check dashboard every 30-60 minutes
- [ ] Monitor P&L - don't panic on small losses
- [ ] Watch for daily loss limit
- [ ] Be ready to stop bot if something seems wrong
- [ ] Keep phone nearby in case you need to leave computer

### Before Market Close (3:30 PM ET)
- [ ] Bot should auto-close positions by 3:30 PM ET
- [ ] Verify all positions are closed (in dashboard and on Schwab)
- [ ] Review the day's performance
- [ ] Check logs for any errors: `docker-compose logs`

### After Market Close
- [ ] Stop the bot: Click "Stop Bot" in dashboard
- [ ] Shut down: `docker-compose down`
- [ ] Review statistics
- [ ] Take notes on what happened
- [ ] Plan adjustments if needed

---

## 8. Week One Plan

### Daily Monitoring
- [ ] **Day 1**: Watch continuously, position size at 5%
- [ ] **Day 2**: Watch frequently (every 30 min), position size at 5%
- [ ] **Day 3**: Watch every hour, position size at 5-7%
- [ ] **Day 4**: Watch every 2 hours, consider increasing position size
- [ ] **Day 5**: Review week, decide if ready to continue

### Success Criteria
- [ ] No major technical issues (crashes, missed trades, etc.)
- [ ] Risk limits working correctly
- [ ] You're comfortable with the bot's behavior
- [ ] Results are in line with expectations from dry-run
- [ ] You can handle the stress of automated trading

### Red Flags - STOP TRADING IF:
- [ ] Daily loss limit hit repeatedly (strategy may need adjustment)
- [ ] Bot crashes or has technical errors
- [ ] Trades executing at unexpected times
- [ ] You can't understand why trades are happening
- [ ] You're too stressed/anxious to continue
- [ ] Losses exceeding what you're comfortable with

---

## 9. Long-term Considerations

### Ongoing Monitoring
- [ ] Plan to review performance weekly
- [ ] Set aside time for maintenance and updates
- [ ] Keep learning about trading and strategies
- [ ] Stay updated on Schwab API changes

### Performance Evaluation
- [ ] Track win rate (should be >50% for scalping)
- [ ] Monitor average profit per trade
- [ ] Calculate total costs (commissions, slippage)
- [ ] Compare to buy-and-hold strategy
- [ ] Be honest about whether it's working

### Exit Strategy
- [ ] Decide in advance when you'd stop using the bot
- [ ] Set a maximum drawdown you're willing to accept
- [ ] Have a plan B if automated trading doesn't work out

---

## 10. Final Confirmation

**Before clicking "Start Bot" in live mode, confirm:**

- [ ] I have tested extensively in dry-run mode
- [ ] I have a separate Schwab account with limited funds
- [ ] I have set conservative risk limits
- [ ] I understand I could lose money
- [ ] I will monitor actively, especially at first
- [ ] I have an emergency stop plan
- [ ] I have read and understood all documentation
- [ ] I accept full responsibility for all trading decisions
- [ ] I will NOT trade with money I can't afford to lose

**Signature**: _________________________ **Date**: _____________

---

## Emergency Contacts

- **Schwab Customer Service**: 1-800-435-4000
- **Schwab Trading Support**: Available 24/7
- **Bot Support**: (See GitHub repository for issues)

---

## Remember

- Start small
- Monitor closely
- Don't panic
- Learn continuously
- Trading is risky
- Past performance ≠ future results
- This is not financial advice

**Good luck, and trade responsibly!** 🚀

# Risk Management & Safety Features

## Overview

This bot includes **multiple layers of protection** to prevent catastrophic losses. Each layer acts independently, so if one fails, others will still protect you.

---

## 🛡️ Multi-Layer Protection System

### Layer 1: Account Isolation
**MOST IMPORTANT**: Use a separate Schwab account for bot trading!

#### How to Set Up a Separate Schwab Account

1. **Log in to Schwab.com**
2. **Click "Open New Account"** (top right)
3. **Select "Individual Brokerage Account"**
4. **Complete the application** (takes 5-10 minutes)
5. **Fund the new account** with a small amount for testing
   - Recommended: $1,000 - $5,000 for initial testing
   - DO NOT fund with more than you can afford to lose
6. **Note the new account number** - this is what the bot will trade with

**Why This Matters:**
- Your main account stays completely untouched
- Bot ONLY has access to the specific account you configure
- If something goes wrong, losses are limited to the test account
- You can monitor the bot account separately from your main trading

**Example:**
- Main Account (#1234): $100,000 (never touched by bot)
- Bot Test Account (#5678): $2,000 (bot trades here)
- Maximum possible loss: $2,000 (the bot account balance)

---

### Layer 2: Kill Switch (Account Drawdown Limit)

**Hardcoded maximum loss** from your starting balance.

**Default: 10%** of starting balance

**How it works:**
- Bot tracks your account balance when it starts
- If account drops 10% from starting balance, **bot stops immediately**
- Requires manual restart (you must click "Start Bot" again)
- Example: Start with $5,000 → If balance drops to $4,500, bot stops

**Configuration:**
```python
max_account_drawdown_percent: 10.0  # 10% max loss from start
```

**Hard Limit:** Cannot be set higher than 30%

---

### Layer 3: Daily Loss Limits (Two Types)

#### A. Percentage-Based Daily Loss

**Default: 5%** of account balance per day

**How it works:**
- If you lose 5% in a single day, bot stops
- Enters 60-minute cooldown (configurable)
- Example: $5,000 account → Stops if you lose $250 in one day

**Configuration:**
```python
max_daily_loss_percent: 5.0  # 5% daily loss limit
```

**Hard Limit:** Cannot exceed 20%

#### B. Dollar-Based Daily Loss (Optional)

Set a **hard dollar amount** you're willing to lose per day.

**How it works:**
- Set a specific dollar limit (e.g., $200)
- If daily loss hits $200, bot stops regardless of percentage
- Useful if you want absolute certainty on max daily loss

**Configuration:**
```python
max_daily_loss_dollars: 200.0  # Stop if lose $200/day
```

**Recommendation:** Set both percentage AND dollar limits for double protection!

---

### Layer 4: Consecutive Loss Circuit Breaker

**Default:** Stop after **5 losses in a row**

**How it works:**
- Tracks winning and losing trades
- If you lose 5 (or configured number) trades in a row, bot stops
- This catches strategy failures early
- Enters cooldown period (60 min default)

**Why this matters:**
- If your strategy isn't working, this stops it before massive losses
- Prevents the bot from "revenge trading" trying to recover

**Configuration:**
```python
max_consecutive_losses: 5  # Stop after 5 losses in a row
```

---

### Layer 5: Position Size Limits

#### A. Percentage-Based Position Sizing

**Default: 10%** of account per trade

**How it works:**
- Each trade uses max 10% of your account balance
- Example: $5,000 account → Max $500 per trade
- Adjusts automatically as account grows/shrinks

**Configuration:**
```python
position_size_percent: 10.0  # 10% of account per trade
```

**Hard Limit:** Cannot exceed 50% (never risk more than half your account on one trade)

#### B. Dollar-Based Position Limit (Optional)

Set a **hard dollar cap** on position size.

**How it works:**
- Caps position value at a specific dollar amount
- Overrides percentage if it would be higher
- Example: Set $1,000 max, even if 10% of account is $1,500

**Configuration:**
```python
max_position_value_dollars: 1000.0  # Max $1,000 per trade
```

#### C. Share Quantity Limit (Optional)

**Hard limit on number of shares** per trade.

**Why this matters:**
- Prevents "fat finger" errors
- Catches calculation bugs
- Example: Accidentally buying 10,000 shares instead of 100

**Configuration:**
```python
max_shares_per_trade: 200  # Never buy more than 200 shares
```

**Recommendation:** Set this based on typical share counts for your stock
- TSLA at $250: 200 shares = $50,000 (probably too much!)
- Adjust based on what makes sense for your account size

---

### Layer 6: Position Count Limit

**Default: 1 position** at a time

**How it works:**
- Bot can only hold 1 open position at once
- Must close current position before opening another
- Prevents overexposure

**Configuration:**
```python
max_positions: 1  # Only 1 position at a time
```

**For advanced users:** Can be increased to 5 max, but start with 1!

---

### Layer 7: Daily Trade Limit

**Default: 100 trades** per day

**How it works:**
- Prevents over-trading
- If you hit 100 trades in a day, bot stops
- Protects against runaway loops

**Why this matters:**
- Scalping can rack up commissions quickly
- Catches bugs that cause excessive trading

**Configuration:**
```python
max_daily_trades: 100  # Max 100 trades per day
```

**Note:** This is a safety limit. Your dad might not hit this, but it prevents disasters.

---

### Layer 8: Trade Frequency Throttle

**Default: 30 seconds** minimum between trades

**How it works:**
- After executing a trade, bot waits at least 30 seconds before next trade
- Prevents rapid-fire trading
- Gives you time to react if something's wrong

**Configuration:**
```python
max_trade_frequency_seconds: 30  # 30 sec between trades
```

---

### Layer 9: Cooldown Periods

**After hitting a risk limit, bot enters "cooldown"**

**Default: 60 minutes** cooldown after daily loss limit

**How it works:**
- Bot stops trading
- Locks out for specified time period
- Requires manual restart after cooldown (by default)
- Prevents emotional "restart and try again" behavior

**Configuration:**
```python
cooldown_after_daily_loss_minutes: 60  # 1 hour cooldown
require_manual_restart_after_stop: True  # Must manually restart
```

**Why this matters:**
- Forces you to review what went wrong
- Prevents impulsive restarts
- Gives time to check logs and assess situation

---

## 🚨 Recommended Configuration for First-Time Users

### Conservative Settings (START HERE!)

```python
# Position Sizing - VERY CONSERVATIVE
position_size_percent: 5.0          # Only 5% per trade
max_position_value_dollars: 500.0   # Cap at $500 regardless
max_positions: 1                     # One at a time
max_shares_per_trade: 20             # Reasonable for most stocks

# Daily Limits - STRICT
max_daily_loss_percent: 3.0          # Stop at 3% daily loss
max_daily_loss_dollars: 150.0        # Also stop at $150 loss
max_daily_trades: 50                 # Max 50 trades/day

# Circuit Breakers - AGGRESSIVE
max_consecutive_losses: 3            # Stop after 3 losses in a row
max_account_drawdown_percent: 5.0    # Kill switch at 5% total drawdown

# Cooldowns - LONG
cooldown_after_daily_loss_minutes: 120  # 2 hour cooldown
require_manual_restart_after_stop: True # Always require restart
max_trade_frequency_seconds: 60         # 1 minute between trades
```

### After 2 Weeks of Success, Can Relax To:

```python
# Position Sizing - MODERATE
position_size_percent: 10.0         # 10% per trade
max_position_value_dollars: 1000.0  # Cap at $1,000
max_positions: 1                     # Still one at a time
max_shares_per_trade: 50             # More shares allowed

# Daily Limits - MODERATE
max_daily_loss_percent: 5.0          # 5% daily loss
max_daily_loss_dollars: 250.0        # $250 daily loss
max_daily_trades: 100                # 100 trades/day

# Circuit Breakers - MODERATE
max_consecutive_losses: 5            # 5 losses in a row
max_account_drawdown_percent: 10.0   # 10% total drawdown

# Cooldowns - MODERATE
cooldown_after_daily_loss_minutes: 60   # 1 hour cooldown
require_manual_restart_after_stop: True # Still require restart
max_trade_frequency_seconds: 30          # 30 sec between trades
```

---

## 📊 Real-World Examples

### Example 1: Small Account ($2,000)

**Starting Balance:** $2,000
**Position Size:** 5% = $100 per trade
**Daily Loss Limit:** 3% = $60
**Kill Switch:** 10% = $200

**Scenario:**
1. Opens position: Buys $100 worth of TSLA (small position)
2. Makes 3 profitable trades: +$30 total
3. Then has 3 losing trades in a row: -$40 total
4. **Bot stops** due to consecutive loss limit (3 in a row)
5. **Total damage:** -$10 (very small)

### Example 2: Medium Account ($10,000)

**Starting Balance:** $10,000
**Position Size:** 10% = $1,000 per trade (capped at $1,000)
**Daily Loss Limit:** 5% = $500
**Kill Switch:** 10% = $1,000

**Scenario - Good Day:**
1. Makes 15 trades throughout the day
2. Win rate: 60% (9 wins, 6 losses)
3. Avg win: +$40, Avg loss: -$25
4. **Daily P&L:** +$210
5. Bot continues normally

**Scenario - Bad Day:**
1. Makes 8 trades, all losses averaging -$60 each
2. Total loss: -$480
3. **Bot stops** just before hitting $500 daily limit
4. Enters 60-minute cooldown
5. **Maximum damage:** -$480 (below limit)
6. Account still has $9,520 (no catastrophic loss)

### Example 3: Runaway Prevention

**Starting Balance:** $5,000

**Scenario - Bug Causes Rapid Trading:**
1. Bug in strategy causes bot to try trading every second
2. **Trade frequency throttle** (30 sec) prevents most trades
3. Makes 5 bad trades very quickly
4. **Consecutive loss limit** (5) triggers
5. **Bot stops immediately**
6. **Maximum damage:** 5 trades x max $250 position = $1,250 potential
7. Actual loss likely much smaller due to throttling
8. Bot locks down, requires manual review

---

## 🔍 Monitoring & Alerts

### What to Watch

**Dashboard Shows:**
- Current account balance
- Daily P&L (profit/loss)
- Number of trades today
- Consecutive wins/losses
- Largest win/loss
- Time until cooldown expires (if in cooldown)
- Stop reason (if stopped by risk limit)

### Warning Signs

**Stop trading and review if you see:**
- ⚠️ Consecutive losses increasing
- ⚠️ Daily P&L steadily negative
- ⚠️ More trades than expected
- ⚠️ Unusual position sizes
- ⚠️ Rapid-fire trading (throttle being hit constantly)

---

## 🛠️ How to Configure

### Via Web Dashboard

1. Go to http://localhost:8000
2. Click "Configure"
3. Scroll to "Risk Management" section
4. Adjust sliders/inputs
5. Click "Save Configuration"
6. **Restart bot for changes to take effect**

### Via Configuration File

Edit `config.example.json` or create `.env` file (see documentation).

---

## 🆘 Emergency Procedures

### If Bot Won't Stop

1. **Click "Stop Bot"** in dashboard (primary)
2. **Click "Close All Positions"** (emergency)
3. **Close browser tab** (stops dashboard but bot may continue)
4. **Run:** `docker-compose down` (kills container)
5. **Call Schwab:** 1-800-435-4000 (last resort)

### If Losses Exceed Limits

**This should be impossible with all the safeguards, but if it happens:**

1. Stop bot immediately (see above)
2. Close all positions via Schwab website
3. Review logs: `docker-compose logs -f`
4. Check configuration - were limits set correctly?
5. Report bug on GitHub (if limits failed)

---

## ✅ Pre-Flight Safety Checklist

Before going live, verify:

- [ ] Using **separate Schwab account** (not main account)
- [ ] Starting balance is money you **can afford to lose**
- [ ] `max_account_drawdown_percent` set (default 10%)
- [ ] `max_daily_loss_percent` set (recommended 3-5%)
- [ ] `max_daily_loss_dollars` set (specific $ amount)
- [ ] `max_consecutive_losses` set (recommended 3-5)
- [ ] `position_size_percent` conservative (start at 5-10%)
- [ ] `max_position_value_dollars` set (safety cap)
- [ ] `max_shares_per_trade` set (prevents fat fingers)
- [ ] `max_positions` set to 1 (safest)
- [ ] `max_daily_trades` set (reasonable limit)
- [ ] `max_trade_frequency_seconds` set (throttle)
- [ ] `cooldown_after_daily_loss_minutes` set (60+ min)
- [ ] `require_manual_restart_after_stop` set to `True`
- [ ] You understand what each limit does
- [ ] You've tested in dry-run mode for 2+ weeks

---

## 🎓 Understanding the Math

### Example: $5,000 Account with Default Settings

**Position Sizing:**
- 10% per trade = $500 max per position
- If TSLA is $250/share: 500 ÷ 250 = 2 shares per trade
- If TSLA drops 0.4% (stop loss): Loss = $5 per share × 2 = $10

**Daily Loss Limit:**
- 5% of $5,000 = $250 max daily loss
- At $10 loss per trade, would need **25 consecutive losses** to hit limit
- Consecutive loss limit (5) would stop you after 5 losses = $50 loss

**Kill Switch:**
- 10% of $5,000 = $500 max total drawdown
- Starting balance: $5,000
- If account drops to $4,500, bot stops completely
- Requires manual review and restart

**Worst Case Scenario:**
- Somehow all limits fail (extremely unlikely)
- You lose entire test account: $5,000
- Your main account (e.g., $100,000) is completely untouched

---

## 📞 Support

Questions? Issues?
- Review this document
- Check [SECURITY.md](SECURITY.md)
- See [PRE_FLIGHT_CHECKLIST.md](PRE_FLIGHT_CHECKLIST.md)
- Open GitHub issue

---

**Remember: No system is perfect. Always monitor actively, especially at first!**

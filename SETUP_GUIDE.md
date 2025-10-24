# Complete Setup Guide for Scalping Bot

**For macOS Users with No Programming Experience**

This guide will walk you through every step needed to get the scalping bot running on your Mac, even if you've never used developer tools before.

---

## Table of Contents

1. [What You'll Need](#what-youll-need)
2. [Step 1: Install Homebrew](#step-1-install-homebrew)
3. [Step 2: Install Docker Desktop](#step-2-install-docker-desktop)
4. [Step 3: Download the Bot from GitHub](#step-3-download-the-bot-from-github)
5. [Step 4: Run the Bot](#step-4-run-the-bot)
6. [Step 5: Configure Your Strategy](#step-5-configure-your-strategy)
7. [Step 6: Setting Up Schwab API (For Live Trading)](#step-6-setting-up-schwab-api-for-live-trading)
8. [Troubleshooting](#troubleshooting)
9. [Daily Usage](#daily-usage)

---

## What You'll Need

- A Mac computer (macOS 10.15 or newer)
- Internet connection
- About 30 minutes for initial setup
- Charles Schwab account (for live trading - not needed for testing)

---

## Step 1: Install Homebrew

Homebrew is a package manager for Mac that makes it easy to install software.

### 1.1 Open Terminal

1. Press `Command (⌘) + Space` to open Spotlight Search
2. Type `Terminal` and press Enter
3. A window with a command prompt will open (it looks like a black or white window with text)

### 1.2 Install Homebrew

1. Copy this entire command (click and drag to select, then press `⌘ + C`):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Paste it into Terminal (press `⌘ + V`) and press Enter
3. You'll be asked to enter your Mac's password (the one you use to log in)
   - **Note**: When you type your password, nothing will appear on screen - this is normal for security!
4. Press Enter and wait for the installation to complete (this may take 5-10 minutes)

### 1.3 Verify Homebrew Installed

Type this and press Enter:
```bash
brew --version
```

You should see something like `Homebrew 4.x.x` - that means it worked!

---

## Step 2: Install Docker Desktop

Docker lets you run the trading bot in an isolated, safe environment.

### 2.1 Download Docker Desktop

**Option A: Using Homebrew (Recommended)**

In Terminal, type:
```bash
brew install --cask docker
```

Wait for it to complete (5-10 minutes).

**Option B: Manual Download**

1. Go to https://www.docker.com/products/docker-desktop
2. Click "Download for Mac"
3. Choose the version for your Mac:
   - **Apple Silicon (M1/M2/M3)**: Download "Apple Chip" version
   - **Intel Mac**: Download "Intel Chip" version
   - Not sure? Click the Apple logo (top left) → "About This Mac" → Look for "Chip" or "Processor"
4. Open the downloaded file and drag Docker to Applications

### 2.2 Start Docker Desktop

1. Open your Applications folder (`Command + Shift + A` in Finder)
2. Double-click on Docker
3. You may be asked to allow Docker to run - click "Open"
4. Docker will ask for permission - enter your Mac password
5. Wait for Docker to start (you'll see a whale icon in your menu bar at the top of the screen)

### 2.3 Verify Docker is Running

In Terminal, type:
```bash
docker --version
```

You should see something like `Docker version 24.x.x` - success!

---

## Step 3: Download the Bot from GitHub

### 3.1 Install Git (if not already installed)

In Terminal, type:
```bash
git --version
```

If you see a version number, Git is already installed - **skip to Step 3.2**.

If not, you'll be prompted to install Command Line Tools - click "Install" and wait.

### 3.2 Choose a Location

Decide where you want to keep the bot files. We recommend your Documents folder.

In Terminal, type:
```bash
cd ~/Documents
```

This moves you to your Documents folder.

### 3.3 Download the Bot

Copy and paste this command (replace `YOUR-GITHUB-USERNAME` and `REPO-NAME` with the actual values):

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/scalp_bot.git
```

**Example:**
```bash
git clone https://github.com/andrewimpellitteri/scalp_bot.git
```

Wait for the download to complete. You'll now have a folder called `scalp_bot` in your Documents.

### 3.4 Enter the Bot Directory

```bash
cd scalp_bot
```

You're now inside the bot's folder.

---

## Step 4: Run the Bot

This is the easy part!

### 4.1 Start the Bot with Docker

In Terminal (make sure you're still in the `scalp_bot` folder), type:

```bash
docker-compose up -d
```

- The first time you run this, it will take 3-5 minutes to download and build everything
- `-d` means it runs in the background
- You'll see lots of text scroll by - this is normal!

### 4.2 Open the Dashboard

1. Open your web browser (Safari, Chrome, etc.)
2. Go to: http://localhost:8000
3. You should see the Scalping Bot Dashboard!

**Congratulations!** The bot is now running in **dry-run mode** (simulation only - no real money).

---

## Step 5: Configure Your Strategy

### 5.1 Open the Dashboard

Make sure you're at http://localhost:8000

### 5.2 Click "Configure" Button

You'll see a configuration screen with all the settings.

### 5.3 Key Settings to Adjust

Fill in these based on your trading strategy:

| Setting | What It Means | Example |
|---------|---------------|---------|
| **Entry Drop %** | Buy when price drops this much from recent high | 0.5 (means 0.5%) |
| **Profit Target %** | Sell when you make this much profit | 0.3 (means 0.3%) |
| **Stop Loss %** | Sell when you lose this much to cut losses | 0.4 (means 0.4%) |
| **Position Size %** | How much of your account to use per trade | 10 (means 10%) |
| **Max Daily Trades** | Maximum trades per day to prevent overtrading | 100 |
| **Max Daily Loss %** | Stop trading if you lose this much in one day | 5 (means 5%) |

### 5.4 Save Configuration

Click "Save Configuration" at the bottom.

### 5.5 Test the Bot

1. Click the **"Start Bot"** button
2. Watch the dashboard - it will start simulating trades
3. The "Daily P&L" will change as it makes simulated trades
4. To stop: Click **"Stop Bot"**

**Important**: Right now it's in **dry-run mode** - it's NOT using real money! This is perfect for testing.

---

## Step 6: Setting Up Schwab API (For Live Trading)

⚠️ **Warning**: Only do this AFTER you've tested extensively in dry-run mode!

### 6.1 Create a Schwab Developer Account

1. Go to https://developer.schwab.com/
2. Click "Register" in the top right
3. Fill out the registration form
4. You'll need:
   - Your Schwab account number
   - Email address
   - Phone number

### 6.2 Wait for Approval

- Schwab will review your application
- This typically takes **3-7 business days**
- You'll receive an email when approved

### 6.3 Create an App

Once approved:

1. Log in to https://developer.schwab.com/
2. Click "My Apps" or "Create App"
3. Fill in:
   - **App Name**: "Scalping Bot" (or whatever you want)
   - **Description**: "Personal trading automation"
   - **Redirect URI**: `https://localhost:8000/callback` (exactly this)
4. Click "Create"

### 6.4 Get Your Credentials

You'll see two important pieces of information:
- **App Key** (also called Client ID)
- **App Secret** (also called Client Secret)

**IMPORTANT**: Write these down somewhere safe! You'll need them.

### 6.5 Configure the Bot with Schwab Credentials

**Option A: Environment Variables (Recommended)**

1. In Terminal, go to your bot folder:
   ```bash
   cd ~/Documents/scalp_bot
   ```

2. Create a file called `.env`:
   ```bash
   echo "SCHWAB_APP_KEY=your_app_key_here" > .env
   echo "SCHWAB_APP_SECRET=your_app_secret_here" >> .env
   ```

   Replace `your_app_key_here` and `your_app_secret_here` with your actual values.

3. Restart the bot:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

**Option B: Through the Dashboard**

1. Open the dashboard at http://localhost:8000
2. Click "Configure"
3. There will be fields for Schwab App Key and Secret
4. Enter your credentials
5. Save

### 6.6 Switch to Live Mode

⚠️ **DANGER ZONE** - Real money at risk!

**Before going live, make sure:**
- [ ] You've tested for at least 1-2 weeks in dry-run mode
- [ ] Your strategy parameters are finalized
- [ ] You're using a **separate test account** with limited funds
- [ ] You've set conservative position sizes (start small!)
- [ ] You have daily loss limits configured
- [ ] You'll be monitoring actively

**To enable live trading:**

1. Open dashboard at http://localhost:8000
2. Make sure the bot is **stopped** (click Stop Bot if running)
3. Click "Configure"
4. Change "Trading Mode" from "Dry Run" to "Live Trading"
5. Save Configuration
6. Take a deep breath
7. Click "Start Bot"

---

## Troubleshooting

### "Docker command not found"

**Solution**: Docker Desktop isn't running or not installed.
1. Check if you see the whale icon in your menu bar (top of screen)
2. If not, open Docker Desktop from Applications
3. Wait for it to start (the whale stops animating when ready)

### "Cannot connect to localhost:8000"

**Solution**: The bot isn't running.
1. In Terminal, go to the bot folder:
   ```bash
   cd ~/Documents/scalp_bot
   ```
2. Check if it's running:
   ```bash
   docker-compose ps
   ```
3. If it says "stopped" or nothing appears:
   ```bash
   docker-compose up -d
   ```

### "Port 8000 is already in use"

**Solution**: Something else is using port 8000.
1. Stop the bot:
   ```bash
   docker-compose down
   ```
2. Change the port by editing `docker-compose.yml`:
   - Find the line that says `"8000:8000"`
   - Change it to `"8001:8000"` (or any other number)
3. Start the bot:
   ```bash
   docker-compose up -d
   ```
4. Access dashboard at http://localhost:8001 (use your new port number)

### Bot keeps stopping or crashing

**Solution**: Check the logs to see what's wrong.
```bash
cd ~/Documents/scalp_bot
docker-compose logs -f
```

Press `Ctrl + C` to stop viewing logs.

Look for error messages and search for them online, or contact support.

### Can't see any trades happening

**Possible reasons**:
1. **Risk limits hit**: Check if you've exceeded daily loss or max trades
2. **Outside trading hours**: Bot avoids first/last 30 minutes of market
3. **Entry conditions not met**: Price hasn't dropped enough to trigger entry
4. **Bot not started**: Make sure you clicked "Start Bot" in the dashboard

### How to completely reset and start fresh

```bash
cd ~/Documents/scalp_bot
docker-compose down
rm -rf data/  # This deletes all saved data
docker-compose up -d
```

---

## Daily Usage

Once everything is set up, daily usage is simple:

### Starting Your Trading Day

1. **Open Terminal**
   ```bash
   cd ~/Documents/scalp_bot
   docker-compose up -d
   ```

2. **Open Dashboard**
   - Go to http://localhost:8000

3. **Review Settings**
   - Click "Configure"
   - Make sure everything looks right
   - Click "Cancel" (unless you want to change something)

4. **Start Trading**
   - Click "Start Bot"
   - Monitor the dashboard for the first 30 minutes

### During the Day

- **Check the dashboard periodically** to monitor P&L and positions
- **Don't panic** if you see small losses - that's normal with scalping
- **Watch for the daily loss limit** - bot will auto-stop if hit
- **Be ready to manually stop** if something seems wrong

### End of Day

The bot will automatically close all positions 30 minutes before market close (by default).

**To manually stop**:
1. Click "Stop Bot" in the dashboard
2. If you have open positions, click "Close All Positions" first

**To shut down completely**:
```bash
cd ~/Documents/scalp_bot
docker-compose down
```

### Checking Results

- **Daily P&L**: Shows on the dashboard
- **Trade History**: Check the `data/` folder (coming soon - database feature)
- **Logs**:
  ```bash
  cd ~/Documents/scalp_bot
  docker-compose logs -f
  ```

---

## Getting Updates

When there are new updates to the bot:

```bash
cd ~/Documents/scalp_bot
git pull
docker-compose down
docker-compose up -d --build
```

---

## Important Safety Reminders

1. ✅ **Always start in dry-run mode** when testing new strategies
2. ✅ **Use a separate account** for bot trading
3. ✅ **Start with small position sizes** (5-10% of account)
4. ✅ **Set conservative daily loss limits** (3-5% max)
5. ✅ **Monitor actively** for the first few weeks
6. ✅ **Never risk money you can't afford to lose**
7. ✅ **This is not financial advice** - you're responsible for all trading decisions

---

## Getting Help

If you're stuck:

1. **Check this guide again** - most issues are covered in Troubleshooting
2. **Check the logs** - they often tell you what's wrong
3. **Search online** for error messages
4. **Contact support** (see GitHub repository for issues)

---

## Quick Reference Commands

Save these for easy access:

```bash
# Go to bot folder
cd ~/Documents/scalp_bot

# Start the bot
docker-compose up -d

# Stop the bot
docker-compose down

# View logs
docker-compose logs -f

# Restart the bot
docker-compose restart

# Check if bot is running
docker-compose ps

# Update bot to latest version
git pull && docker-compose up -d --build
```

---

## Appendix: Understanding the Dashboard

### Status Section
- **Bot Status**: Green "Running" or Red "Stopped"
- **Trading Mode**: "DRY RUN" (safe) or "LIVE" (real money)
- **Symbols**: Which stocks it's watching (e.g., TSLA)

### Account Section
- **Balance**: Current account balance
- **Daily P&L**: Profit/Loss for today (green = profit, red = loss)
- **Daily Trades**: Number of trades executed today

### Performance Section
- **Open Positions**: How many stocks you currently own
- **Total Wins**: Number of profitable trades (all time)
- **Total Losses**: Number of losing trades (all time)

### Controls
- **Start Bot**: Begin trading
- **Stop Bot**: Stop trading (doesn't close positions)
- **Configure**: Change settings
- **Close All Positions**: Immediately sell everything you own

### Positions Table
Shows each open position with:
- Symbol (e.g., TSLA)
- Quantity (number of shares)
- Entry Price (what you paid)
- Current Price (current market price)
- Unrealized P&L (profit/loss if you sold now)
- P&L % (percentage profit/loss)

---

**You're all set!** Remember to test thoroughly in dry-run mode before risking real money. Good luck! 🚀

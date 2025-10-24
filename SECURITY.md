# Security Policy

## Overview

This trading bot handles sensitive financial data and API credentials. Please follow these security best practices.

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please email the maintainer directly rather than opening a public issue. We will respond as quickly as possible.

## Best Practices

### 1. API Credentials

**NEVER commit credentials to Git:**
- ✅ Use `.env` files (already in `.gitignore`)
- ✅ Use environment variables
- ✅ Keep `tokens.json` in the `data/` folder (gitignored)
- ❌ Never put credentials directly in code
- ❌ Never commit `.env` or `tokens.json`
- ❌ Never share credentials in screenshots or logs

**Schwab API Credentials:**
- Store App Key and App Secret securely
- Treat them like passwords
- Rotate them if compromised
- Don't share them with anyone

### 2. Network Security

**Dashboard Access:**
- The bot runs on `0.0.0.0:8000` (accessible from network) by default
- For local use only, change to `127.0.0.1:8000` in `docker-compose.yml`
- No authentication is built in - add reverse proxy with auth if exposing to internet
- Never expose directly to the internet without HTTPS and authentication

**Firewall:**
- Keep your Mac's firewall enabled
- Only allow necessary incoming connections
- Consider using a VPN if accessing remotely

### 3. Docker Security

**Container Isolation:**
- Bot runs in isolated Docker container
- Limited access to host system
- Data persisted only in mounted `data/` volume

**Updates:**
- Keep Docker Desktop updated
- Regularly pull updated bot images: `docker-compose pull`
- Review changes before updating: `git diff`

### 4. Data Protection

**Trade History:**
- Trade history stored in `data/` folder
- Contains sensitive financial information
- Back up securely if needed
- Don't share publicly

**Logs:**
- Logs may contain account numbers and trade details
- Review before sharing for debugging
- Redact sensitive information

### 5. Account Security

**Schwab Account:**
- Use strong, unique password
- Enable two-factor authentication (2FA)
- Monitor account regularly for unauthorized access
- Use a separate account for bot trading (not your main account)
- Start with limited funds

**Pattern Day Trading:**
- Be aware of PDT rules (need $25k for unlimited day trades)
- Violating PDT rules can restrict your account

### 6. Code Security

**Dependencies:**
- Dependencies are pinned in `pyproject.toml`
- Review updates before applying
- Use `uv` for reproducible builds
- Check for known vulnerabilities: `pip-audit` (optional)

**Code Review:**
- Review code before running, especially updates
- Don't run untrusted code
- Check for malicious changes in pull requests

### 7. Risk Management

**Financial Security:**
- Never trade with money you can't afford to lose
- Set conservative daily loss limits
- Use a separate test account
- Start with small position sizes
- Have an emergency stop plan

**Monitoring:**
- Monitor bot actively, especially at first
- Check for unexpected behavior
- Review trade executions regularly
- Keep Schwab's customer service number handy: 1-800-435-4000

## What's Protected

### ✅ Gitignored (Safe)

These files will NOT be committed to GitHub:
- `.env` - Environment variables with credentials
- `data/` - Trade history, database, tokens
- `tokens.json` - Schwab API tokens
- `__pycache__/` - Python bytecode
- `.venv/` - Virtual environment

### ⚠️ Committed (Public)

These files WILL be on GitHub:
- All source code
- Documentation
- Docker configuration
- Example config (`config.example.json` - no real credentials)
- `.env.example` - Template only, no real values

## Emergency Procedures

### If Credentials Are Compromised

1. **Immediately** stop the bot: `docker-compose down`
2. Go to https://developer.schwab.com/
3. Delete the compromised app credentials
4. Create new app with new credentials
5. Update your `.env` file with new credentials
6. Change your Schwab password
7. Enable 2FA if not already enabled
8. Review recent trades for unauthorized activity

### If Unauthorized Trades Detected

1. Click "Stop Bot" in dashboard immediately
2. Click "Close All Positions" if needed
3. Call Schwab: 1-800-435-4000
4. Review logs: `docker-compose logs -f`
5. Check `data/` folder for trade history
6. Report to Schwab's fraud department if needed

### If Bot Is Compromised

1. Stop the bot: `docker-compose down`
2. Remove the container: `docker-compose rm`
3. Delete the `data/` folder if it may contain malicious code
4. Re-download from official GitHub repository
5. Review code changes carefully
6. Rebuild: `docker-compose build --no-cache`
7. Change all credentials before restarting

## Compliance

### Regulatory Considerations

- This bot is for personal use only
- Understand your local trading regulations
- Keep records of all trades for tax purposes
- Consult a tax professional about trading income/losses
- Be aware of wash sale rules and other tax implications

### Terms of Service

- Review Charles Schwab's Terms of Service
- Ensure automated trading is allowed
- Understand your responsibilities as an account holder
- Don't violate exchange rules or regulations

## Data Privacy

**What Data Is Collected:**
- Trade executions (buy/sell, price, quantity, time)
- Account balance (for position sizing)
- Bot configuration and settings
- Performance statistics

**What Data Is NOT Collected:**
- Personal information beyond what you provide
- Data is stored locally only (not sent to external servers)
- No telemetry or analytics sent to developers
- No tracking or third-party services

**Your Responsibility:**
- You own all your data
- You're responsible for backing it up
- You're responsible for securing it
- You're responsible for deleting it when done

## Security Checklist

Before going live, ensure:

- [ ] `.gitignore` includes all sensitive files
- [ ] API credentials stored in `.env` (not in code)
- [ ] `.env` file never committed to Git
- [ ] `tokens.json` in `data/` folder (gitignored)
- [ ] Schwab account has 2FA enabled
- [ ] Using a separate account for bot trading
- [ ] Docker Desktop is updated
- [ ] Mac firewall is enabled
- [ ] Bot dashboard not exposed to internet
- [ ] You understand how to stop the bot in emergency
- [ ] You have Schwab's phone number saved

## Contact

For security concerns, contact the repository maintainer directly.

---

**Remember: Security is your responsibility. Stay vigilant and trade safely!**

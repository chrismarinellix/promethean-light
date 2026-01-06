# Promethean Light Laptop Server - Quick Setup

## 🚀 5-Minute Setup

### Step 1: Configure for 24/7 Operation (2 minutes)
```batch
CONFIGURE_24_7_LAPTOP.bat
```

This will:
- Disable sleep/hibernate when plugged in
- Set high performance power plan
- Optimize for continuous operation

**Manual step:** Set lid close action to "Do nothing" in Power Options

---

### Step 2: Enable Network Access (1 minute)
```batch
ENABLE_NETWORK_ACCESS.bat
```

This will:
- Configure API to listen on network (0.0.0.0)
- Add Windows Firewall rule for port 8000
- Show your IP address and hostname for team access

**Requires:** Administrator privileges for firewall configuration

---

### Step 3: Install Auto-Start (1 minute)
```batch
INSTALL_AUTO_START.bat
```

This will:
- Create Windows Task Scheduler task
- Auto-start on boot (even if not logged in)
- Auto-restart on failure

---

### Step 4: Restart Promethean Light (1 minute)
```batch
START.bat
```

Server will now be accessible to your team!

---

### Step 5: Test Network Access
```batch
TEST_NETWORK_ACCESS.bat
```

Verifies:
- API server is running
- Network access is working
- Shows URLs for team access

---

## 📊 Performance Comparison

| Location | Latency | Read Speed | Small Files | Recommendation |
|----------|---------|------------|-------------|----------------|
| **C: Drive (Local)** | 0.3 ms | 2,329 MB/s | 563.9 files/s | ✓ PERFECT |
| V: Drive (Network) | 178.8 ms | 8.48 MB/s | 8.4 files/s | ✗ TOO SLOW |

**Your local C: drive is 600x faster than the network drive!**

---

## 📋 What Your Team Gets

Once set up, your team can access:

### Web Browser
```
http://YOUR-IP:8000/search?q=india+staff
http://YOUR-IP:8000/stats
http://YOUR-IP:8000/recent?limit=20
```

### PowerShell
```powershell
$results = Invoke-RestMethod "http://YOUR-IP:8000/search?q=project+pipeline"
$results.documents | Format-Table
```

### Python
```python
import requests
results = requests.get("http://YOUR-IP:8000/search?q=india").json()
```

### Excel Power Query
Direct data import from API into spreadsheets

---

## 🔧 Maintenance Commands

```batch
# Enable network access
ENABLE_NETWORK_ACCESS.bat

# Disable network access (localhost only)
DISABLE_NETWORK_ACCESS.bat

# Configure laptop for 24/7
CONFIGURE_24_7_LAPTOP.bat

# Install auto-start
INSTALL_AUTO_START.bat

# Remove auto-start
UNINSTALL_AUTO_START.bat

# Test network access
TEST_NETWORK_ACCESS.bat

# Start server
START.bat

# Restart daemon
RESTART_DAEMON.bat (if exists)
```

---

## 📱 Server Status Checks

### Is the server running?
```batch
netstat -an | findstr :8000
```

### What's the API doing?
```batch
curl http://localhost:8000/stats
```

### Check system resources
Open Task Manager → Performance tab
- CPU: Should be 5-15% when idle
- Memory: ~500MB-2GB depending on database size
- Network: Minimal when not in use

---

## 🔐 Security Checklist

- ✓ Network access restricted to company LAN
- ✓ Data encrypted at rest (ChaCha20-Poly1305)
- ✗ No authentication (internal team only - ADD THIS IF NEEDED)
- ✗ No HTTPS (HTTP only - UPGRADE IF NEEDED)

**For production with external access, add:**
1. API key authentication
2. HTTPS with SSL certificate
3. Rate limiting
4. Access logs and monitoring

---

## 💾 Backup Strategy

Already configured! Your system has:

```batch
# Manual backup
BACKUP_NOW.bat

# Install automated daily backups
INSTALL_BACKUP_SCHEDULE.bat
```

**Backup locations:**
- Local: `C:\Code\Promethian Light\backups\`
- Network: `V:\mel_energy_office\Business Dev\Data Base Backup\`

---

## ⚡ Performance Expectations

Based on local C: drive testing:

- **Search queries**: < 100ms
- **Concurrent users**: 5-10 optimal, up to 20 acceptable
- **Uptime**: 24/7 (assuming laptop stays on)
- **Data freshness**: Real-time (emails: 1 min, files: instant)

---

## 📚 Documentation

- `LAPTOP_SERVER_SETUP.md` - Comprehensive setup guide
- `TEAM_ACCESS_GUIDE.md` - Share with team members
- `QUICK_SETUP.md` - This file (quick reference)

---

## 🆘 Troubleshooting

### Team can't connect

1. Is server running? `netstat -an | findstr :8000`
2. Is firewall configured? `ENABLE_NETWORK_ACCESS.bat`
3. Test locally first: `curl http://localhost:8000/stats`
4. Check IP hasn't changed: `ipconfig`

### Server stopped

1. Check logs: `type %USERPROFILE%\.mydata\daemon.log`
2. Restart: `START.bat`
3. If auto-start not working: `INSTALL_AUTO_START.bat`

### Laptop going to sleep

1. Re-run: `CONFIGURE_24_7_LAPTOP.bat`
2. Check lid close action in Power Options
3. Ensure plugged into AC power

### Performance degrading

1. Restart daemon: Kill python processes, run `START.bat`
2. Check disk space: `dir C:\`
3. Monitor Task Manager for resource hogs

---

## 📞 Next Steps

1. **Now**: Run the 5-minute setup above
2. **Today**: Share `TEAM_ACCESS_GUIDE.md` with team
3. **This Week**: Monitor performance and team feedback
4. **Monthly**: Review backup integrity

---

## 💡 Pro Tips

1. **Keep laptop elevated** on a stand for better cooling
2. **Use a cooling pad** for prolonged 24/7 operation
3. **Disable Windows Update auto-restart** to prevent downtime
4. **Set a static IP** from your router/IT for consistency
5. **Monitor temperature** periodically (especially in summer)
6. **Keep laptop plugged in** at all times
7. **Test backups monthly** to ensure recoverability

---

## 🎯 Success Criteria

You'll know it's working when:
- ✓ Server auto-starts on boot
- ✓ Team can search and get results
- ✓ Emails are ingested automatically
- ✓ No sleep/hibernate interruptions
- ✓ Backups running daily

---

## 📈 Future Enhancements

As usage grows, consider:

1. **Authentication**: Add API keys for security
2. **HTTPS**: SSL certificate for encryption
3. **Rate limiting**: Prevent abuse
4. **Caching layer**: Redis for faster responses
5. **Load balancing**: If users > 20
6. **Dedicated server**: If laptop becomes bottleneck
7. **Cloud deployment**: For remote team access

---

**Setup Time**: 5-10 minutes
**Maintenance**: < 5 minutes/week
**Cost**: $0 (using existing hardware)

**Your C: drive performance is excellent - this will work great!**

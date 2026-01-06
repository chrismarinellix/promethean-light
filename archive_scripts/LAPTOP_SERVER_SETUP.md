# Laptop Server Setup Guide for Promethean Light

## Performance Comparison

### Local C: Drive (EXCELLENT)
- Latency: 0.3 ms (600x faster than network)
- Read Speed: 2,329 MB/s
- Small File Serving: 563.9 files/s
- **Status: IDEAL for team server**

### Network V: Drive (POOR)
- Latency: 178.8 ms
- Read Speed: 8.48 MB/s
- Small File Serving: 8.4 files/s
- **Status: Too slow for live server**

## Laptop as Server - Overview

Your laptop can serve Promethean Light to your team on the local network. Here's what you need:

### Pros
- Blazing fast performance (local SSD)
- No cloud costs
- Full control over data
- Works on company network
- SQLite performs excellently

### Cons
- Laptop must stay on 24/7
- Battery/power management needed
- Your IP address might change (solution below)
- Firewall configuration required

### Recommended Setup
- **Host**: Your laptop (C:\Code\Promethian Light)
- **Access**: Team connects via http://your-laptop-ip:5000
- **Data**: Local SQLite + Qdrant (already configured)
- **Uptime**: Run as Windows service or startup script

---

## Setup Steps

### 1. Configure Promethean Light for Network Access

Your FastAPI server needs to listen on your network interface (not just localhost).

**Check current API configuration:**
```python
# In mydata/api.py, the uvicorn.run should bind to 0.0.0.0
# This allows external connections
```

### 2. Find Your Laptop's IP Address

Run this to find your local network IP:
```bash
ipconfig
```

Look for "IPv4 Address" under your active network adapter (e.g., 192.168.1.100).

### 3. Configure Windows Firewall

Allow incoming connections on port 5000:

```powershell
# Run as Administrator
netsh advfirewall firewall add rule name="Promethean Light API" dir=in action=allow protocol=TCP localport=5000
```

### 4. Keep Laptop Running 24/7

**Power Settings:**
```powershell
# Prevent sleep when lid closed (laptop on AC power)
powercfg /change monitor-timeout-ac 0
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```

**Recommended:**
- Keep laptop plugged in
- Use a cooling pad (prolonged use generates heat)
- Set "When I close the lid: Do nothing" in Power Options
- Enable "Turn on fast startup" for quicker recovery from issues

### 5. Auto-Start on Boot

Two options:

#### Option A: Windows Task Scheduler (Recommended)
- Runs even if not logged in
- Survives reboots
- No user interaction needed

#### Option B: Startup Folder (Simple)
- Only runs when you log in
- Easier to set up
- Good for testing

---

## Network Access for Your Team

### Option 1: Direct IP Access (Simplest)

Team members access via:
```
http://192.168.1.100:5000
```

**Setup:**
1. Find your IP address: `ipconfig`
2. Share IP with team
3. They bookmark: `http://YOUR-IP:5000`

**Limitations:**
- IP might change if you disconnect/reconnect
- Only works on same network (office WiFi/LAN)

### Option 2: Static IP Address (Better)

Request a static IP from IT department:
- IP won't change
- More reliable
- Team can bookmark permanent address

### Option 3: Hostname Access (Best)

Use your computer name instead of IP:
```
http://CHRIS-LAPTOP:5000
```

**Find your hostname:**
```bash
hostname
```

**Advantages:**
- Works even if IP changes
- Easier to remember
- More professional

### Option 4: DNS Name (Professional)

If your IT department manages DNS:
- Request: `promethean.mel.local` → your laptop IP
- Team accesses: `http://promethean.mel.local:5000`
- Most professional solution

---

## Security Considerations

### 1. Authentication (Currently Missing)

Promethean Light API has no authentication. Anyone on the network can access it.

**Options:**
- Add API key authentication
- Use VPN (if company has one)
- Configure network firewall to restrict access
- Add basic HTTP authentication

### 2. HTTPS (Optional but Recommended)

For encrypted connections:
- Generate self-signed certificate
- Configure FastAPI to use SSL
- Team accesses `https://` instead of `http://`

### 3. Network Segmentation

Work with IT to:
- Ensure laptop is on trusted network
- Block external access (only internal team)
- Configure appropriate network policies

---

## Monitoring and Maintenance

### 1. Check Server Status

```bash
# See if API is running
netstat -an | findstr :5000

# Check process
tasklist | findstr python
```

### 2. View Logs

```bash
# Daemon logs
type %USERPROFILE%\.mydata\daemon.log

# API logs (if configured)
type C:\Code\Promethian Light\logs\api.log
```

### 3. Restart Server

```bash
# Kill existing process
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Promethean*"

# Restart
START.bat
```

### 4. Monitor Performance

```bash
# Check system resources
Task Manager → Performance
- CPU usage (should be low when idle)
- Memory (Promethean Light uses ~500MB-2GB)
- Disk activity
```

---

## Team Access Instructions

### For Team Members

**Web Browser Access:**
```
1. Open browser
2. Go to: http://LAPTOP-IP:5000
3. Bookmark for easy access
```

**API Access (for developers):**
```bash
# Search
curl http://LAPTOP-IP:5000/search?q=india+staff

# Recent documents
curl http://LAPTOP-IP:5000/recent?limit=10

# Export data
curl http://LAPTOP-IP:5000/export?query=pipeline
```

**Python Client:**
```python
import requests

# Search Promethean Light
response = requests.get("http://LAPTOP-IP:5000/search",
                       params={"q": "project pipeline"})
results = response.json()

for doc in results["documents"]:
    print(doc["title"], doc["snippet"])
```

---

## Troubleshooting

### Problem: Team can't connect

**Solutions:**
1. Check firewall: `netsh advfirewall firewall show rule name="Promethean Light API"`
2. Verify server is running: `netstat -an | findstr :5000`
3. Test locally first: Open `http://localhost:5000` on your laptop
4. Ping test: Team member runs `ping YOUR-IP`
5. Check same network: Ensure team is on same WiFi/LAN

### Problem: IP address keeps changing

**Solutions:**
1. Use hostname instead of IP
2. Request static IP from IT
3. Update team when IP changes
4. Set up DNS entry

### Problem: Laptop goes to sleep

**Solutions:**
1. Check power settings: `powercfg /query`
2. Ensure "Do nothing" when lid closed
3. Disable sleep/hibernate timers
4. Keep laptop plugged in

### Problem: Performance degrades over time

**Solutions:**
1. Restart daemon weekly: `RESTART_DAEMON.bat`
2. Clear cache: Delete `%USERPROFILE%\.mydata\cache\*`
3. Check disk space: `dir C:\ `
4. Monitor RAM usage in Task Manager

### Problem: Server crashes/stops

**Solutions:**
1. Check logs for errors
2. Set up auto-restart script
3. Use Task Scheduler with "Restart on failure"
4. Monitor with heartbeat service

---

## Advanced: VPN Access

If team works remotely, set up VPN:

### Windows Built-in VPN
1. Open Settings → Network → VPN
2. Add VPN connection (Point-to-Point Tunneling Protocol)
3. Use your laptop as VPN server
4. Team connects via VPN, then accesses Promethean Light

### Third-Party Solutions
- **ZeroTier**: Free, easy P2P VPN
- **Tailscale**: Modern, secure mesh VPN
- **Hamachi**: Simple VPN for small teams
- **WireGuard**: Fast, secure VPN protocol

---

## Cost Analysis

### Laptop Server (Your Setup)
- **Hardware**: $0 (using existing laptop)
- **Software**: $0 (all open source)
- **Network**: $0 (company network)
- **Total**: **FREE**

### Cloud Alternative
- **AWS EC2 t3.medium**: ~$30/month
- **Azure VM B2s**: ~$35/month
- **DigitalOcean Droplet**: ~$24/month
- **Data transfer**: ~$5-20/month
- **Total**: **$30-60/month = $360-720/year**

**Laptop server saves ~$400-700/year**

---

## Backup Considerations

Since your laptop is the server, backups are critical:

### Automated Backups
```bash
# Already configured!
BACKUP_NOW.bat  # Manual backup
INSTALL_BACKUP_SCHEDULE.bat  # Automated daily backups
```

**Backup locations:**
- Local: `C:\Code\Promethian Light\backups\`
- Network: `V:\mel_energy_office\Business Dev\Data Base Backup\`

### Disaster Recovery

If laptop fails:
1. Restore from latest backup
2. Install on new machine
3. Run `START.bat`
4. Update IP address with team

---

## Performance Expectations

Based on local drive testing:

### Concurrent Users
- **1-5 users**: Excellent performance
- **6-10 users**: Good performance
- **11-20 users**: Acceptable (depends on queries)
- **20+ users**: Consider dedicated server

### Response Times
- Simple search: <100ms
- Complex queries: 100-500ms
- Large exports: 1-5 seconds
- Email ingestion: Background process (no impact)

### Resource Usage
- **CPU**: 5-15% idle, 30-60% during queries
- **RAM**: 500MB-2GB (depends on database size)
- **Disk**: Minimal (mostly reads)
- **Network**: <1 Mbps for typical usage

---

## Upgrade Path

If laptop server becomes insufficient:

### Next Steps
1. **Dedicated desktop**: More reliable than laptop
2. **Small server**: HP ProLiant, Dell PowerEdge
3. **NUC/Mini PC**: Intel NUC, low power consumption
4. **Cloud hosting**: AWS/Azure for remote teams

---

## Summary

**YES, your laptop can absolutely be a server!**

### Quick Setup Checklist
- [ ] Configure API to bind to 0.0.0.0 (network interface)
- [ ] Find your IP address (`ipconfig`)
- [ ] Open firewall port 5000
- [ ] Configure power settings (no sleep)
- [ ] Set up auto-start on boot
- [ ] Share IP/hostname with team
- [ ] Test access from team member's computer
- [ ] Set up automated backups
- [ ] Monitor performance

**Expected setup time: 30-60 minutes**

**Your C: drive performance is excellent - this will work great!**

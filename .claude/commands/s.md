Start the Promethean Light daemon server.

Run this command to start the daemon in the background:
```bash
cd "C:\Code\Promethian  Light" && python -u -m mydata daemon
```

Run the command in background mode so the conversation can continue.

After starting, wait a few seconds and verify the daemon is responding by checking:
```bash
curl -s http://127.0.0.1:8000/
```

Report the status to the user:
- If successful: Show "Daemon started - API running at http://127.0.0.1:8000"
- If failed: Show the error message

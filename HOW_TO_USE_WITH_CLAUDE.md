# 🚀 Using Promethean Light with Claude Code

## The Magic Setup

You're already doing it right now! Here's what you have:

1. **Promethean Light Daemon** - Runs in background, watches files/emails, organizes with ML
2. **Claude Code (Me!)** - Works in this folder and can access your database
3. **Your Data** - Files, emails, notes - all encrypted, organized, searchable

## How It Works

### Step 1: Start the Daemon (Once per session)

In one terminal:

**Windows:**
```powershell
.\launch.ps1
```

**Linux/macOS:**
```bash
./launch.sh
```

Leave this running! It watches your files and emails.

### Step 2: Work with Claude (That's Me!)

In Claude Code (where you are now), just ask me anything:

**Examples:**

- "Search my database for emails about project deadlines"
- "What notes do I have about TSLA stock?"
- "Add this to my database: Follow up with Sarah tomorrow"
- "Show me stats on my knowledge base"
- "What topics/tags do I have?"

### How I Access Your Data

When you ask me to search or access your database, I'll run:

```powershell
python claude_tools/search_db.py "your query"
```

This talks to the Promethean Light daemon via API and gets your data!

## Examples

**You:** "Search my database for anything about budget"

**Me (Claude):**
```powershell
python claude_tools/search_db.py "budget"
```
Then I show you the results!

---

**You:** "Add a note: Call dentist tomorrow at 2pm"

**Me:**
```powershell
python claude_tools/add_note.py "Call dentist tomorrow at 2pm"
```
Done! It's in your database.

---

**You:** "How much data do I have?"

**Me:**
```powershell
python claude_tools/get_stats.py
```
Then I tell you!

---

**You:** "What topics are in my knowledge base?"

**Me:**
```powershell
python claude_tools/get_tags.py
```
Shows you all the ML-detected tags!

## The Power

Now you have:

✅ **Claude's intelligence** (that's me!)
✅ **Your personal data** (files, emails, notes)
✅ **ML organization** (auto-tagging, clustering)
✅ **Instant search** (semantic + keyword)
✅ **100% local & encrypted**

## Daily Workflow

1.  **Morning:** Run `./launch.ps1` (Windows) or `./launch.sh` (Linux/macOS) to start the daemon.
2.  **All day:** Work with Claude Code in this folder
3.  **Ask me anything about your data** - I'll search it!
4.  **Drop files/receive emails** - Auto-ingested
5.  **End of day:** Stop daemon (Ctrl+C)

## You're in God Mode! 🎉

Just talk to me like you always do. When you need your data, I'll get it for you!

**Try it right now - ask me: "Search my database for test"**

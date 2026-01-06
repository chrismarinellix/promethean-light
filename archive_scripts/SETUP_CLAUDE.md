# How to Use Promethean Light with Claude Code

## What This Does

When you `cd` into this folder and talk to Claude Code, Claude will have access to your entire Promethean Light database! You can ask Claude to:

- Search your knowledge base
- Find information from your files and emails
- Add new notes
- See statistics about your data

## Setup (One-Time)

### 1. Make sure the daemon is running

```powershell
START.bat
```

Leave this running in the background.

### 2. Start Claude Code in this folder

```powershell
cd "C:\Code\Promethian  Light"
# Then start Claude Code (however you normally do)
```

## How to Use

Just talk to Claude naturally! Claude now has these powers:

### Search Your Knowledge Base

**You:** "Claude, search my knowledge base for anything about project deadlines"

**Claude will:** Use the `promethean_search` tool to find relevant information from your ingested files and emails.

### Add Notes

**You:** "Claude, add a note: Need to follow up with Sarah about Q4 budget"

**Claude will:** Use the `promethean_add_note` tool to save it to your database.

### Check Stats

**You:** "Claude, how much data do I have in Promethean Light?"

**Claude will:** Use the `promethean_stats` tool to show you document counts, tags, etc.

### See Topics

**You:** "Claude, what topics are in my knowledge base?"

**Claude will:** Use the `promethean_tags` tool to show all auto-detected tags.

## Examples

```
You: "Search my database for emails about the budget"
Claude: *searches and shows you relevant emails*

You: "What were my notes about TSLA stock?"
Claude: *finds and summarizes your TSLA notes*

You: "Add this to my database: Remember to review code before Friday"
Claude: *saves it and confirms*

You: "Show me stats on my knowledge base"
Claude: *displays total documents, chunks, tags, etc.*
```

## The Magic

Claude Code will automatically:
1. Detect you're in the Promethean Light folder
2. Load the MCP server
3. Have access to search, add, and query your data
4. Use it naturally in conversation!

**You get the power of Claude + your perfectly organized, ML-curated knowledge base!**

## Troubleshooting

**If Claude says the daemon isn't running:**

```powershell
START.bat
```

**If Claude doesn't seem to have access:**

Make sure `.clauderc` exists in this folder with the MCP server configuration.

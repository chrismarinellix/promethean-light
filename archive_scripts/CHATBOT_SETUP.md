# Chatbot Setup Guide

## Overview

The Promethean Light chatbot uses **RAG (Retrieval-Augmented Generation)** to answer questions about your data. It combines:
- **Vector search** - Finds semantically similar documents
- **Hybrid search** - Combines vector + BM25 keyword matching
- **OpenAI GPT** - Generates natural language responses from retrieved context

**Important:** Chat conversations are stored in the **default database** and retrieve context from whichever database you're querying. The chatbot never mixes chat logs with your private document data.

---

## Setup Steps

### 1. Install Dependencies

```bash
pip install -e .
```

This will install the `openai` package along with other dependencies.

### 2. Start the Daemon

```bash
mydata daemon
```

The daemon must be running for the chatbot to work.

### 3. Add Your OpenAI API Key

The API key is **encrypted** and stored securely in the default database, accessible across all databases:

```bash
mydata api-key openai YOUR_API_KEY_HERE
```

**Example:**
```bash
mydata api-key openai sk-proj-abc123...
```

You can verify it was stored:
```bash
mydata api-keys
```

---

## Usage

### Single Question

Ask a one-time question:

```bash
mydata chat "What are the retention bonuses?"
```

**Output:**
```
Response:
Based on your documents, retention bonuses expire in Feb 2026 and Aug 2026...

Conversation ID: 1
Sources: 5 chunks | Tokens: 342
```

### Interactive Chat Mode

Start an interactive conversation:

```bash
mydata chat --interactive
```

### Continue a Conversation

```bash
mydata chat -c 1 "Who has the highest bonus?"
```

### List All Conversations

```bash
mydata conversations
```

---

## Using with Different Databases

The chatbot searches whichever database you specify with `--db`:

```bash
# Chat with default (private) database
mydata chat "What are the project timelines?"

# Chat with a project database
mydata --db=project_9002 chat "What are the deliverables?"
```

---

## API Endpoints

For web/app integration:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send chat message with RAG |
| `/chat/conversations` | GET | List conversations |
| `/chat/conversations/{id}` | GET | Get conversation history |
| `/chat/conversations/{id}` | DELETE | Delete conversation |
| `/api-keys` | POST | Add API key |
| `/api-keys` | GET | List API keys |

**Example API call:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the retention bonuses?", "model": "gpt-4o-mini"}'
```

---

## Configuration Options

### Model Selection

Use different OpenAI models:

```bash
mydata chat -m gpt-4o "Complex question requiring more reasoning"
mydata chat -m gpt-4o-mini "Quick simple question"
```

### Context Chunks

The chatbot retrieves 5 document chunks by default. Adjust via API if needed.

---

## Troubleshooting

### "Chatbot not available"

1. Make sure daemon is running: `mydata daemon`
2. Check API key is configured: `mydata api-keys`
3. Restart daemon after adding API key

### "OpenAI API error"

1. Verify API key is valid
2. Check you have API credits
3. Ensure network connectivity

### No relevant results

1. Make sure documents are ingested
2. Try more specific queries
3. Check `mydata stats` for document count

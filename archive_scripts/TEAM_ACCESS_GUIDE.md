# Promethean Light - Team Access Guide

## Quick Start for Team Members

Promethean Light is now available as a shared knowledge base server. You can search emails, documents, and get instant answers.

### Access URLs

**Primary (IP Address):**
```
http://[YOUR-LAPTOP-IP]:8000
```

**Alternative (Hostname):**
```
http://[YOUR-LAPTOP-NAME]:8000
```

*Ask Chris for the specific IP/hostname*

---

## Web Browser Access

### 1. Search Documents

Open in your browser:
```
http://[SERVER]:8000/search?q=your+search+query
```

**Examples:**
- Search for India staff: `http://[SERVER]:8000/search?q=india+staff`
- Search project pipeline: `http://[SERVER]:8000/search?q=project+pipeline`
- Search retention bonuses: `http://[SERVER]:8000/search?q=retention+bonuses`

### 2. View Statistics

```
http://[SERVER]:8000/stats
```

Shows:
- Total documents
- Total chunks
- Tags
- Topic clusters

### 3. Recent Documents

```
http://[SERVER]:8000/recent?limit=20
```

Get the last 20 documents added to the system.

### 4. Browse Tags

```
http://[SERVER]:8000/tags
```

See all automatically generated tags.

### 5. View Topic Clusters

```
http://[SERVER]:8000/clusters
```

Browse documents organized by topic.

---

## API Access (for Developers)

### Using PowerShell

```powershell
# Search
$response = Invoke-RestMethod -Uri "http://[SERVER]:8000/search?q=project+pipeline"
$response

# Get stats
$stats = Invoke-RestMethod -Uri "http://[SERVER]:8000/stats"
Write-Host "Total documents: $($stats.total_documents)"

# Recent documents
$recent = Invoke-RestMethod -Uri "http://[SERVER]:8000/recent?limit=10"
$recent.documents | Format-Table title, source, created_at
```

### Using cURL

```bash
# Search
curl "http://[SERVER]:8000/search?q=india+staff"

# Stats
curl "http://[SERVER]:8000/stats"

# Recent
curl "http://[SERVER]:8000/recent?limit=10"
```

### Using Python

```python
import requests

SERVER = "http://[SERVER]:8000"

# Search function
def search(query, limit=10):
    response = requests.get(f"{SERVER}/search",
                          params={"q": query, "limit": limit})
    return response.json()

# Get stats
def get_stats():
    response = requests.get(f"{SERVER}/stats")
    return response.json()

# Recent documents
def get_recent(limit=10):
    response = requests.get(f"{SERVER}/recent",
                          params={"limit": limit})
    return response.json()

# Example usage
results = search("india staff retention")
for doc in results["documents"]:
    print(f"{doc['title']}")
    print(f"  Source: {doc['source']}")
    print(f"  Score: {doc['score']:.2f}")
    print()
```

### Using JavaScript (Node.js)

```javascript
const fetch = require('node-fetch');

const SERVER = 'http://[SERVER]:8000';

// Search
async function search(query, limit = 10) {
    const url = `${SERVER}/search?q=${encodeURIComponent(query)}&limit=${limit}`;
    const response = await fetch(url);
    return await response.json();
}

// Stats
async function getStats() {
    const response = await fetch(`${SERVER}/stats`);
    return await response.json();
}

// Example
search('project pipeline').then(results => {
    console.log(`Found ${results.documents.length} documents`);
    results.documents.forEach(doc => {
        console.log(`- ${doc.title} (score: ${doc.score})`);
    });
});
```

---

## Excel / Power Query Integration

You can pull Promethean Light data directly into Excel:

1. Open Excel
2. Data → Get Data → From Web
3. Enter URL: `http://[SERVER]:8000/search?q=your+query`
4. Load data into spreadsheet

**Example Power Query M code:**
```m
let
    Source = Json.Document(Web.Contents("http://[SERVER]:8000/search?q=india+staff&limit=50")),
    Documents = Source[documents],
    ToTable = Table.FromList(Documents, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    Expanded = Table.ExpandRecordColumn(ToTable, "Column1", {"title", "source", "score", "created_at"})
in
    Expanded
```

---

## API Endpoints Reference

### GET /search
Search documents using hybrid semantic + keyword search.

**Parameters:**
- `q` (required): Search query
- `limit` (optional): Number of results (default: 10, max: 100)
- `tag` (optional): Filter by tag

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_123",
      "title": "Document title",
      "snippet": "Relevant excerpt...",
      "source": "email",
      "score": 0.85,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 42,
  "query": "india staff"
}
```

### GET /stats
Get system statistics.

**Response:**
```json
{
  "total_documents": 1234,
  "total_chunks": 5678,
  "total_tags": 89,
  "total_clusters": 12
}
```

### GET /recent
Get recently added documents.

**Parameters:**
- `limit` (optional): Number of documents (default: 10, max: 100)

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_456",
      "title": "Recent document",
      "source": "outlook",
      "created_at": "2024-01-20T14:22:00"
    }
  ]
}
```

### GET /tags
Get all tags with document counts.

**Response:**
```json
{
  "tags": [
    {"name": "hr", "count": 45},
    {"name": "project", "count": 38}
  ]
}
```

### GET /clusters
Get topic clusters.

**Response:**
```json
{
  "clusters": [
    {
      "id": "cluster_1",
      "name": "HR & Recruitment",
      "document_count": 23,
      "keywords": ["staff", "hire", "retention"]
    }
  ]
}
```

### POST /add
Add a new document (requires JSON body).

**Request:**
```json
{
  "text": "Your document content here",
  "source": "manual_entry"
}
```

**Response:**
```json
{
  "document_id": "doc_789",
  "chunks_created": 3,
  "status": "success"
}
```

---

## Common Use Cases

### 1. Find Information About Staff
```
http://[SERVER]:8000/search?q=india+staff+salaries
http://[SERVER]:8000/search?q=australia+team+retention
```

### 2. Project Pipeline Research
```
http://[SERVER]:8000/search?q=project+pipeline+status
http://[SERVER]:8000/search?q=alinta+energy+proposal
```

### 3. Email Thread Search
```
http://[SERVER]:8000/search?q=khadija+promotion
http://[SERVER]:8000/search?q=robby+resignation
```

### 4. Recent Activity Monitoring
```
http://[SERVER]:8000/recent?limit=20
```

### 5. Topic Exploration
```
http://[SERVER]:8000/clusters
```

Then drill down:
```
http://[SERVER]:8000/search?tag=hr
http://[SERVER]:8000/search?tag=projects
```

---

## Performance Expectations

- **Search latency**: < 100ms for simple queries
- **Complex searches**: 100-500ms
- **Concurrent users**: Optimized for 5-10 simultaneous users
- **Data freshness**: Real-time (emails ingested every minute)

---

## Data Sources

Promethean Light automatically ingests:

1. **Outlook Emails** (Chris's account)
   - Inbox and Sent Items
   - 60-day rolling window
   - Updated every minute

2. **Documents Folder**
   - Auto-watches: `Documents\` and `Downloads\`
   - Supported formats: .txt, .md, .pdf, .docx, .csv

3. **Manual Entries**
   - Via `/save` command
   - Via API POST `/add`

---

## Security & Privacy

- **Network**: Accessible only on company local network
- **Authentication**: Currently none (internal team only)
- **Encryption**: Data encrypted at rest
- **Logging**: Access logs maintained for audit

**IMPORTANT**: This server contains sensitive HR and business data. Access is restricted to authorized team members only.

---

## Troubleshooting

### "Can't connect to server"

1. Check if server is running (ask Chris)
2. Verify you're on the same network
3. Try pinging the server: `ping [SERVER-IP]`
4. Check firewall isn't blocking port 8000

### "Empty results"

1. Check spelling and try different keywords
2. Use broader terms (e.g., "india" instead of "india staff salaries")
3. Try semantic search: ask a question instead of keywords

### "Slow responses"

1. Reduce result limit: `?limit=5` instead of default
2. Server might be under heavy load
3. Notify Chris if persistent

### "Stale data"

1. Check recent documents to see last update time
2. Email watcher runs every minute
3. File watcher detects changes within seconds

---

## Getting Help

**Contact:** Chris Marinelli
**Email:** chris.marinelli@[company].com

**Server Status:** Ask Chris or check:
```
http://[SERVER]:8000/stats
```

**Request New Features:** Email Chris with requirements

---

## Advanced: Building Custom Tools

### Create a Quick Search Script

**search.bat:**
```batch
@echo off
curl -s "http://[SERVER]:8000/search?q=%*" | jq .
```

**Usage:**
```
search india staff
search project pipeline
```

### PowerShell Function

Add to your `$PROFILE`:
```powershell
function Search-MyData {
    param([string]$Query)
    $results = Invoke-RestMethod "http://[SERVER]:8000/search?q=$Query"
    $results.documents | Select-Object title, score, source
}

# Usage: Search-MyData "india staff"
```

### Python Helper Library

```python
# mydata_client.py
import requests
from typing import List, Dict, Optional

class MyDataClient:
    def __init__(self, server_url: str):
        self.server = server_url.rstrip('/')

    def search(self, query: str, limit: int = 10, tag: Optional[str] = None) -> List[Dict]:
        params = {"q": query, "limit": limit}
        if tag:
            params["tag"] = tag
        response = requests.get(f"{self.server}/search", params=params)
        response.raise_for_status()
        return response.json()["documents"]

    def stats(self) -> Dict:
        response = requests.get(f"{self.server}/stats")
        response.raise_for_status()
        return response.json()

    def recent(self, limit: int = 10) -> List[Dict]:
        response = requests.get(f"{self.server}/recent", params={"limit": limit})
        response.raise_for_status()
        return response.json()["documents"]

# Usage
client = MyDataClient("http://[SERVER]:8000")
results = client.search("india staff")
for doc in results:
    print(f"{doc['title']} - Score: {doc['score']}")
```

---

## Changelog

**2024-01-21**: Initial team access setup
- Configured network access
- Added API documentation
- Created team access guide

---

*Last updated: 2024-01-21*
*Server maintained by: Chris Marinelli*

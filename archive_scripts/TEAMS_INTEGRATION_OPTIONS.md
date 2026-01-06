# Teams Integration Options

## Option 1: Microsoft Graph API (Recommended)
**Best for**: Real-time access to Teams messages

```python
# Requirements:
# - Microsoft Graph API access
# - Azure AD app registration
# - Permissions: Chat.Read, ChannelMessage.Read.All

from msal import ConfidentialClientApplication
import requests

class TeamsWatcher:
    def __init__(self, tenant_id, client_id, client_secret):
        self.app = ConfidentialClientApplication(
            client_id,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
            client_credential=client_secret
        )

    def get_messages(self, since=None):
        # Get access token
        token = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

        # Fetch chat messages
        endpoint = "https://graph.microsoft.com/v1.0/me/chats/getAllMessages"
        if since:
            endpoint += f"?$filter=createdDateTime gt {since}"

        response = requests.get(
            endpoint,
            headers={'Authorization': 'Bearer ' + token['access_token']}
        )

        return response.json()
```

**Pros**:
- Real-time access
- Can fetch chat AND channel messages
- Official Microsoft API

**Cons**:
- Requires Azure AD app setup
- Needs admin consent for some permissions
- API rate limits

## Option 2: Teams Export Files (Simplest)
**Best for**: Periodic batch imports

Teams allows manual export of chat history. You could:
1. Export Teams chat to JSON/HTML
2. Drop the file in your `Documents` folder
3. FileWatcher auto-ingests it

**Pros**:
- No API setup needed
- Works immediately
- No authentication complexity

**Cons**:
- Manual export required
- Not real-time
- May miss recent messages

## Option 3: Outlook Integration (Already Available!)
**Best for**: Teams notifications via email

If you have "Get email notifications for Teams messages" enabled:
- Teams sends email notifications for important messages
- These are already being ingested via OutlookWatcher
- No additional code needed!

**Pros**:
- Already working
- Zero setup

**Cons**:
- Only gets notifications (not full chats)
- Depends on Teams notification settings

## Recommended Implementation: Graph API

Would you like me to implement the Graph API integration? I can create:
- `teams_watcher.py` similar to `outlook_watcher.py`
- Configuration for Azure AD credentials
- Automatic polling for new messages
- Same semantic deduplication as emails

**Setup required**:
1. Register app in Azure Portal
2. Add Microsoft Graph permissions
3. Get admin consent
4. Add credentials to `.env`

Let me know if you want me to build this!

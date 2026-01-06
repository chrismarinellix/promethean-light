"""Quick script to show last 10 emails and action items"""

from mydata.crypto import CryptoManager
from mydata.database import Database
from mydata.models import Document
from sqlmodel import select
from datetime import datetime

# Initialize
crypto = CryptoManager()
crypto.unlock()

db = Database()
session = db.session()

# Query last 10 emails
stmt = (
    select(Document)
    .where(Document.source_type == "email")
    .order_by(Document.created_at.desc())
    .limit(10)
)

emails = session.exec(stmt).all()

if not emails:
    print("No emails found in the database.")
else:
    print(f"\n{'='*80}")
    print(f"LAST {len(emails)} EMAILS")
    print(f"{'='*80}\n")

    for i, email in enumerate(emails, 1):
        print(f"\n[{i}] EMAIL FROM: {email.source}")
        print(f"    DATE: {email.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    PREVIEW: {email.raw_text[:200]}...")

        # Simple action item detection (keywords)
        text_lower = email.raw_text.lower()
        actions = []

        if any(word in text_lower for word in ["please", "can you", "could you", "need you to", "action required"]):
            actions.append("⚠️ Request/Action detected")
        if any(word in text_lower for word in ["deadline", "due", "asap", "urgent", "by end of"]):
            actions.append("⏰ Time-sensitive")
        if any(word in text_lower for word in ["review", "approve", "sign off", "feedback"]):
            actions.append("✍️ Review requested")
        if any(word in text_lower for word in ["meeting", "call", "schedule", "book time"]):
            actions.append("📅 Meeting/Schedule")
        if any(word in text_lower for word in ["invoice", "payment", "expense", "budget"]):
            actions.append("💰 Financial")

        if actions:
            print(f"    ACTIONS: {', '.join(actions)}")
        else:
            print(f"    ACTIONS: No specific actions detected")

        print(f"    {'-'*76}")

print(f"\n{'='*80}\n")

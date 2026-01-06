"""Show last 10 emails with action items"""

from mydata.crypto import CryptoManager
from mydata.database import Database
from mydata.models import Document
from sqlmodel import select

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
    print("\n" + "="*80)
    print(f"LAST {len(emails)} EMAILS")
    print("="*80 + "\n")

    for i, email in enumerate(emails, 1):
        print(f"[{i}] FROM: {email.source}")
        print(f"    DATE: {email.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Show first 400 chars
        preview = email.raw_text[:400] if len(email.raw_text) > 400 else email.raw_text
        print(f"    PREVIEW: {preview}")
        if len(email.raw_text) > 400:
            print("    ...")

        # Simple action item detection
        text_lower = email.raw_text.lower()
        actions = []

        if any(word in text_lower for word in ["please", "can you", "could you", "need you to", "action required", "todo", "to do"]):
            actions.append("⚠️ Action/Request")
        if any(word in text_lower for word in ["deadline", "due", "asap", "urgent", "by end of", "eod", "eow"]):
            actions.append("⏰ Time-sensitive")
        if any(word in text_lower for word in ["review", "approve", "sign off", "feedback", "check this"]):
            actions.append("✍️ Review needed")
        if any(word in text_lower for word in ["meeting", "call", "schedule", "book time", "zoom", "teams"]):
            actions.append("📅 Meeting")
        if any(word in text_lower for word in ["invoice", "payment", "expense", "budget", "cost"]):
            actions.append("💰 Financial")
        if any(word in text_lower for word in ["decision", "decide", "choose", "approval needed"]):
            actions.append("🎯 Decision needed")

        if actions:
            print(f"    ACTIONS: {', '.join(actions)}")
        else:
            print(f"    ACTIONS: No specific actions detected")

        print("    " + "-"*76 + "\n")

print("="*80)

#!/usr/bin/env python3
"""Search for emails from Robby about Mt Challenger"""

from mydata.client import Client

def main():
    client = Client()

    # Search for emails from Robby mentioning Mt Challenger
    print("Searching for emails from Robby about Mt Challenger...\n")

    results = client.search("from:robby mt challenger OR from:robby challenger", limit=50)

    if not results:
        print("No emails found from Robby about Mt Challenger.")
        return

    print(f"Found {len(results)} email(s):\n")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. Subject: {result.get('subject', 'No subject')}")
        print(f"   From: {result.get('sender', 'Unknown')}")
        print(f"   Date: {result.get('date', 'Unknown')}")
        print(f"   To: {result.get('recipients', 'Unknown')}")
        print(f"   Score: {result.get('score', 0):.3f}")

        # Show preview of content
        content = result.get('content', result.get('text', ''))
        if content:
            preview = content[:300].replace('\n', ' ')
            print(f"   Preview: {preview}...")

        print("-" * 80)

if __name__ == "__main__":
    main()

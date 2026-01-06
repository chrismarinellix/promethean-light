import requests
import json

# Query the API for salary review information
url = "http://localhost:8000/search"

queries = [
    "salary review team members completed",
    "reviewed salaries team",
    "pending salary reviews",
    "compensation review status"
]

for query in queries:
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print('='*80)

    try:
        response = requests.post(url, json={"query": query, "limit": 10}, timeout=10)
        if response.status_code == 200:
            results = response.json()
            if results.get("results"):
                for i, result in enumerate(results["results"], 1):
                    print(f"\n{i}. {result.get('title', 'Untitled')}")
                    print(f"   Score: {result.get('score', 0):.3f}")
                    if result.get('content'):
                        content = result['content'][:300]
                        print(f"   Content: {content}...")
            else:
                print("No results found")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error querying: {e}")

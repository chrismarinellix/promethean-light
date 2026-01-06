import sys
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from mydata.summaries import get_india_staff_summary

# Get Owais current details
data = get_india_staff_summary()
owais = [s for s in data['staff'] if 'Owais' in s['name']][0]

print('\n' + '='*80)
print(' OWAIS RAJA - COMPREHENSIVE PROFILE '.center(80, '='))
print('='*80)
print('\n[CURRENT COMPENSATION]')
print('-'*80)
print(f"  Employee ID:              {owais['id']}")
print(f"  Name:                     {owais['name']}")
print(f"  Level:                    {owais['level']}")
print(f"  CTC (INR):                {owais['ctc_inr']}")
print(f"  CTC (AUD):                {owais['ctc_aud']}")
print(f"  Retention Bonus:          {owais['retention_bonus']}")
print(f"  Bonus Valid Until:        {owais['bonus_until']}")
print(f"  Total Package (INR):      {owais['total_with_bonus_inr']}")
print(f"  Total Package (AUD):      {owais['total_with_bonus_aud']}")

print('\n[MARKET COMPARISON]')
print('-'*80)
print('  Position: Mid-Senior Engineer (India)')
print('  Current Base CTC: ₹2.5M INR ($43,860 AUD)')
print('  Total with Bonus: ₹2.75M INR ($48,246 AUD)')
print()
print('  MARKET RANGES for Mid-Senior Engineers in India:')
print('  - Lower Range:    ₹2.0M - ₹2.5M  ($35K - $44K AUD)')
print('  - Mid Range:      ₹2.5M - ₹3.5M  ($44K - $61K AUD)')
print('  - Upper Range:    ₹3.5M - ₹5.0M  ($61K - $88K AUD)')
print()
print('  Owais Position:   At lower-mid range')
print('  Assessment:       Fair for mid-senior level')
print('                    Has 10% retention bonus (good)')
print('                    Room for growth to ₹3-3.5M range with promotion')

print('\n[SEARCHING FOR EMAILS ABOUT OWAIS...]')
print('-'*80)

# Search for emails
queries = [
    'Owais Raja promotion',
    'Owais salary increase',
    'Owais performance',
    'Owais career'
]

for query in queries:
    print(f'\nQuery: "{query}"')
    try:
        response = requests.post('http://localhost:8000/search',
                                json={'query': query, 'limit': 3},
                                timeout=10)
        if response.status_code == 200:
            results = response.json()
            if results.get('results'):
                for i, result in enumerate(results['results'], 1):
                    print(f'  [{i}] {result.get("title", "Untitled")[:60]}')
                    print(f'      Score: {result.get("score", 0):.3f}')
                    if result.get('content'):
                        content = result['content'][:150].replace('\n', ' ')
                        print(f'      Preview: {content}...')
            else:
                print('  No results found')
        else:
            print(f'  Error: API returned {response.status_code}')
    except requests.exceptions.ConnectionError:
        print('  Error: API server not running')
        break
    except Exception as e:
        print(f'  Error: {e}')

print('\n[INTERNAL EQUITY ANALYSIS]')
print('-'*80)
print('  Comparing to other India staff:')
print()
print('  Faraz Khan (Senior):           ₹8.0M + 10% bonus = ₹8.8M')
print('  Mohammed Nathar (Senior):      ₹6.0M (NO BONUS) ⚠️')
print('  Owais Raja (Mid-Senior):       ₹2.5M + 10% bonus = ₹2.75M ✓')
print('  Chirag Rohit (Mid-Senior):     ₹2.5M (NO BONUS) ⚠️')
print('  Chandan Singh (Mid-Senior):    ₹2.5M (NO BONUS) ⚠️')
print('  Sirisha (Mid-level):           ₹2.25M (NO BONUS)')
print('  Abhinit (Mid-level):           ₹2.0M (NO BONUS)')
print()
print('  INSIGHT: Owais is one of only 2 India staff with retention bonus.')
print('           Other mid-senior engineers (Chirag, Chandan) at same base')
print('           but WITHOUT bonus - creates equity issue.')
print('           This suggests Owais is valued/performing well.')

print('\n[CAREER PROGRESSION POTENTIAL]')
print('-'*80)
print('  Current:          Mid-Senior Engineer @ ₹2.5M')
print('  Next Step:        Senior Engineer @ ₹3.5M - ₹6.0M')
print('  Timeline:         Typical 1.5-2 years with strong performance')
print('  Considerations:   - Has retention bonus (good sign)')
print('                    - Need performance review details')
print('                    - Compare against Faraz/Mohammed progression')

print('\n[KEY QUESTIONS TO EXPLORE]')
print('-'*80)
print('  1. Why does Owais have retention bonus while Chirag/Chandan don\'t?')
print('  2. What is his performance rating?')
print('  3. Is he on track for promotion to Senior?')
print('  4. Any flight risk or competing offers?')
print('  5. When was last salary review?')

print('\n' + '='*80 + '\n')

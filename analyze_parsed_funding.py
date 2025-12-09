import csv
import statistics

def analyze_funding():
    """Analyze the parsed funding data."""
    
    with open('data_with_parsed_funding.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Filter rows with valid AUD amounts
    valid_amounts = []
    for row in rows:
        aud_str = row.get('Funding Amount (AUD)', '').replace(',', '')
        if aud_str and aud_str.replace('.', '').isdigit():
            valid_amounts.append({
                'name': row['Grant Name'],
                'amount': float(aud_str),
                'currency': row['Funding Currency'],
                'confidence': row['Parsing Confidence']
            })
    
    # Sort by amount
    valid_amounts.sort(key=lambda x: x['amount'])
    
    amounts_only = [x['amount'] for x in valid_amounts]
    
    print(f"\n{'='*80}")
    print(f"FUNDING AMOUNT ANALYSIS")
    print(f"{'='*80}\n")
    
    print(f"Total grants with parsed amounts: {len(valid_amounts)}")
    print(f"\nStatistics (in AUD):")
    print(f"  Minimum:  ${min(amounts_only):>15,.0f}")
    print(f"  Maximum:  ${max(amounts_only):>15,.0f}")
    print(f"  Mean:     ${statistics.mean(amounts_only):>15,.0f}")
    print(f"  Median:   ${statistics.median(amounts_only):>15,.0f}")
    
    # Percentiles
    print(f"\nPercentiles:")
    for p in [10, 25, 50, 75, 90]:
        value = statistics.quantiles(amounts_only, n=100)[p-1] if len(amounts_only) > 1 else amounts_only[0]
        print(f"  {p}th:     ${value:>15,.0f}")
    
    # Top 10 largest grants
    print(f"\n{'='*80}")
    print(f"TOP 10 LARGEST GRANTS (by maximum amount in AUD)")
    print(f"{'='*80}\n")
    
    for i, grant in enumerate(valid_amounts[-10:][::-1], 1):
        print(f"{i:2d}. {grant['name'][:60]:<60}")
        print(f"    Amount: ${grant['amount']:>15,.0f} AUD ({grant['currency']}) [{grant['confidence']}]")
        print()
    
    # Bottom 10 smallest grants
    print(f"\n{'='*80}")
    print(f"TOP 10 SMALLEST GRANTS (by maximum amount in AUD)")
    print(f"{'='*80}\n")
    
    for i, grant in enumerate(valid_amounts[:10], 1):
        print(f"{i:2d}. {grant['name'][:60]:<60}")
        print(f"    Amount: ${grant['amount']:>15,.0f} AUD ({grant['currency']}) [{grant['confidence']}]")
        print()
    
    # Currency breakdown
    print(f"\n{'='*80}")
    print(f"CURRENCY BREAKDOWN")
    print(f"{'='*80}\n")
    
    currency_counts = {}
    for grant in valid_amounts:
        curr = grant['currency']
        currency_counts[curr] = currency_counts.get(curr, 0) + 1
    
    for curr, count in sorted(currency_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {curr}: {count:3d} grants ({count/len(valid_amounts)*100:.1f}%)")
    
    # Funding ranges
    print(f"\n{'='*80}")
    print(f"FUNDING RANGES (AUD)")
    print(f"{'='*80}\n")
    
    ranges = [
        (0, 10_000, "Under $10K"),
        (10_000, 50_000, "$10K - $50K"),
        (50_000, 100_000, "$50K - $100K"),
        (100_000, 250_000, "$100K - $250K"),
        (250_000, 500_000, "$250K - $500K"),
        (500_000, 1_000_000, "$500K - $1M"),
        (1_000_000, 5_000_000, "$1M - $5M"),
        (5_000_000, float('inf'), "Over $5M"),
    ]
    
    for min_val, max_val, label in ranges:
        count = sum(1 for x in amounts_only if min_val <= x < max_val)
        if count > 0:
            print(f"  {label:<20} {count:3d} grants ({count/len(amounts_only)*100:.1f}%)")

if __name__ == '__main__':
    try:
        analyze_funding()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

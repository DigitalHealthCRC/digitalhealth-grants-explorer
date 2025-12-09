import csv
import re
from typing import Dict, List, Tuple, Optional

# Exchange rates (approximate, as of Dec 2024)
EXCHANGE_RATES = {
    'AUD': 1.0,
    'NZD': 0.91,
    'USD': 1.52,
    'CAD': 1.09,
    'GBP': 1.93,
    'EUR': 1.63,
}

def extract_currency(text: str) -> str:
    """Extract currency from text."""
    text_upper = text.upper()
    
    # Check for explicit currency codes
    if 'USD' in text_upper or 'US$' in text_upper:
        return 'USD'
    elif 'NZD' in text_upper or 'NZ$' in text_upper:
        return 'NZD'
    elif 'CAD' in text_upper or 'CA$' in text_upper:
        return 'CAD'
    elif 'GBP' in text_upper or '£' in text:
        return 'GBP'
    elif 'EUR' in text_upper or '€' in text:
        return 'EUR'
    elif 'AUD' in text_upper or 'A$' in text_upper:
        return 'AUD'
    elif '$' in text:
        # Default to AUD for Australian grants
        return 'AUD'
    
    return 'UNKNOWN'

def extract_numbers_from_text(text: str) -> List[float]:
    """Extract all numerical values from text."""
    # Remove commas from numbers
    text = text.replace(',', '')
    
    # Pattern to match numbers with optional decimal points
    # Matches: 100, 100.5, 1.5M, 100K, $100,000, etc.
    patterns = [
        r'\$?\s*(\d+(?:\.\d+)?)\s*[Mm]illion',  # X million
        r'\$?\s*(\d+(?:\.\d+)?)\s*[Mm]',         # XM
        r'\$?\s*(\d+(?:\.\d+)?)\s*[Kk]',         # XK
        r'\$\s*(\d+(?:\.\d+)?)',                  # $X
        r'(\d+(?:\.\d+)?)',                       # X
    ]
    
    numbers = []
    
    # Check for millions
    million_pattern = r'\$?\s*(\d+(?:\.\d+)?)\s*[Mm]illion'
    for match in re.finditer(million_pattern, text, re.IGNORECASE):
        numbers.append(float(match.group(1)) * 1_000_000)
    
    # Check for M suffix (millions)
    m_pattern = r'\$?\s*(\d+(?:\.\d+)?)\s*[Mm](?![a-z])'
    for match in re.finditer(m_pattern, text):
        value = float(match.group(1)) * 1_000_000
        if value not in numbers:  # Avoid duplicates
            numbers.append(value)
    
    # Check for K suffix (thousands)
    k_pattern = r'\$?\s*(\d+(?:\.\d+)?)\s*[Kk](?![a-z])'
    for match in re.finditer(k_pattern, text):
        value = float(match.group(1)) * 1_000
        if value not in numbers:
            numbers.append(value)
    
    # Check for regular dollar amounts (must be >= 1000 to avoid false positives)
    dollar_pattern = r'\$\s*(\d{1,3}(?:,?\d{3})+(?:\.\d+)?)'
    for match in re.finditer(dollar_pattern, text.replace(',', '')):
        value = float(match.group(1))
        if value >= 1000 and value not in numbers:
            numbers.append(value)
    
    # Check for standalone numbers >= 10000 (likely funding amounts)
    standalone_pattern = r'(?:^|[^\d$])(\d{5,})(?:[^\d]|$)'
    for match in re.finditer(standalone_pattern, text.replace(',', '')):
        value = float(match.group(1))
        if value >= 10000 and value not in numbers:
            numbers.append(value)
    
    return sorted(set(numbers))

def parse_funding_amount(text: str) -> Dict[str, any]:
    """
    Parse funding amount text and extract structured information.
    
    Returns:
        Dict with keys: min_amount, max_amount, currency, amount_aud, 
                       confidence, notes
    """
    if not text or text.strip() == '':
        return {
            'min_amount': None,
            'max_amount': None,
            'currency': 'UNKNOWN',
            'amount_aud': None,
            'confidence': 'NONE',
            'notes': 'Empty field'
        }
    
    text = text.strip()
    
    # Check for special cases
    if any(keyword in text.lower() for keyword in ['variable', 'varies', 'not specified', 'unspecified']):
        return {
            'min_amount': None,
            'max_amount': None,
            'currency': 'UNKNOWN',
            'amount_aud': None,
            'confidence': 'VARIABLE',
            'notes': 'Variable or unspecified amount'
        }
    
    # Check for percentage-based funding
    if '%' in text and not any(char.isdigit() and text[i-1] == '$' for i, char in enumerate(text) if i > 0):
        return {
            'min_amount': None,
            'max_amount': None,
            'currency': 'UNKNOWN',
            'amount_aud': None,
            'confidence': 'PERCENTAGE',
            'notes': 'Percentage-based funding'
        }
    
    # Extract currency
    currency = extract_currency(text)
    
    # Extract all numbers
    numbers = extract_numbers_from_text(text)
    
    if not numbers:
        return {
            'min_amount': None,
            'max_amount': None,
            'currency': currency,
            'amount_aud': None,
            'confidence': 'LOW',
            'notes': 'No numbers found'
        }
    
    # Determine min and max
    min_amount = min(numbers)
    max_amount = max(numbers)
    
    # Convert to AUD
    exchange_rate = EXCHANGE_RATES.get(currency, 1.0)
    amount_aud = max_amount * exchange_rate
    
    # Determine confidence level
    confidence = 'HIGH'
    notes = []
    
    # Check for "up to" pattern
    if re.search(r'up to', text, re.IGNORECASE):
        notes.append('Up to amount')
    
    # Check for ranges
    if len(numbers) > 1:
        notes.append(f'Range: {min_amount:,.0f} - {max_amount:,.0f}')
        confidence = 'MEDIUM'
    
    # Check for tiered funding
    if re.search(r'tier|stream|phase', text, re.IGNORECASE):
        notes.append('Tiered/multi-stream funding')
        confidence = 'MEDIUM'
    
    # Check for "per annum" or multi-year
    if re.search(r'per annum|per year|p\.a\.|annually', text, re.IGNORECASE):
        notes.append('Per annum amount')
    
    if re.search(r'over \d+ years?|for \d+ years?', text, re.IGNORECASE):
        notes.append('Multi-year total')
    
    # Check for multiple currencies in same text
    currency_count = sum(1 for curr in ['AUD', 'NZD', 'USD', 'CAD', 'GBP', 'EUR'] if curr in text.upper())
    if currency_count > 1:
        notes.append('Multiple currencies mentioned')
        confidence = 'MEDIUM'
    
    return {
        'min_amount': min_amount,
        'max_amount': max_amount,
        'currency': currency,
        'amount_aud': amount_aud,
        'confidence': confidence,
        'notes': '; '.join(notes) if notes else 'Standard amount'
    }

def process_csv(input_file: str, output_file: str):
    """Process the CSV file and add parsed funding columns."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # Add new columns
        new_fieldnames = list(fieldnames) + [
            'Funding Min Amount',
            'Funding Max Amount',
            'Funding Currency',
            'Funding Amount (AUD)',
            'Parsing Confidence',
            'Parsing Notes'
        ]
        
        rows = list(reader)
    
    # Process each row
    processed_rows = []
    stats = {
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0,
        'VARIABLE': 0,
        'PERCENTAGE': 0,
        'NONE': 0
    }
    
    for row in rows:
        funding_text = row.get('Funding Amount', '')
        parsed = parse_funding_amount(funding_text)
        
        row['Funding Min Amount'] = f"{parsed['min_amount']:,.0f}" if parsed['min_amount'] else ''
        row['Funding Max Amount'] = f"{parsed['max_amount']:,.0f}" if parsed['max_amount'] else ''
        row['Funding Currency'] = parsed['currency']
        row['Funding Amount (AUD)'] = f"{parsed['amount_aud']:,.0f}" if parsed['amount_aud'] else ''
        row['Parsing Confidence'] = parsed['confidence']
        row['Parsing Notes'] = parsed['notes']
        
        processed_rows.append(row)
        stats[parsed['confidence']] += 1
    
    # Write output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)
    
    # Print statistics
    print(f"\n{'='*60}")
    print(f"FUNDING AMOUNT PARSING RESULTS")
    print(f"{'='*60}")
    print(f"\nTotal grants processed: {len(processed_rows)}")
    print(f"\nConfidence Level Breakdown:")
    print(f"  HIGH confidence:       {stats['HIGH']:3d} ({stats['HIGH']/len(processed_rows)*100:.1f}%)")
    print(f"  MEDIUM confidence:     {stats['MEDIUM']:3d} ({stats['MEDIUM']/len(processed_rows)*100:.1f}%)")
    print(f"  LOW confidence:        {stats['LOW']:3d} ({stats['LOW']/len(processed_rows)*100:.1f}%)")
    print(f"  VARIABLE/Unspecified:  {stats['VARIABLE']:3d} ({stats['VARIABLE']/len(processed_rows)*100:.1f}%)")
    print(f"  PERCENTAGE-based:      {stats['PERCENTAGE']:3d} ({stats['PERCENTAGE']/len(processed_rows)*100:.1f}%)")
    print(f"  NO DATA:               {stats['NONE']:3d} ({stats['NONE']/len(processed_rows)*100:.1f}%)")
    
    successfully_parsed = stats['HIGH'] + stats['MEDIUM']
    print(f"\nSuccessfully parsed: {successfully_parsed} ({successfully_parsed/len(processed_rows)*100:.1f}%)")
    print(f"\nOutput saved to: {output_file}")
    print(f"{'='*60}\n")
    
    # Show examples of each confidence level
    print("\nEXAMPLES BY CONFIDENCE LEVEL:")
    print(f"{'='*60}\n")
    
    shown = {level: 0 for level in stats.keys()}
    max_examples = 3
    
    for row in processed_rows:
        confidence = row['Parsing Confidence']
        if shown[confidence] < max_examples:
            print(f"[{confidence}] {row['Grant Name'][:50]}")
            print(f"  Original: {row['Funding Amount'][:80]}")
            if row['Funding Amount (AUD)']:
                print(f"  Parsed: {row['Funding Currency']} {row['Funding Max Amount']} → AUD {row['Funding Amount (AUD)']}")
            print(f"  Notes: {row['Parsing Notes']}")
            print()
            shown[confidence] += 1
        
        if all(count >= max_examples for count in shown.values()):
            break

if __name__ == '__main__':
    input_file = 'data.csv'
    output_file = 'data_with_parsed_funding.csv'
    
    print("\nStarting funding amount parsing...")
    print(f"Input file: {input_file}")
    
    try:
        process_csv(input_file, output_file)
        print("\n✅ Processing complete!")
        print(f"\nNext steps:")
        print(f"1. Review the output file: {output_file}")
        print(f"2. Check entries with MEDIUM/LOW confidence")
        print(f"3. Manually review VARIABLE and PERCENTAGE entries")
        
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find {input_file}")
        print(f"Please make sure the file exists in the current directory.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

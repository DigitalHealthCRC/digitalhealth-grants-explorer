import csv
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Current date for reference
CURRENT_DATE = datetime(2025, 12, 9)

def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse various date formats into datetime object.
    """
    date_str = date_str.strip()
    
    # Common date formats
    formats = [
        "%d %B %Y",           # 23 July 2025
        "%d-%b-%y",           # 2-Jul-25
        "%d %b %Y",           # 23 Jul 2025
        "%B %d, %Y",          # July 23, 2025
        "%d/%m/%Y",           # 23/07/2025
        "%Y-%m-%d",           # 2025-07-23
        "%d %B, %Y",          # 23 July, 2025
    ]
    
    # Try each format
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def extract_dates_from_text(text: str) -> List[datetime]:
    """
    Extract all dates from text using various patterns.
    """
    dates = []
    
    # Pattern 1: "23 July 2025" or "23 July, 2025"
    pattern1 = r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+(\d{4})'
    for match in re.finditer(pattern1, text, re.IGNORECASE):
        date_str = f"{match.group(1)} {match.group(2)} {match.group(3)}"
        parsed = parse_date_string(date_str)
        if parsed:
            dates.append(parsed)
    
    # Pattern 2: "2-Jul-25" or "23-Aug-25"
    pattern2 = r'(\d{1,2})-([A-Za-z]{3})-(\d{2})'
    for match in re.finditer(pattern2, text):
        try:
            date_str = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            parsed = datetime.strptime(date_str, "%d-%b-%y")
            dates.append(parsed)
        except ValueError:
            continue
    
    # Pattern 3: "31-Mar-26"
    pattern3 = r'(\d{1,2})-([A-Za-z]{3})-(\d{2})'
    for match in re.finditer(pattern3, text):
        try:
            date_str = f"{match.group(1)}-{match.group(2)}-20{match.group(3)}"
            parsed = datetime.strptime(date_str, "%d-%b-%Y")
            dates.append(parsed)
        except ValueError:
            continue
    
    return sorted(set(dates))

def categorize_deadline_type(text: str) -> str:
    """
    Categorize the type of deadline.
    """
    text_lower = text.lower()
    
    # Check for specific patterns
    if any(word in text_lower for word in ['ongoing', 'continuous', 'open/continuous', 'rolling']):
        return 'ROLLING'
    
    if any(word in text_lower for word in ['annual', 'yearly', 'annually']):
        return 'ANNUAL'
    
    if any(word in text_lower for word in ['closed', 'completed', 'allocated']):
        return 'CLOSED'
    
    if any(word in text_lower for word in ['tbc', 'to be announced', 'tba', 'expected', 'anticipated']):
        return 'TBA'
    
    if any(word in text_lower for word in ['various', 'varies', 'multiple', 'specific calls']):
        return 'MULTIPLE'
    
    if 'round' in text_lower and any(word in text_lower for word in ['expected', 'next']):
        return 'NEXT_ROUND'
    
    # If we can extract a date, it's a specific deadline
    dates = extract_dates_from_text(text)
    if dates:
        return 'SPECIFIC'
    
    return 'OTHER'

def calculate_deadline_status(deadline_date: Optional[datetime], deadline_type: str) -> str:
    """
    Calculate if deadline is upcoming, past, or ongoing.
    """
    if deadline_type in ['ROLLING', 'ANNUAL', 'MULTIPLE']:
        return 'ONGOING'
    
    if deadline_type == 'CLOSED':
        return 'CLOSED'
    
    if deadline_type == 'TBA':
        return 'TBA'
    
    if deadline_date:
        if deadline_date < CURRENT_DATE:
            return 'PAST'
        elif deadline_date < CURRENT_DATE + timedelta(days=30):
            return 'URGENT'  # Within 30 days
        elif deadline_date < CURRENT_DATE + timedelta(days=90):
            return 'SOON'    # Within 90 days
        else:
            return 'UPCOMING'
    
    return 'UNKNOWN'

def extract_deadline_info(text: str) -> Dict[str, any]:
    """
    Parse deadline text and extract structured information.
    
    Returns:
        Dict with keys: deadline_type, primary_date, secondary_date, 
                       deadline_status, days_until, formatted_date, notes
    """
    if not text or text.strip() == '':
        return {
            'deadline_type': 'UNKNOWN',
            'primary_date': None,
            'secondary_date': None,
            'deadline_status': 'UNKNOWN',
            'days_until': None,
            'formatted_date': '',
            'notes': 'No deadline information'
        }
    
    text = text.strip()
    
    # Categorize deadline type
    deadline_type = categorize_deadline_type(text)
    
    # Extract dates
    dates = extract_dates_from_text(text)
    
    primary_date = dates[0] if dates else None
    secondary_date = dates[1] if len(dates) > 1 else None
    
    # Calculate status
    deadline_status = calculate_deadline_status(primary_date, deadline_type)
    
    # Calculate days until deadline
    days_until = None
    if primary_date and deadline_status not in ['PAST', 'CLOSED']:
        days_until = (primary_date - CURRENT_DATE).days
    
    # Format date for display
    formatted_date = ''
    if primary_date:
        formatted_date = primary_date.strftime("%Y-%m-%d")
        if secondary_date:
            formatted_date += f" to {secondary_date.strftime('%Y-%m-%d')}"
    
    # Generate notes
    notes = []
    
    if 'minimum data' in text.lower():
        notes.append('Multi-stage application')
    
    if 'eoi' in text.lower():
        notes.append('EOI required')
    
    if 'round' in text.lower():
        # Extract round number
        round_match = re.search(r'round\s+(\d+)', text.lower())
        if round_match:
            notes.append(f'Round {round_match.group(1)}')
    
    if re.search(r'\d{1,2}:\d{2}\s*(am|pm|AEST|AEDT|NZST|NZDT)', text, re.IGNORECASE):
        notes.append('Specific time deadline')
    
    if deadline_type == 'ROLLING':
        notes.append('Applications accepted continuously')
    elif deadline_type == 'ANNUAL':
        notes.append('Annual application cycle')
    elif deadline_type == 'MULTIPLE':
        notes.append('Multiple deadlines throughout year')
    
    return {
        'deadline_type': deadline_type,
        'primary_date': primary_date.strftime("%Y-%m-%d") if primary_date else None,
        'secondary_date': secondary_date.strftime("%Y-%m-%d") if secondary_date else None,
        'deadline_status': deadline_status,
        'days_until': days_until,
        'formatted_date': formatted_date,
        'notes': '; '.join(notes) if notes else 'Standard deadline'
    }

def process_csv(input_file: str, output_file: str):
    """Process the CSV file and add parsed deadline columns."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # Add new columns
        new_fieldnames = list(fieldnames) + [
            'Deadline Type',
            'Deadline Date',
            'Deadline Status',
            'Days Until Deadline',
            'Deadline Notes'
        ]
        
        rows = list(reader)
    
    # Process each row
    processed_rows = []
    stats = {
        'SPECIFIC': 0,
        'ROLLING': 0,
        'ANNUAL': 0,
        'CLOSED': 0,
        'TBA': 0,
        'MULTIPLE': 0,
        'NEXT_ROUND': 0,
        'OTHER': 0,
        'UNKNOWN': 0
    }
    
    status_stats = {
        'URGENT': 0,
        'SOON': 0,
        'UPCOMING': 0,
        'ONGOING': 0,
        'PAST': 0,
        'CLOSED': 0,
        'TBA': 0,
        'UNKNOWN': 0
    }
    
    for row in rows:
        deadline_text = row.get('Application Deadline', '')
        parsed = extract_deadline_info(deadline_text)
        
        row['Deadline Type'] = parsed['deadline_type']
        row['Deadline Date'] = parsed['formatted_date']
        row['Deadline Status'] = parsed['deadline_status']
        row['Days Until Deadline'] = str(parsed['days_until']) if parsed['days_until'] is not None else ''
        row['Deadline Notes'] = parsed['notes']
        
        processed_rows.append(row)
        stats[parsed['deadline_type']] += 1
        status_stats[parsed['deadline_status']] += 1
    
    # Write output
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)
    
    # Print statistics
    print(f"\n{'='*60}")
    print(f"DEADLINE PARSING RESULTS")
    print(f"{'='*60}")
    print(f"\nTotal grants processed: {len(processed_rows)}")
    
    print(f"\nDeadline Type Breakdown:")
    for dtype, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {dtype:<15} {count:3d} ({count/len(processed_rows)*100:.1f}%)")
    
    print(f"\nDeadline Status Breakdown:")
    for status, count in sorted(status_stats.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {status:<15} {count:3d} ({count/len(processed_rows)*100:.1f}%)")
    
    print(f"\nOutput saved to: {output_file}")
    print(f"{'='*60}\n")
    
    # Show examples of each type
    print("\nEXAMPLES BY DEADLINE TYPE:")
    print(f"{'='*60}\n")
    
    shown = {dtype: 0 for dtype in stats.keys()}
    max_examples = 2
    
    for row in processed_rows:
        dtype = row['Deadline Type']
        if shown[dtype] < max_examples:
            print(f"[{dtype}] {row['Grant Name'][:50]}")
            print(f"  Original: {row['Application Deadline'][:70]}")
            if row['Deadline Date']:
                print(f"  Parsed Date: {row['Deadline Date']}")
            print(f"  Status: {row['Deadline Status']}")
            if row['Days Until Deadline']:
                print(f"  Days Until: {row['Days Until Deadline']}")
            print(f"  Notes: {row['Deadline Notes']}")
            print()
            shown[dtype] += 1
        
        if all(count >= max_examples for count in shown.values() if count > 0):
            break
    
    # Show urgent deadlines
    urgent = [r for r in processed_rows if r['Deadline Status'] == 'URGENT']
    if urgent:
        print(f"\n{'='*60}")
        print(f"⚠️  URGENT DEADLINES (Within 30 days)")
        print(f"{'='*60}\n")
        for row in urgent[:10]:
            print(f"• {row['Grant Name']}")
            print(f"  Deadline: {row['Deadline Date']} ({row['Days Until Deadline']} days)")
            print()

if __name__ == '__main__':
    input_file = 'data.csv'
    output_file = 'data_with_parsed_deadlines.csv'
    
    print("\nStarting deadline parsing...")
    print(f"Input file: {input_file}")
    print(f"Reference date: {CURRENT_DATE.strftime('%Y-%m-%d')}")
    
    try:
        process_csv(input_file, output_file)
        print("\n✅ Processing complete!")
        print(f"\nNext steps:")
        print(f"1. Review the output file: {output_file}")
        print(f"2. Check URGENT deadlines")
        print(f"3. Verify TBA and MULTIPLE deadline entries")
        
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find {input_file}")
        print(f"Please make sure the file exists in the current directory.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

import csv
import sys

def merge_parsed_data():
    """
    Merge the parsed funding and deadline data into a single comprehensive CSV.
    """
    
    # Read original data
    with open('data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        original_data = {row['Grant Name']: row for row in reader}
    
    # Read parsed funding data
    with open('data_with_parsed_funding.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        funding_data = {row['Grant Name']: row for row in reader}
    
    # Read parsed deadline data
    with open('data_with_parsed_deadlines.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        deadline_data = {row['Grant Name']: row for row in reader}
    
    # Merge all data
    merged_rows = []
    
    # Define final column order
    final_columns = [
        'Grant Name',
        'Administering Body',
        'Grant Purpose',
        'Application Deadline',
        'Deadline Type',
        'Deadline Date',
        'Deadline Status',
        'Days Until Deadline',
        'Deadline Notes',
        'Expired',
        'Funding Amount',
        'Funding Min Amount',
        'Funding Max Amount',
        'Funding Currency',
        'Funding Amount (AUD)',
        'Parsing Confidence',
        'Parsing Notes',
        'Co-contribution Requirements',
        'Eligibility Criteria',
        'Assessment Criteria',
        'Application Complexity',
        'Web Link',
        'Level of Complexity'
    ]
    
    for grant_name in original_data.keys():
        merged_row = {}
        
        # Start with original data
        orig = original_data[grant_name]
        fund = funding_data.get(grant_name, {})
        dead = deadline_data.get(grant_name, {})
        
        # Merge all columns
        for col in final_columns:
            if col in dead and dead.get(col):
                merged_row[col] = dead[col]
            elif col in fund and fund.get(col):
                merged_row[col] = fund[col]
            elif col in orig:
                merged_row[col] = orig[col]
            else:
                merged_row[col] = ''
        
        merged_rows.append(merged_row)
    
    # Write merged data
    with open('data_parsed_complete.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=final_columns)
        writer.writeheader()
        writer.writerows(merged_rows)
    
    print(f"\n{'='*60}")
    print(f"MERGED DATA CREATED")
    print(f"{'='*60}\n")
    print(f"Total grants: {len(merged_rows)}")
    print(f"Output file: data_parsed_complete.csv")
    print(f"\nColumns included:")
    print(f"  • Original columns: {len([c for c in final_columns if c in original_data[list(original_data.keys())[0]]])}")
    print(f"  • Funding columns: 6")
    print(f"  • Deadline columns: 5")
    print(f"  • Total columns: {len(final_columns)}")
    print(f"\n{'='*60}\n")
    
    # Generate summary statistics
    print("SUMMARY STATISTICS:")
    print(f"{'='*60}\n")
    
    # Deadline stats
    deadline_status_counts = {}
    for row in merged_rows:
        status = row.get('Deadline Status', 'UNKNOWN')
        deadline_status_counts[status] = deadline_status_counts.get(status, 0) + 1
    
    print("Deadline Status:")
    for status, count in sorted(deadline_status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {status:<15} {count:3d} ({count/len(merged_rows)*100:.1f}%)")
    
    # Funding stats
    print("\nFunding Confidence:")
    funding_confidence_counts = {}
    for row in merged_rows:
        conf = row.get('Parsing Confidence', 'UNKNOWN')
        funding_confidence_counts[conf] = funding_confidence_counts.get(conf, 0) + 1
    
    for conf, count in sorted(funding_confidence_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {conf:<15} {count:3d} ({count/len(merged_rows)*100:.1f}%)")
    
    # Actionable grants (open + with funding)
    actionable = [
        r for r in merged_rows 
        if r.get('Deadline Status') in ['URGENT', 'SOON', 'UPCOMING', 'ONGOING'] 
        and r.get('Funding Amount (AUD)') 
        and r.get('Funding Amount (AUD)').replace(',', '').isdigit()
    ]
    
    print(f"\n{'='*60}")
    print(f"ACTIONABLE GRANTS")
    print(f"{'='*60}\n")
    print(f"Grants with open deadlines AND parsed funding: {len(actionable)}")
    
    # Show top actionable grants by funding
    actionable_sorted = sorted(
        actionable, 
        key=lambda x: float(x['Funding Amount (AUD)'].replace(',', '')), 
        reverse=True
    )
    
    print(f"\nTop 10 Actionable Grants by Funding Amount:")
    print(f"{'-'*60}\n")
    for i, row in enumerate(actionable_sorted[:10], 1):
        print(f"{i:2d}. {row['Grant Name'][:45]:<45}")
        print(f"    Amount: ${row['Funding Amount (AUD)']:>15} AUD")
        print(f"    Status: {row['Deadline Status']:<10} | Deadline: {row['Deadline Date']}")
        print()

if __name__ == '__main__':
    try:
        merge_parsed_data()
        print("\n✅ Merge complete!")
        print("\nYou now have a comprehensive dataset with:")
        print("  • Parsed funding amounts in AUD")
        print("  • Categorized deadlines with status")
        print("  • Days until deadline calculations")
        print("  • All original grant information")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: Missing required file")
        print(f"Please ensure you have run both:")
        print(f"  1. parse_funding_amounts.py")
        print(f"  2. parse_deadlines.py")
        print(f"\nError details: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

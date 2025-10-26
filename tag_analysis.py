#!/usr/bin/env python3
"""
Script to analyze tags from data.csv file
Extracts all tags and counts their frequency
"""

import csv
from collections import Counter
from pathlib import Path

def analyze_tags(csv_file_path):
    """
    Analyze tags from the healthcare grants CSV file
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        Counter: Counter object with tag frequencies
    """
    # Extract all tags
    all_tags = []
    
    # Read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        # Iterate through all grants
        for row in csv_reader:
            # Generate tags from grant data (similar to JavaScript implementation)
            tags = generate_tags_from_grant(row)
            all_tags.extend(tags)
    
    # Count frequency of each tag
    tag_counts = Counter(all_tags)
    
    return tag_counts

def get_geographic_tags(administering_body):
    """
    Determine geographic tags based on administering body
    
    Args:
        administering_body (str): Administering body text
        
    Returns:
        list: List of geographic tags
    """
    tags = []
    administering_body = administering_body.lower()
    
    # Check for New Zealand
    if any(indicator in administering_body for indicator in [
        'new zealand', 'nz', 'mbie', 'tec', 'hrc', 'callaghan innovation',
        'ministry of business, innovation and employment', 'tertiary education commission',
        'health research council of new zealand'
    ]):
        tags.append('#NewZealand')
        return tags
    
    # Check for international organizations
    if any(indicator in administering_body for indicator in [
        'gates foundation', 'bill & melinda gates', 'unesco', 'chan zuckerberg',
        'wellcome trust', 'open philanthropy', 'global innovation fund',
        'grand challenges canada', 'american australian association'
    ]):
        tags.append('#International')
        return tags
    
    # Check for Australian organizations
    australian_indicators = [
        'australian', 'australia', 'commonwealth', 'federal', 'nhmrc', 'arc',
        'csiro', 'austcyber', 'arena', 'ato',  'mrff'
    ]
    
    if any(indicator in administering_body for indicator in australian_indicators):
        tags.append('#Australia')
        
        # Check for Commonwealth/Federal
        if any(indicator in administering_body for indicator in [
            'commonwealth', 'federal', 'australian government', 
            'nhmrc', 'arc', 'csiro', 'ato', 'mrff', 'austcyber', 'arena'
        ]):
            tags.append('#Commonwealth')
        
        # Check for specific Australian states
        if any(indicator in administering_body for indicator in [
            'nsw', 'new south wales', 'sydney', 'investment nsw'
        ]):
            tags.append('#NSW')
        elif any(indicator in administering_body for indicator in [
            'victoria', 'victorian', 'melbourne', 'vic'
        ]):
            tags.append('#Victoria')
        elif any(indicator in administering_body for indicator in [
            'queensland', 'qld', 'brisbane'
        ]):
            tags.append('#Queensland')
        elif any(indicator in administering_body for indicator in [
            'western australia', 'wa', 'perth'
        ]):
            tags.append('#WesternAustralia')
        elif any(indicator in administering_body for indicator in [
            'south australia', 'sa', 'adelaide'
        ]):
            tags.append('#SouthAustralia')
        elif any(indicator in administering_body for indicator in [
            'tasmania', 'tas', 'hobart', 'tasmanian'
        ]):
            tags.append('#Tasmania')
        elif any(indicator in administering_body for indicator in [
            'northern territory', 'nt', 'darwin'
        ]):
            tags.append('#NorthernTerritory')
        elif any(indicator in administering_body for indicator in [
            'act', 'australian capital territory', 'canberra'
        ]):
            tags.append('#ACT')
    
    return tags

def generate_tags_from_grant(grant_row):
    """
    Generate tags from grant data 
    
    Args:
        grant_row (dict): Row from CSV file
        
    Returns:
        list: List of generated tags
    """
    tags = []
    
    # Get grant name and purpose for tag generation
    grant_name = grant_row.get('Grant Name', '').lower()
    purpose = grant_row.get('Grant Purpose', '').lower()
    administering_body = grant_row.get('Administering Body', '').lower()
    complexity = grant_row.get('Level of Complexity', '')
    
    # Add tags based on grant name and purpose
    searchable_text = f"{grant_name} {purpose}"
    
    if 'research' in searchable_text:
        tags.append('#Research')
    if 'health' in searchable_text:
        tags.append('#Health')
    if 'medical' in searchable_text:
        tags.append('#Medical')
    if 'innovation' in searchable_text:
        tags.append('#Innovation')
    if 'mrff' in searchable_text:
        tags.append('#MRFF')
    if 'clinical' in searchable_text:
        tags.append('#Clinical')
    if 'trial' in searchable_text:
        tags.append('#ClinicalTrials')
    if 'stem cell' in searchable_text:
        tags.append('#StemCell')
    if 'cardiovascular' in searchable_text:
        tags.append('#Cardiovascular')
    if 'cancer' in searchable_text:
        tags.append('#Cancer')
    if 'dementia' in searchable_text or 'ageing' in searchable_text:
        tags.append('#Dementia')
    if 'diabetes' in searchable_text:
        tags.append('#Diabetes')
    
    # Add innovation and digital transformation tags
    if 'innovation' in searchable_text or 'innovative' in searchable_text:
        tags.append('#Innovation')
    if 'digital' in searchable_text and ('transformation' in searchable_text or 'transform' in searchable_text):
        tags.append('#DigitalTransformation')
    if 'workforce' in searchable_text and 'health' in searchable_text:
        tags.append('#HealthWorkforce')
    if 'digital' in searchable_text and 'workforce' in searchable_text and 'health' in searchable_text:
        tags.append('#DigitalHealthWorkforce')
    if 'digital' in searchable_text and 'health' in searchable_text:
        tags.append('#DigitalHealth')
    
    # Add geographic tags based on administering body
    geographic_tags = get_geographic_tags(administering_body)
    tags.extend(geographic_tags)
    
    # Add specific organization tags
    if 'nhmrc' in administering_body:
        tags.append('#NHMRC')
    if 'arc' in administering_body:
        tags.append('#ARC')
    
    # Add complexity tag
    if complexity:
        tags.append(f"#{complexity.replace(' ', '').replace('-', '')}")
    
    # Remove duplicates
    return list(set(tags))

def create_markdown_table(tag_counts):
    """
    Create a markdown table from tag counts
    
    Args:
        tag_counts (Counter): Counter object with tag frequencies
        
    Returns:
        str: Markdown formatted table
    """
    # Sort by frequency (descending)
    sorted_tags = tag_counts.most_common()
    
    # Create markdown table
    table = "| Tag | Frequency |\n"
    table += "|-----|----------|\n"
    
    for tag, count in sorted_tags:
        table += f"| {tag} | {count} |\n"
    
    return table

def main():
    project_root = Path(__file__).resolve().parent
    csv_file_path = project_root / 'data.csv'
    
    # Analyze tags
    tag_counts = analyze_tags(csv_file_path)
    
    # Create and print markdown table
    markdown_table = create_markdown_table(tag_counts)
    print("# Healthcare Grants Tag Frequency Analysis\n")
    print(markdown_table)
    
    # Print some summary statistics
    print(f"\n## Summary Statistics")
    print(f"- Total unique tags: {len(tag_counts)}")
    print(f"- Total tag occurrences: {sum(tag_counts.values())}")
    if tag_counts:
        print(f"- Most frequent tag: {tag_counts.most_common(1)[0][0]} ({tag_counts.most_common(1)[0][1]} occurrences)")
    else:
        print("- No tags found")

if __name__ == "__main__":
    main()

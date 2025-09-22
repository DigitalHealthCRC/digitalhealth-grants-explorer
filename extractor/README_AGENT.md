# Grant Extraction Agent

## Overview
This AI-driven grant extraction script uses Claude LLM to autonomously navigate the Australian Health Department's MRFF grant opportunities website and extract structured grant information.

## Features
- **Autonomous Navigation**: Claude AI agent explores the website, follows links, and handles pagination
- **Comprehensive Extraction**: Extracts 11 specific fields per grant including name, deadline, funding amount, etc.
- **Australian English**: Formats output using Australian English conventions
- **JSON Output**: Structured output format for easy processing
- **Error Handling**: Robust error handling for web requests and API calls

## Setup

### Prerequisites
1. Python 3.8 or higher
2. Anthropic API key for Claude access

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set your Claude API key
export ANTHROPIC_API_KEY="your_claude_api_key_here"
```

## Usage

### Basic Usage
```bash
python grant_extractor_agent.py
```

### Expected Output
The script will create a timestamped JSON file (e.g., `extracted_grants_20241209_143022.json`) containing:
- Extraction timestamp
- Source URL
- Claude's structured response with grant information
- All 11 required fields per grant

## Grant Information Extracted

For each grant found, the agent extracts:

1. **Grant Name**: Official title of the grant
2. **Administering Body**: Organization providing the grant
3. **Grant Purpose**: Description of the grant's purpose
4. **Application Deadline**: Submission deadline
5. **Funding Amount**: Available funding
6. **Co-contribution Requirements**: Required matching funds or contributions
7. **Eligibility Criteria**: Who can apply
8. **Assessment Criteria**: How applications are evaluated
9. **Application Complexity**: AI judgment of application complexity
10. **Web Link**: Source URL for the grant information
11. **Level of Complexity**: Categorical complexity rating (Low/Moderate/Complex/Very Complex/Varies)

## How It Works

1. **Content Extraction**: Downloads and cleans website content using requests and BeautifulSoup
2. **AI Processing**: Sends comprehensive prompt with website content to Claude AI
3. **Autonomous Navigation**: Claude AI intelligently navigates the site structure in its reasoning
4. **Structured Extraction**: AI extracts information according to the specified format
5. **JSON Output**: Results are saved in structured JSON format

## Important Notes

- **No Hallucination**: The AI is instructed to only extract information that's actually present
- **Australian English**: All output uses Australian spelling and conventions
- **Judgment Fields**: Only "Application Complexity" and "Level of Complexity" use AI judgment
- **Comprehensive**: The agent explores all relevant pages and pagination
- **Rate Limiting**: Includes appropriate delays and headers to respect website policies

## Configuration

The script can be easily modified to:
- Target different grant websites
- Extract additional fields
- Use different AI models
- Adjust output formats

## Error Handling

The script handles:
- Network connectivity issues
- API rate limits and errors
- Malformed website content
- Missing information gracefully

## Example Output Structure

```json
{
  "extraction_timestamp": "2024-12-09T14:30:22",
  "source_url": "https://www.health.gov.au/our-work/mrff/grant-opportunities-calendar",
  "grants": [
    {
      "Grant Name": "MRFF 2025 Cardiovascular Health Grant Opportunity",
      "Administering Body": "Australian Government Department of Health",
      "Grant Purpose": "Support innovative cardiovascular health research",
      "Application Deadline": "31 March 2025 (5pm AEST)",
      "Funding Amount": "AUD $250,000",
      "Co-contribution Requirements": "20% cash co-contribution required",
      "Eligibility Criteria": "Australian universities and research institutions",
      "Assessment Criteria": "Innovation potential and research methodology",
      "Application Complexity": "Complex - requires detailed research proposals and budgets",
      "Web Link": "https://www.health.gov.au/mrff/cardiovascular-health-2025",
      "Level of Complexity": "Complex"
    }
  ]
}
```

## Future Enhancements

- Integration with LangExtract for more precise extraction
- Support for multiple websites simultaneously  
- Automated scheduling for regular updates
- Integration with the main grant scraper system
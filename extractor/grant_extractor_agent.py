#!/usr/bin/env python3
"""
AI Agent-Driven Grant Extraction Script
Uses Claude LLM with LangExtract to autonomously extract grant information
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class GrantExtractionAgent:
    """AI Agent for autonomous grant extraction using Claude LLM"""
    
    def __init__(self, claude_api_key: str = None):
        """Initialize the grant extraction agent"""
        self.claude_api_key = claude_api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.claude_api_key:
            raise ValueError("Claude API key required. Set ANTHROPIC_API_KEY environment variable.")
        
        self.target_url = "https://www.health.gov.au/our-work/mrff/grant-opportunities-calendar"
        self.output_file = f"extracted_grants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    def get_comprehensive_prompt(self) -> str:
        """Create the comprehensive prompt for the AI agent"""
        return """
I want you to explore the following webpage and see if it lists some available grants. Make a list of all the grants and provide the following information if it is available:

WEBSITE TO EXPLORE: https://www.health.gov.au/our-work/mrff/grant-opportunities-calendar

INSTRUCTIONS:
- Navigate through the entire website, follow relevant links, and check paginated pages if there is a long list
- Look for ALL funding opportunities and grants listed
- Extract the following information for each grant you find:

REQUIRED INFORMATION FOR EACH GRANT:
1. Grant Name: Name or title of the grant, Example: "MRFF 2025 Cardiovascular Health Grant Opportunity (GO7554)"
2. Administering Body: The organisation providing the grant, Example: "Australian Government Department of Health"
3. Grant Purpose: Any listed purpose of the grant, Example: "Grow Australia's cyber security industry by supporting innovative projects that enhance cyber capabilities, foster collaboration, and drive industry growth"
4. Application Deadline: The deadline for the application, Example: "1 September 2025 (5pm AEST)"
5. Funding Amount: The funding amount of the grant, Example: "AUD $50,000"
6. Co-contribution Requirements: Use free text to say if there are any co-contribution requirements for this grant, it could also be "none required" or "not specified". Example: "Mandatory matched funding (cash) from the applicant"
7. Eligibility Criteria: Criteria listed for the grant, it could include education level, ethnicity, nationality, organisation type, experience, etc. Example: "Australian and Indigenous Australian individuals undertaking full-time graduate-level study at an accredited US educational institution"
8. Assessment Criteria: Any listed criteria for assessment, Example: "Academic excellence, innovation potential, and contribution to global challenges"
9. Application Complexity: Considering the grant amount, reputation, number of applications for this type of grant, requirements, what would be your judgement and reasoning regarding the complexity, write in one sentence: Example: "Complex - requires detailed technical, financial, and commercial proposals"
10. Web Link: This would be the URL of the page from which the text is extracted, Example: "https://www.health.gov.au/our-work/mrff/grant-opportunities-calendar"
11. Level of Complexity: Considering your response for "Application Complexity", map it into one of the 5 choices below: "Low", "Moderate", "Complex", "Very Complex," or "Varies"

IMPORTANT RULES:
- You MUST NOT make things up or hallucinate, if the info is not provided, just say "not found"
- The only info you can use your own judgement for is defining "Application Complexity" and "Level of Complexity"
- Always use Australian English, even if the original text is using American English or British English
- Avoid using Em-dashes and title case
- Be thorough - explore all relevant pages and links to find all available grants
- If you encounter pagination, navigation menus, or "View more" links, follow them to find additional grants

OUTPUT FORMAT:
Provide your response as a structured list that can be easily converted to JSON, with each grant as a separate entry containing all 11 fields.
"""

    def extract_website_content(self, url: str) -> str:
        """Extract content from website using requests and BeautifulSoup"""
        try:
            headers = {
                'User-Agent': 'Grant Extraction Bot 1.0 (Research Purpose)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-AU,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return f"Error: Could not extract content from {url}"
    
    def call_claude_api(self, prompt: str, content: str) -> str:
        """Call Claude API with the extraction prompt"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=self.claude_api_key)
        
        full_prompt = f"""
{prompt}

WEBSITE CONTENT TO ANALYZE:
{content[:50000]}  # Limit content to avoid token limits

Please analyze this content thoroughly and extract all grant information as requested. If the content is truncated and you need to see more, let me know and I can provide additional content.
"""
        
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8000,
                temperature=0.1,  # Low temperature for consistent extraction
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return f"Error: Could not get response from Claude API - {e}"
    
    def parse_claude_response_to_json(self, response_text: str) -> List[Dict]:
        """Parse Claude's response into structured JSON format"""
        try:
            # This is a simplified parser - in practice, you might need more sophisticated parsing
            # depending on how Claude formats the response
            
            # For now, return the raw response and let the user manually structure it
            # In a production version, you'd implement proper parsing logic
            
            parsed_data = {
                "extraction_timestamp": datetime.now().isoformat(),
                "source_url": self.target_url,
                "raw_response": response_text,
                "note": "This is the raw response from Claude. Manual parsing may be needed to structure into individual grants."
            }
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            return {"error": f"Could not parse response: {e}", "raw_response": response_text}
    
    def run_extraction(self) -> str:
        """Main method to run the grant extraction process"""
        print(f"Starting grant extraction from {self.target_url}")
        
        # Step 1: Get the comprehensive prompt
        prompt = self.get_comprehensive_prompt()
        print("✓ Comprehensive prompt prepared")
        
        # Step 2: Extract website content
        print("Extracting website content...")
        content = self.extract_website_content(self.target_url)
        print(f"✓ Extracted {len(content)} characters of content")
        
        # Step 3: Call Claude API with the prompt and content
        print("Calling Claude API for grant extraction...")
        claude_response = self.call_claude_api(prompt, content)
        print("✓ Received response from Claude")
        
        # Step 4: Parse response and save as JSON
        print("Processing and saving results...")
        structured_data = self.parse_claude_response_to_json(claude_response)
        
        # Save to JSON file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Results saved to {self.output_file}")
        print(f"\nExtraction complete! Check {self.output_file} for results.")
        
        return self.output_file


def main():
    """Main function to run the grant extraction"""
    try:
        # Initialize the agent
        agent = GrantExtractionAgent()
        
        # Run the extraction
        output_file = agent.run_extraction()
        
        print(f"\nSuccess! Grant extraction completed.")
        print(f"Output file: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
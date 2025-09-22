# LangExtract + LangChain Integration Reference

## Overview

This document serves as a comprehensive reference for implementing LangExtract with LangChain for our grant scraping system. LangExtract provides precise structured data extraction from unstructured text, while LangChain offers powerful web navigation and agent capabilities.

## LangExtract Core Concepts

### What is LangExtract?
LangExtract is a Python library for extracting structured information from unstructured text using Large Language Models (LLMs). It uses few-shot learning to consistently extract data across different text formats.

### Key Features
- **Precise Source Grounding**: Maps extractions to exact text locations in source material
- **Few-Shot Learning**: Uses example-based training for consistent extraction patterns
- **Interactive HTML Visualization**: Visual debugging of extracted entities
- **Multi-Provider Support**: Works with Gemini, OpenAI, Ollama (local models)
- **Structured Output**: Generates consistent data structures from unstructured input

## LangExtract Code Patterns

### Basic Extraction Setup
```python
import langextract as lx

result = lx.extract(
    text_or_documents=input_text,
    prompt_description="Extract specific information from grant announcements",
    examples=examples,
    model_id="gemini-2.5-flash"
)
```

### Few-Shot Learning Example Structure
```python
examples = [
    lx.data.ExampleData(
        text="Grant Title: Digital Health Innovation Fund\nAdministering Body: Department of Health\nDeadline: March 31, 2025\nFunding Amount: $500,000",
        extractions=[
            lx.data.Extraction(
                extraction_class="grant_title",
                extraction_text="Digital Health Innovation Fund",
                attributes={"domain": "health", "type": "innovation"}
            ),
            lx.data.Extraction(
                extraction_class="administering_body",
                extraction_text="Department of Health",
                attributes={"level": "federal", "department": "health"}
            ),
            lx.data.Extraction(
                extraction_class="deadline",
                extraction_text="March 31, 2025",
                attributes={"date_format": "month_day_year"}
            ),
            lx.data.Extraction(
                extraction_class="funding_amount",
                extraction_text="$500,000",
                attributes={"currency": "USD", "amount": 500000}
            )
        ]
    )
]
```

### Model Configuration Options

#### Cloud API Models
```python
# Using Gemini (Google)
config = lx.factory.ModelConfig(
    model_id="gemini-2.5-flash",
    provider_kwargs={"api_key": "your_api_key"}
)

# Using OpenAI
config = lx.factory.ModelConfig(
    model_id="gpt-4",
    provider_kwargs={"api_key": "your_openai_key"}
)
```

#### Local Models (Ollama)
```python
# Setup: ollama pull gemma2:2b
config = lx.factory.ModelConfig(
    model_id="gemma2:2b",
    provider_kwargs={
        "model_url": "http://localhost:11434",
        "timeout": 300  # 5 minutes for larger models
    }
)
```

## LangChain Integration

### Why Combine LangExtract + LangChain?

**LangChain Strengths:**
- Web browsing and navigation
- Document loaders and text processing
- Agent frameworks and tool usage
- Chain orchestration and workflow management

**LangExtract Strengths:**
- Precise structured data extraction
- Source grounding and traceability
- Consistent few-shot learning
- Interactive visualization

**Combined Power:**
- LangChain agents navigate complex websites
- LangExtract extracts structured data from discovered content
- LangChain manages workflow and error handling
- LangExtract ensures data quality and consistency

### Integration Pattern
```python
from langchain.agents import initialize_agent
from langchain.tools import WebBrowserTool
import langextract as lx

# LangChain handles web navigation
web_tool = WebBrowserTool()
agent = initialize_agent([web_tool], llm, agent="zero-shot-react-description")

# Navigate to grant website
web_content = agent.run("Navigate to grant website and extract all grant listings")

# LangExtract handles structured extraction
result = lx.extract(
    text_or_documents=web_content,
    prompt_description="Extract grant information including title, body, deadline, amount, eligibility",
    examples=grant_examples,
    model_id="gemini-2.5-flash"
)
```

## Grant Scraping Application

### Extraction Schema for Grants
```python
# Grant-specific extraction classes
GRANT_EXTRACTION_CLASSES = [
    "grant_title",           # Official name of the grant
    "administering_body",    # Organization offering the grant
    "grant_purpose",         # Brief description/purpose
    "deadline",              # Application deadline
    "funding_amount",        # Available funding
    "eligibility_criteria",  # Who can apply
    "assessment_criteria",   # How applications are evaluated
    "complexity",            # Application complexity level
    "web_link",             # Direct URL to grant details
    "co_contribution"        # Required matching funds
]

# Corresponding attributes for context
GRANT_ATTRIBUTES = {
    "domain": ["health", "research", "innovation", "education"],
    "level": ["federal", "state", "local", "international"],
    "organization_type": ["nonprofit", "university", "company", "government"],
    "complexity_level": ["simple", "moderate", "complex"],
    "currency": ["USD", "AUD", "EUR"],
    "amount_range": ["small", "medium", "large"]
}
```

### Complete Grant Extraction Example
```python
grant_examples = [
    lx.data.ExampleData(
        text="""
        Medical Research Future Fund (MRFF) - Digital Health Research
        
        The Department of Health is pleased to announce funding opportunities under the MRFF Digital Health Research initiative. This program supports innovative research projects that leverage digital technologies to improve healthcare outcomes.
        
        Key Details:
        - Total funding available: $2.5 million
        - Individual grants: Up to $250,000 per project
        - Application deadline: June 15, 2024
        - Eligibility: Australian universities and research institutions
        - Co-contribution: 20% cash or in-kind required
        - Application complexity: Moderate (15-20 pages)
        
        Assessment will focus on innovation potential, research methodology, and projected health impact.
        
        Apply online: https://www.health.gov.au/mrff-digital-health
        """,
        extractions=[
            lx.data.Extraction(
                extraction_class="grant_title",
                extraction_text="Medical Research Future Fund (MRFF) - Digital Health Research",
                attributes={"domain": "health", "type": "research", "program": "MRFF"}
            ),
            lx.data.Extraction(
                extraction_class="administering_body",
                extraction_text="Department of Health",
                attributes={"level": "federal", "country": "Australia"}
            ),
            lx.data.Extraction(
                extraction_class="grant_purpose",
                extraction_text="supports innovative research projects that leverage digital technologies to improve healthcare outcomes",
                attributes={"focus": "digital_health", "type": "research"}
            ),
            lx.data.Extraction(
                extraction_class="deadline",
                extraction_text="June 15, 2024",
                attributes={"date_format": "month_day_year", "timezone": "AEST"}
            ),
            lx.data.Extraction(
                extraction_class="funding_amount",
                extraction_text="Up to $250,000 per project",
                attributes={"currency": "AUD", "max_amount": 250000, "total_pool": 2500000}
            ),
            lx.data.Extraction(
                extraction_class="eligibility_criteria",
                extraction_text="Australian universities and research institutions",
                attributes={"geographic": "Australia", "org_type": ["university", "research_institution"]}
            ),
            lx.data.Extraction(
                extraction_class="assessment_criteria",
                extraction_text="innovation potential, research methodology, and projected health impact",
                attributes={"focus_areas": ["innovation", "methodology", "impact"]}
            ),
            lx.data.Extraction(
                extraction_class="complexity",
                extraction_text="Moderate (15-20 pages)",
                attributes={"level": "moderate", "page_count": "15-20"}
            ),
            lx.data.Extraction(
                extraction_class="web_link",
                extraction_text="https://www.health.gov.au/mrff-digital-health",
                attributes={"link_type": "application_portal"}
            ),
            lx.data.Extraction(
                extraction_class="co_contribution",
                extraction_text="20% cash or in-kind required",
                attributes={"percentage": 20, "type": ["cash", "in_kind"]}
            )
        ]
    )
]
```

## Implementation Architecture

### Complete Integration Flow
```python
class LangChainLangExtractGrantScraper:
    def __init__(self, config):
        self.config = config
        self.langchain_agent = self._setup_langchain_agent()
        self.extraction_examples = self._load_grant_examples()
        
    def scrape_grants_from_url(self, url):
        # Step 1: LangChain navigates and extracts content
        raw_content = self.langchain_agent.run(f"Extract all grant information from {url}")
        
        # Step 2: LangExtract processes content for structured data
        extractions = lx.extract(
            text_or_documents=raw_content,
            prompt_description="Extract structured grant information",
            examples=self.extraction_examples,
            model_id=self.config.model_id
        )
        
        # Step 3: Convert to our CSV format
        grants = self._convert_extractions_to_grants(extractions)
        return grants
        
    def _convert_extractions_to_grants(self, extractions):
        grants = []
        # Group extractions by source location to create complete grant records
        # Convert to our CSV column format
        # Apply validation and deduplication
        return grants
```

## Best Practices

### Model Selection
- **Development/Testing**: Use cloud APIs (Gemini, OpenAI) for reliability
- **Production**: Consider local models (Ollama) for cost and privacy
- **Hybrid**: Cloud for complex extractions, local for simple ones

### Few-Shot Learning Optimization
- **Diversity**: Include examples from different website structures
- **Quality**: Use clear, well-structured examples
- **Iterative**: Refine examples based on extraction accuracy
- **Validation**: Test against unseen content regularly

### Error Handling
```python
try:
    result = lx.extract(text, prompt, examples, model_id)
    if not result.extractions:
        # Fallback to simpler extraction or manual parsing
        pass
except Exception as e:
    logger.error(f"LangExtract failed: {e}")
    # Implement fallback strategy
```

### Cost Management
- Monitor API usage and costs
- Implement usage limits and quotas
- Use local models for high-volume processing
- Cache results to avoid re-processing

## Next Steps for Implementation

1. **Setup Dependencies**: Add LangExtract and LangChain to requirements
2. **Model Configuration**: Choose and configure LLM provider
3. **Create Examples**: Build comprehensive few-shot learning examples
4. **Integration**: Replace existing parsing with LangExtract calls
5. **Testing**: Validate extraction accuracy across different grant sources
6. **Optimization**: Refine examples and prompts based on results

## Resources

- **LangExtract GitHub**: https://github.com/google/langextract
- **LangChain Documentation**: https://python.langchain.com/docs/introduction/
- **Romeo & Juliet Example**: https://github.com/google/langextract/blob/main/examples/notebooks/romeo_juliet_extraction.ipynb
- **Ollama Integration**: https://github.com/google/langextract/tree/main/examples/ollama
- **Custom Provider Plugin**: https://github.com/google/langextract/tree/main/examples/custom_provider_plugin
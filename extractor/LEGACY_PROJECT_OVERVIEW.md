# Legacy Grant Extraction Project Overview

This document captures the intent and mechanics of the current grant-extraction codebase so we can archive it confidently before rebuilding the workflow on top of Jina DeepSearch.

## Project Goal

Automate the discovery of Australian (and New Zealand) digital-health-relevant grant opportunities by:

1. Crawling curated seed domains, harvesting in-domain pages, and extracting human-readable text.
2. Running a constrained OpenAI prompt to convert each page into structured grant records with 11 mandatory attributes.
3. Filtering to a pre-defined digital health scope, deduplicating results, and exporting JSON/CSV datasets.
4. Enriching the crawl-derived grants with three dedicated data feeds (ARC, Research Data Australia, NIH) that are ingested through bespoke API/RSS paths rather than web crawling.

## Agent Architecture

| Component | Responsibilities |
| --- | --- |
| `crawler_agent.CrawlAgent` | Breadth-first traversal of every seed URL. Keeps requests in-domain, honours `max_depth` and `max_pages_per_seed`, applies a politeness delay (0.3 s), and stores a `PageContent` tuple (URL, depth, title, cleaned text). Removes scripts/nav/headers before returning text. |
| `playwright_agent` (optional) | Re-fetches pages flagged by `needs_playwright_render`—anything empty or containing phrases such as “enable JavaScript”. Only runs when `--use-playwright` is passed. |
| `extraction_agent.ExtractionAgent` | Splits each page into 3,500-character chunks, sends them to the OpenAI Chat Completions API with JSON-schema enforced output, and parses the response back into grant dicts. Retries up to three times with exponential backoff. |
| `grant_extractor_agent` | CLI orchestrator. Reads seeds, runs the crawler, triggers Playwright fallback when needed, executes extraction, filters to scope, dedupes, ingests external feeds, and writes JSON/CSV snapshots plus raw feed dumps. |

## Prompt Contracts

### System Prompt

```
You are an assistant that extracts Australian grant information. Only report details explicitly present in the supplied content. If a field is missing, use the string 'not found'. Write using Australian English and avoid em dashes. Focus strictly on funding opportunities related to healthcare, digital health, artificial intelligence, research, innovation, synthetic data, digital workforce, or education within Australia or New Zealand. Ignore grants outside these domains.
```

### User Prompt Template

```
Analyse the following content from {url} and identify every distinct grant or funding opportunity. Only include grants that are relevant to the Australian (or New Zealand) digital health ecosystem, including healthcare, digital health, AI, innovation, research, synthetic data, digital workforce, or education. Exclude unrelated grants. Return a JSON object with a 'grants' array; each grant must include the 11 fields specified in the schema. If multiple relevant grants are present, include them all in the array.

CONTENT START
{chunk}
CONTENT END
```

The JSON schema (`grant_json_schema`) enforces the structure and rejects extra properties.

## Grant Classes & Attributes

- **Fields (11 total):** `Grant Name`, `Administering Body`, `Grant Purpose`, `Application Deadline`, `Funding Amount`, `Co-contribution Requirements`, `Eligibility Criteria`, `Assessment Criteria`, `Application Complexity`, `Web Link`, `Level of Complexity`.
- **Level of Complexity Enum:** `Low`, `Moderate`, `Complex`, `Very Complex`, `Varies`, `not found`.
- **Missing Data Handling:** If the source lacks a value, the extractor must literally output `not found`.
- **Deduplication Key:** (`Grant Name`, `Administering Body`, `Application Deadline`), lower-cased. Duplicate rows are logged and dropped.
- **Outputs:** Timestamped `grants_<ts>.json` and `grants_<ts>.csv` in the chosen output directory; feed snapshots saved to subfolders (`arc_raw`, `rda_raw`, `nih_raw`).

## Filters & Scope Rules

- **Scope Keywords:** `"digital health"`, `"healthcare"`, `"health care"`, `"medical"`, `"telehealth"`, `"tele-health"`, `"ehealth"`, `"e-health"`, `"ai"`, `"artificial intelligence"`, `"machine learning"`, `"innovation"`, `"research"`, `"clinical"`, `"synthetic data"`, `"digital workforce"`, `"health workforce"`, `"education"`, `"training"`, `"biomedical"`, `"life science"`, `"health technology"`, `"medtech"`, `"pharma"`.
- **Filtering Logic:** Concatenate Grant Name + Purpose + Eligibility + Assessment, lowercase, and retain records containing at least one keyword. Others are discarded before dedupe/export.
- **Dynamic Page Heuristic:** If a crawled page body is empty or contains strings like “javascript is disabled / enable javascript / this site requires javascript”, the orchestrator enqueues it for Playwright rendering.

## Special-Case Feeds & URL Pipelines

These sources bypass the crawler and are ingested separately before the final dedupe step:

1. **ARC Research Grants (RGS) & NCGP:**  
   - `ARC_FEEDS`: two API endpoints (`/RGS/API/grants` and `/NCGP/API/grants`).  
   - Fetch up to 10 pages of 1,000 records each (`ARC_MAX_PAGES`, `ARC_PAGE_SIZE`).  
   - NCGP feed filters FOR codes (`4602`, `5001`, `31`, `32`, `33`, `39`, `40`, `41`, `42`) and `status="Active"`.  
   - Each entry is mapped through `_map_arc_entry`, which flattens nested `scheme-information` and `grant-priorities` into text fields. Raw responses stored under `outputs/<run>/arc_raw/`.

2. **Research Data Australia (RDA):**  
   - REST call to `https://researchdata.edu.au/registry/services/api/registry/activities/_search?wt=json`.  
   - Payload restricts ANZSRC FOR codes to `["11","10","08","09","06"]`, uses `RDA_PAGE_SIZE=100`, and paginates until exhaustion.  
   - Request headers emulate Chromium (`User-Agent`, `X-Requested-With`, Referer). Raw responses written to `outputs/<run>/rda_raw/`.

3. **NIH RSS Feeds:**  
   - `https://grants.nih.gov/grants/guide/rssfiles/PA.xml`, `RFA.xml`, `NOT.xml`.  
   - Parsed via `xml.etree.ElementTree`. Each entry becomes a pseudo-grant mapped into the 11-field schema. Raw XML saved to `outputs/<run>/nih_raw/`.

Each feed is filtered with the same keyword list before being merged with crawler-derived data.

## Seeds & Crawl Behaviour

- `seeds.txt` lists HTTPS URLs (one per line, `#` comments supported). CLI also accepts `--urls`.
- BFS stays in the original domain, normalising URLs to avoid duplicates (adds trailing slash when safe, preserves query strings).
- Links that look like pagination (keywords such as `next`, `page=`, `load-more`, etc.) are eagerly followed to capture catalogue-style listings.

## Known Constraints

- Requires a valid `OPENAI_API_KEY` at runtime; extraction agent refuses to start without it.
- Costs scale with chunks × tokens (~3,500 chars per chunk, `max_output_tokens=4000` per request).
- Em dash avoidance and Australian English tone are enforced in the system prompt.

This snapshot should give future developers enough context on the original system’s behaviour, prompts, classifications, and bespoke feed handling.

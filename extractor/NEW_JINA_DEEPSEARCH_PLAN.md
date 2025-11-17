# New Project Blueprint: DeepSearch-First Grant Discovery

This plan describes how to rebuild the grant pipeline in a fresh folder using Jina AI’s hosted stack (DeepSearch + MCP tools) instead of our bespoke crawler/OpenAI agents.

## Vision & Success Criteria

**Goal:** Replace all local scraping, HTML-to-Markdown, and manual prompt engineering with Jina-hosted services that can search, read, reason, and emit the 11-field grant schema with minimal glue code.

We succeed when:
- Every targeted grant source is reachable via DeepSearch or Reader without local headless browsers.
- The pipeline consumes a list of intents (seed prompts, keyword filters, or domain lists) and produces the same JSON/CSV grant schema.
- MCP tools cover ad-hoc extras (screenshots, timestamp detection, arXiv-only passes) without custom scripts.

## Reference Architecture

```
deepsearch-pipeline/
├─ config/
│  ├─ prompts/                    # YAML describing question templates & scope
│  ├─ domains_whitelist.json      # Domain prioritisation for DeepSearch
│  └─ schema.json                 # 11-field grant schema for validation
├─ src/
│  ├─ deepsearch_client.py        # Thin wrapper over https://deepsearch.jina.ai/v1/chat/completions
│  ├─ workflow.py                 # Orchestrates queries → responses → grant parsing
│  ├─ postprocess.py              # Scope filtering, dedupe, validation
│  ├─ outputs.py                  # Writers for JSON/CSV + raw traces
│  └─ mcp_tools.py                # Optional helpers calling jina-mcp-server (read_url, parallel_search_web)
├─ data/
│  └─ seeds.json                  # List of search intents (queries, domain filters, optional budgets)
├─ docs/
│  └─ operations.md               # Runbooks, monitoring, rate-limit notes
└─ scripts/
   └─ run_pipeline.py             # CLI entrypoint
```

## Implementation Plan

### Phase 0 – Environment & Access
1. Create `deepsearch_pipeline/` folder and initialise a clean virtual environment.
2. Store `JINA_API_KEY` (for DeepSearch + MCP) and `OPENAI_API_KEY` only if fallback models are needed.
3. Copy `JINA_MCP_INSTALLATION_GUIDE.md` into the new folder’s docs for quick reference.
4. Smoke-test both:
   - `curl https://deepsearch.jina.ai/v1/chat/completions ...`
   - `cmd> codex mcp call jina-mcp-server read_url ...`

### Phase 1 – DeepSearch Client Layer
1. Implement `deepsearch_client.py`:
   - Thin wrapper using `requests` or `httpx`.
   - Accepts parameters surfaced on https://jina.ai/deepsearch/ (e.g. `model`, `stream`, `reasoning_effort`, `budget_tokens`, `max_attempts`, `agentic_team_size`).
   - Support optional structured-output schemas for the 11 grant fields.
   - Parse streaming chunks to capture reasoning traces + visited URLs.
2. Unit-test the client with mocked responses (fixtures saved under `tests/fixtures/deepsearch`).

### Phase 2 – Intent & Query Design
1. Define `data/seeds.json` entries like:
   ```json
   {
     "query": "current Australian digital health grant opportunities",
     "reasoning_effort": "high",
     "budget_tokens": 120000,
     "good_domains": ["business.gov.au", "health.gov.au", "grants.gov.au"],
     "only_domains": [],
     "max_returned_urls": 12
   }
   ```
2. Add templates for recurring tasks (ARC feeds, Research Data Australia, NIH):
   - Use `only_domains` or `good_domains` to bias DeepSearch towards official portals.
   - For arXiv-style needs, toggle `arxiv_optimized_search`.

### Phase 3 – Response Parsing & Schema Enforcement
1. Request structured output by sending a JSON schema identical to the legacy `grant_json_schema`.
2. Validate each chunk using `jsonschema` to reject malformed entries before aggregation.
3. Record metadata per run:
   - Prompt tokens vs. search tokens vs. answer tokens (from DeepSearch usage section).
   - `visited_urls` summary, reasoning steps text, and failure diagnostics.

### Phase 4 – Scope Filtering & Deduplication
1. Re-use the existing keyword list (digital health + AI + workforce, etc.) as a config file.
2. Filter each grant by scanning the same text fields as before (Name/Purpose/Eligibility/Assessment); keep the logic configurable for future changes.
3. Deduplicate with the same tuple key to maintain continuity with historical exports.

### Phase 5 – MCP Tool Integrations (Optional but Powerful)
1. Add helper functions in `mcp_tools.py` that talk to `jina-mcp-server` for:
   - `parallel_search_web` when you want deterministic coverage of known sites.
   - `read_url` for deterministic conversions of tricky URLs (e.g. PDF guidelines, single-page applications that DeepSearch might summarise too aggressively).
   - `capture_screenshot_url` when reviewers need visual confirmation.
2. Allow workflows to mix DeepSearch (broad reasoning) with targeted MCP calls (precise scraping) depending on the intent definition.

### Phase 6 – Outputs & Observability
1. Mirror the legacy export format (JSON + CSV) so downstream consumers remain unaffected.
2. Persist DeepSearch transcripts (`reasoning.log` per run) alongside outputs to aid audits.
3. Track latency per query and implement exponential backoff if you hit 524 timeout thresholds (ensure `stream=true` as per the docs).

### Phase 7 – Testing & QA
1. Add integration tests that replay canned DeepSearch responses and ensure the parser + filter pipeline reproduces expected grants.
2. Run parallel comparisons (legacy vs. DeepSearch) on a sample of sites to validate coverage.
3. Document operational runbooks (token budgeting strategy, rate-limit dashboards, fallback procedures) in `docs/operations.md`.

## How Each Requirement Is Covered

| Legacy Need | Jina Replacement | Notes |
| --- | --- | --- |
| Web scraping + HTML → Markdown | `read_url`, `parallel_read_url`, MCP `capture_screenshot_url` | Reader outputs clean markdown/JSON; no custom parser needed. |
| Discovery of fresh grants | DeepSearch with `reasoning_effort` and `good_domains` | Use multi-step reasoning to combine SERP search + site reading + summarisation. |
| Domain-specific feeds (ARC/RDA/NIH) | DeepSearch intents targeting those domains, optionally paired with `read_url` of API docs | For APIs requiring POST flow, either keep lightweight fetchers or instruct DeepSearch to consult documentation first. |
| Deduplication & schema enforcement | Structured outputs + local validator | Maintains continuity with analytics consumers. |
| Manual review aids | `capture_screenshot_url`, `guess_datetime_url`, `primer` | Provide metadata to analysts without manual browsing. |

## Rollout Checklist

1. ✅ Decide on repository structure and initialise `deepsearch-pipeline`.
2. ☐ Obtain/secure `JINA_API_KEY`; set up MCP in Codex + VS Code (see installation guide).
3. ☐ Build DeepSearch client + tests.
4. ☐ Encode legacy prompts/filters into config files.
5. ☐ Implement workflow orchestration + output writers.
6. ☐ Run pilot against a small seed set; compare with final legacy export.
7. ☐ Iterate on prompts (`no_direct_answer`, `arxiv_optimized_search`, structured output) until the schema is consistently filled.
8. ☐ Document runbooks, cost expectations, and failure-handling strategies.

Following this plan will let us stand up a new grant extraction system that leans entirely on Jina’s hosted capabilities while preserving the structured outputs and domain focus that stakeholders need.

# Architecture & Design — ComplianceRadar-Scanner v2.1

## 1. High-Level Architecture

```mermaid
flowchart LR
    subgraph Sources["Regulatory Sources (UAE, KSA, MENAT, SA)"]
        Portals["40+ Seed Regulator Portals\n(CBUAE, VARA, DFSA, ADGM, SAMA, NCA, SDAIA, CST...)"]
        Manual["Manually Added Links\n(Custom URLs & Circulars)"]
        Horizon["Boolean Horizon RSS Feeds\n(Tech, AI, Cyber, BCM/DR, Crypto, Open Banking)"]
    end

    subgraph Engine["ComplianceRadar-Scanner Core"]
        Scraper["Scraper Engine\n(scraper/engine.py)"]
        LLMAdapter["Portable LLM Adapter\n(llm/provider.py)\nGemini | AWS Bedrock | OpenAI | Deterministic"]
        DB[("SQLite / PostgreSQL\n(db/database.py)\nregulations, monitored_sources,\nscan_runs, email_subscribers")]
    end

    subgraph Outputs["Interfaces & Downstream Integrations"]
        UI["5-Tab Enterprise Web UI\n(static/index.html)"]
        Reports["Report Generator\n(CSV / Printable PDF-HTML / Strict JSON)"]
        Email["Weekly Corporate Email Digest\n(SMTP / AWS SES)"]
        ExtAPI["Secure External API & Webhook\n(Bearer + HMAC-SHA256)\n-> Compliance IQ & Phase 2 Mobile App"]
    end

    Portals --> Scraper
    Manual --> Scraper
    Horizon --> Scraper
    Scraper <--> LLMAdapter
    Scraper --> DB
    DB <--> UI
    DB --> Reports
    DB --> Email
    DB --> ExtAPI
```

## 2. Core Modules
- **`config/jurisdictions.yaml`**: Declarative taxonomy for Regions (`MENAT`, `GCC`, `Levant & North Africa`, `Sub-Saharan Africa`), Sectors, Regulation/Standard types, and per-country seed authorities and boolean queries (with `UAE` and `KSA` enabled by default).
- **`llm/provider.py`**: Implements `BaseLLMAdapter` with `BedrockLLMAdapter` (`boto3` `converse` API), `GeminiLLMAdapter`, `OpenAICompatibleAdapter`, and `DeterministicRuleExtractor`.
- **`scraper/engine.py`**: Implements `RegulatoryScannerEngine` for scoped scanning (`run_scan`), single-URL scraping (`scrape_single_source_url`), report generation (`generate_csv_report`, `generate_executive_html_report`), and weekly corporate email dispatch (`send_weekly_corporate_digest`).
- **`db/database.py`**: Persistence layer managing `regulations`, `monitored_sources`, `scan_runs`, `discovered_authorities`, `email_subscribers`, and `email_digest_logs`.
- **`app.py`**: FastAPI application exposing REST endpoints, background scheduler loop, and HMAC-SHA256 authentication.

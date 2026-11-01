# MASTER PROMPT & SPECIFICATION FOR AWS KIRO AGENT
# Project: ComplianceRadar-Scanner v2.1 (Enterprise Regulatory Intelligence & Compliance IQ Engine)

> **Instructions for AWS Kiro:**  
> Use this specification to understand, extend, deploy, or generate `.kiro/specs/` (`requirements.md`, `design.md`, `tasks.md`) for **ComplianceRadar-Scanner**. The baseline codebase is already implemented in this repository (`app.py`, `cli.py`, `config/jurisdictions.yaml`, `llm/provider.py`, `scraper/engine.py`, `db/database.py`, `db/seed_data.py`, `static/index.html`).

---

## 1. SYSTEM ROLE & ARCHITECTURE OBJECTIVE
You are **ComplianceRadar-Scanner**, an enterprise-grade regulatory scanning, scraping, normalization, and compliance ingestion engine.  
Your purpose is to autonomously discover, crawl, ingest, normalize, and extract regulatory updates, circulars, frameworks, standards, enforcement guidelines, consultation papers, and regulatory news across the **MENAT region (UAE, Saudi Arabia / KSA, Qatar, Bahrain, Kuwait, Oman, Egypt, Turkey, Jordan)** and **South Africa**, with **UAE** and **Saudi Arabia (KSA)** fully active and pre-populated.

---

## 2. FUNCTIONAL REQUIREMENTS (EARS FORMAT FOR AWS KIRO)

### Requirement 1: Multi-Level Scoped Scanning & Filtering (1.a)
- **WHEN** a user selects any combination of **Region** (`MENAT`, `GCC`, `Levant & North Africa`, `Sub-Saharan Africa / South Africa`), **Country** (`UAE`, `KSA`, `Qatar`, `Bahrain`, `Kuwait`, `Oman`, `Egypt`, `Turkey`, `Jordan`, `South Africa`), **Sector** (`Banking & Central Banking`, `Virtual Assets, Crypto & Blockchain`, `Capital Markets & Wealth Management`, `Insurance & Takaful`, `Payments, Open Banking & FinTech`, `Cybersecurity & Critical Infrastructure`, `Data Privacy, AI & Cloud Computing`, `Telecommunications & Digital Government`), and **Regulation / Standard Level** (`Regulation`, `Standard`, `Framework`, `Circular`, `Rulebook`, `Guideline`, `Directive`, `Law`, `News`), **THE SYSTEM SHALL** filter the live regulatory feed and allow initiating a targeted on-demand scan (`POST /api/v1/scan`) for that exact scope.

### Requirement 2: Manual Link Ingestion & Re-Scanning (1.b)
- **WHEN** an administrator or user submits a custom URL (`https://...`) via the UI (`Tab 2`) or API (`POST /api/v1/sources`) with its Region, Country, Sector, Regulation/Standard name, and Issuing Authority, **THE SYSTEM SHALL** persist the link in the `monitored_sources` table, optionally trigger an immediate scrape (`POST /api/v1/sources/{source_id}/scan`), and include it in future periodic background scans.

### Requirement 3: Filterable Monitored Sources Directory (1.c)
- **WHEN** a user opens the **Monitored Sources Directory (`Tab 2`)**, **THE SYSTEM SHALL** display all official seed regulator portals (40+ across UAE, KSA, MENAT, and South Africa) and manually added links, filterable by **Region, Country, Sector, Source Origin (`Seed` vs `Manual`), and Regulation/Standard**, showing last scan timestamps, HTTP/extraction status, and total items extracted.

### Requirement 4: Cross-Domain Technology, Risk & Financial Coverage
- **THE SYSTEM SHALL** monitor both direct technology regulations and non-tech regulations that overlap with technology, data, or operational risk across:
  - **Core Technology Domains:** Artificial Intelligence (`AI`), Machine Learning (`ML`), Generative AI, Emerging Tech, Blockchain / DLT, Quantum Computing & Post-Quantum Cryptography, Cybersecurity, Data Privacy (`PDPL` / `POPIA`), Cloud Computing & Data Localization, Digital Assets.
  - **Financial & Operational Infrastructure:** Central Banking, FinTech, Open Banking / Open Finance (`AISP` / `PISP`), Payments, Crypto / Virtual Assets (`VASP` / `CASP`), Digital Currency (`CBDC`, Stablecoins, Payment Tokens), Operational Resilience (`CORF`, `DORA`-aligned rules), Disaster Recovery (`DR`), Business Continuity Management (`BCM`), Operational Risk, Third-Party / ICT Vendor Governance.
- **THE SYSTEM SHALL** dynamically detect unlisted or newly formed authorities, ministries, or councils outside the seed list and flag `"is_new_authority_discovered": true`.

### Requirement 5: Zero-Hallucination Extraction & Portable AI Stack (AWS Bedrock + Gemini)
- **THE SYSTEM SHALL** enforce a strict zero-hallucination policy: if a publication date, enforcement date, or URL is missing from the source text, the extractor **MUST** output `"N/A"`.
- **THE SYSTEM SHALL** maintain a portable **LLM Provider Adapter (`llm/provider.py`)** supporting seamless switching via `LLM_PROVIDER`:
  - `bedrock` — **AWS Bedrock** (`boto3` `bedrock-runtime` Converse API supporting Anthropic Claude 3.5/3.7 Sonnet, Amazon Nova Pro/Lite, Meta Llama 3/4, Mistral).
  - `gemini` — **Google Gemini** (`google-genai` / REST API).
  - `openai_compatible` — Any OpenAI-compatible endpoint.
  - `deterministic` — Built-in zero-cost regex/taxonomy rule engine fallback.

### Requirement 6: Secure External Platform API (Compliance IQ Integration) (2)
- **WHEN** an external platform (such as **Compliance IQ**) requests regulatory data from `GET /api/v1/external/feed`, **THE SYSTEM SHALL** authenticate the caller via `X-API-Key` or `Authorization: Bearer <COMPLIANCE_IQ_API_SECRET>` and sign the JSON response with an `X-ComplianceRadar-Signature: sha256=<hmac>` header.
- **WHEN** pushing updates outbound (`POST /api/v1/compliance-iq/push`), **THE SYSTEM SHALL** sign the webhook payload with HMAC-SHA256 using `COMPLIANCE_IQ_API_SECRET`.

### Requirement 7: Downloadable Scan Reports (3)
- **WHEN** a user requests a report from the interface or `GET /api/v1/reports/download?format=csv|html|json`, **THE SYSTEM SHALL** generate and download a scoped report in:
  1. **CSV / Excel** (`format=csv`)
  2. **Executive Printable HTML / Save-as-PDF** (`format=html`)
  3. **Strict Schema JSON** (`format=json`)

### Requirement 8: Weekly Corporate Email Digest for Colleagues (4)
- **THE SYSTEM SHALL** allow subscribing colleagues via their corporate email address with custom Region, Country, and Sector filters (`POST /api/v1/email-digest/subscribers`) and dispatch a formatted HTML Weekly Corporate Regulatory Briefing (`POST /api/v1/email-digest/send-now`) via corporate SMTP or AWS SES.

### Requirement 9: Phase 2 Roadmap (iOS & Android Mobile App Readiness) (5)
- **WHERE** Phase 2 mobile app development is initiated, **THE SYSTEM SHALL** expose stateless, token-authenticated REST endpoints (`/api/v1/external/feed`, `/api/v1/status`, `/api/v1/regulations`, `/api/v1/sources`) ready for consumption by an iOS/Android client (Flutter / React Native / AWS Amplify).

---

## 3. UAE & SAUDI ARABIA (KSA) REGULATORY ONTOLOGY (PRE-CONFIGURED)

### United Arab Emirates (`UAE`)
- **Terms:** `UAE`, `United Arab Emirates`, `Federal Decree-Law`, `Cabinet Resolution`, `Ministerial Decision`, `Official Gazette`, `Mainland`, `Free Zone`.
- **Regulators:**
  - `CBUAE` — Central Bank of the UAE (Payment Token Services Regulation, Open Finance Regulation, Operational Resilience & Risk, Model Management Standards / AI Guidance)
  - `VARA` — Virtual Assets Regulatory Authority (Dubai VASP Rulebooks, Digital Operational Resilience)
  - `DFSA` — Dubai Financial Services Authority (DIFC Crypto Token Regime, Cyber Risk, AI Governance)
  - `ADGM / FSRA` — Financial Services Regulatory Authority (ADGM Cyber Risk Management Framework, Virtual Assets)
  - `TDRA` — Telecommunications and Digital Government Regulatory Authority
  - `UAE Cyber Security Council (CSC)` — National Encryption Policy, Post-Quantum Cryptography, IAS v2
  - `DESC` — Dubai Electronic Security Center (ISR, Cloud & AI Security)
  - `UAE Data Office` — Federal Personal Data Protection Law (Decree-Law No. 45 of 2021)
  - `DIFC Commissioner of Data Protection` — DIFC DP Law Regulation 10 (Autonomous & AI Systems)
  - `SCA / CMA` — Securities and Commodities Authority / Capital Market Authority

### Kingdom of Saudi Arabia (`KSA`)
- **Terms:** `KSA`, `Saudi Arabia`, `Royal Decree`, `Council of Ministers Resolution`, `Circular`, `Controls`, `Framework`, `Umm Al-Qura Gazette`.
- **Regulators:**
  - `SAMA` — Saudi Central Bank (SAMA Cyber Security Framework CSF, Cloud Subdomain 3.4.3, BCM Framework, Open Banking Framework AISP/PISP)
  - `NCA` — National Cybersecurity Authority (`ECC-2:2024`, Cloud Cybersecurity Controls `CCC`, Critical Systems `CSCC`, OT `OTCC`)
  - `SDAIA / NDMO` — Saudi Data and Artificial Intelligence Authority (Saudi `PDPL`, Cross-Border Data Transfer Rules, Generative AI & AI Ethics Principles)
  - `CST` — Communications, Space and Technology Commission (Data Center Services Regulations, Cloud Computing Regulatory Framework `CCRF`)
  - `CMA` — Capital Market Authority (Cybersecurity Guidelines for Capital Market Institutions, FinTech ExPermit)
  - `DGA` — Digital Government Authority (Digital Government Regulatory Framework, Cloud-First Policy)
  - `IA` — Insurance Authority (Saudi Insurance Cybersecurity & InsurTech Regulations)
  - `ZATCA` — Zakat, Tax and Customs Authority (FATOORA E-Invoicing Phase 2 API & Cryptographic Standards)

---

## 4. STRICT OUTPUT JSON SCHEMA
All exports (`GET /api/v1/export/strict-json` and `GET /api/v1/external/feed`) must strictly conform to:

```json
{
  "scanned_articles": [
    {
      "title": "Exact title of the regulation, standard, or news piece",
      "region": "GCC / Levant & North Africa / Sub-Saharan Africa (South Africa)",
      "jurisdiction": "UAE / KSA / South Africa / etc.",
      "sector": "Banking & Central Banking / Virtual Assets, Crypto & Blockchain / etc.",
      "regulation_standard": "Regulation / Standard / Framework / Circular / Rulebook",
      "issuing_authority": "Name of the regulator (e.g., CBUAE, SAMA, NCA, SDAIA, VARA)",
      "publication_date": "YYYY-MM-DD or N/A",
      "enforcement_date": "YYYY-MM-DD or N/A",
      "domain_tags": ["Artificial Intelligence (AI)", "Operational Resilience", "Crypto/Virtual Assets"],
      "summary": "Concise, factual summary of the update.",
      "impacted_entities": ["Banks", "Cloud Providers", "VASP"],
      "source_url": "Exact URL or N/A",
      "is_new_authority_discovered": false
    }
  ],
  "recommended_api_integrations": [
    {
      "api_name": "Name of the API service",
      "provider_type": "Free / Paid",
      "description": "What data this API provides that isn't easily scraped",
      "documentation_url": "URL to API docs or N/A"
    }
  ],
  "execution_metadata": {
    "new_authorities_discovered": ["List of regulators found outside the seed list or N/A"],
    "hallucination_check": "Passed - All missing data marked as N/A"
  }
}
```

---

## 5. NEXT-STAGE AWS KIRO ENHANCEMENT TASKS
When continuing development in **AWS Kiro**, prioritize these tasks:
1. **AWS Bedrock Native Configuration:** Switch `.env` to `LLM_PROVIDER=bedrock` using IAM Role / `boto3` credentials with `anthropic.claude-3-5-sonnet-20241022-v2:0` or `amazon.nova-pro-v1:0`.
2. **Headless Browser & PDF Deep-Crawler:** Extend `scraper/engine.py` with Playwright + `pypdf`/`pdfplumber` (or Amazon Textract) to parse full multi-page PDF circulars linked from CBUAE, SAMA, NCA, and SDAIA portals.
3. **AWS Cloud Deployment:** Package the FastAPI + Background Scheduler app with a `Dockerfile` for deployment on **AWS App Runner / ECS Fargate**, backed by **Amazon RDS (PostgreSQL)**, **Amazon EventBridge** (for scheduled scans and Monday 08:30 GST weekly digests), and **Amazon SES** (for corporate email delivery).
4. **Phase 2 Mobile App (iOS & Android):** Scaffold a Flutter or React Native mobile client consuming the authenticated `/api/v1/external/feed` and `/api/v1/status` endpoints with push notification alerts for high-priority UAE & KSA circulars.

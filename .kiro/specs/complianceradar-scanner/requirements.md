# Requirements Document — ComplianceRadar-Scanner v2.1

## Introduction
**ComplianceRadar-Scanner** is an enterprise regulatory intelligence engine covering the MENAT region (with UAE and Saudi Arabia/KSA active by default) and South Africa. It discovers, scrapes, normalizes, and extracts regulatory updates across Technology, Data, Cybersecurity, AI/ML, Quantum, Cloud, BCM/DR, Operational Resilience, Crypto/Virtual Assets, and Open Banking, serving both an interactive web dashboard and a signed REST/Webhook API for the downstream **Compliance IQ** platform.

## Requirements

### Requirement 1: Multi-Level Scoped Regulatory Scanning
**User Story:** As a Compliance Officer, I want to initiate scans and filter results at the Region, Country, Sector, and Regulation/Standard levels, so that I can focus on specific jurisdictions such as UAE and Saudi Arabia (KSA).
1. WHEN a user selects a Region, Country, Sector, or Regulation/Standard filter in the UI, THE SYSTEM SHALL filter the displayed regulatory feed in real time.
2. WHEN a user clicks "Initiate Scan for Selected Scope", THE SYSTEM SHALL execute horizon queries and regulator portal probes scoped to the selected Region, Country, Sector, and Regulation/Standard level.

### Requirement 2: Manual Link Ingestion & Source Directory
**User Story:** As a Compliance Analyst, I want to manually add custom URLs to scan and view a filterable directory of all monitored sources, so that I have full visibility and control over where regulatory intelligence is gathered.
1. WHEN a user submits a manual URL with Country, Sector, and Regulation/Standard metadata via `POST /api/v1/sources`, THE SYSTEM SHALL store the link in `monitored_sources` and optionally scan it immediately.
2. WHEN a user views the Monitored Sources Directory, THE SYSTEM SHALL allow filtering all seed and manual sources by Region, Country, Sector, Origin (`Seed` vs `Manual`), and Regulation/Standard.

### Requirement 3: Portable AI Extraction (Gemini & AWS Bedrock) with Zero Hallucination
**User Story:** As a Platform Architect, I want the AI extraction layer to be portable across Google Gemini and AWS Bedrock with strict anti-hallucination rules, so that we avoid vendor lock-in and never fabricate regulatory dates.
1. WHERE `LLM_PROVIDER=bedrock` is configured, THE SYSTEM SHALL invoke AWS Bedrock via `boto3` `bedrock-runtime` Converse API.
2. WHERE `LLM_PROVIDER=gemini` is configured, THE SYSTEM SHALL invoke Google Gemini.
3. IF a publication date, enforcement date, or URL is absent from the source text, THEN THE SYSTEM SHALL output `"N/A"`.

### Requirement 4: Secure External Platform API (Compliance IQ)
**User Story:** As an Integration Engineer, I want a secure API and signed webhook dispatcher, so that the separate Compliance IQ platform can safely ingest regulatory updates.
1. WHEN an external client calls `GET /api/v1/external/feed`, THE SYSTEM SHALL verify the `X-API-Key` or `Authorization: Bearer` token and return an `X-ComplianceRadar-Signature` HMAC-SHA256 header.
2. WHEN `POST /api/v1/compliance-iq/push` is triggered, THE SYSTEM SHALL sign the payload with HMAC-SHA256 and dispatch it to the configured Compliance IQ webhook URL.

### Requirement 5: Downloadable Reports & Weekly Corporate Email Digest
**User Story:** As a Compliance Manager, I want to download scan reports and automatically share weekly regulatory updates with colleagues via corporate email.
1. WHEN a user requests a report download (`GET /api/v1/reports/download`), THE SYSTEM SHALL generate the scoped report in CSV, Executive Printable HTML/PDF, or Strict JSON format.
2. WHEN the weekly digest is triggered (`POST /api/v1/email-digest/send-now` or scheduled run), THE SYSTEM SHALL compile the latest updates and dispatch an HTML briefing to subscribed corporate emails via SMTP/SES.

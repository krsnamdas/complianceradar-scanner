# ComplianceRadar-Scanner

Enterprise-grade autonomous regulatory scanning, scraping, extraction, and compliance intelligence engine covering the **MENAT region (UAE, KSA, Qatar, Bahrain, Kuwait, Oman, Egypt, Turkey, Jordan)** and **South Africa**, with **UAE** configured as the Phase 1 validation testbed.

---

## Key Architecture Highlights

1. **UAE Phase 1 Testbed + Full MENAT & South Africa Ontology (`config/jurisdictions.yaml`)**
   - Pre-configured with UAE federal and free-zone regulators (`CBUAE`, `VARA`, `DFSA/DIFC`, `ADGM/FSRA`, `TDRA`, `UAE Cyber Security Council`, `DESC`, `UAE Data Office`, `DIFC Commissioner of Data Protection`, `SCA/CMA`) and ready-to-enable profiles for `KSA`, `Qatar`, `Bahrain`, `Kuwait`, `Oman`, `Egypt`, `Turkey`, `Jordan`, and `South Africa`.
   - Dynamically detects and records newly formed councils, ministries, or authorities outside the seed list (`is_new_authority_discovered: true`).

2. **Portable AI Extraction Layer — Zero Vendor Lock-In (`llm/provider.py`)**
   - Switch between **Google Gemini**, **AWS Bedrock** (Claude 3.5/3.7 Sonnet, Amazon Nova, Meta Llama via `boto3` `converse` API), **OpenAI-compatible models**, or the built-in **Deterministic Rule Engine** via a single environment variable (`LLM_PROVIDER`) or directly inside the Dashboard UI.
   - Enforces strict anti-hallucination rules: any missing publication date, enforcement timeline, or URL is populated strictly as `"N/A"`.

3. **Background Periodic Daemon + Live Dashboard (`app.py`, `static/index.html`)**
   - Built-in asyncio background scheduler runs periodic horizon scans and regulator portal probes automatically.
   - Interactive web dashboard to filter regulations by Jurisdiction, Authority, Cross-Domain Tag (`AI`, `ML`, `Cybersecurity`, `Operational Resilience`, `BCM`, `DR`, `Crypto`, `Open Banking`, `Cloud`, `Quantum`), inspect obligations, trigger on-demand scans, and view/download the strict JSON schema.

4. **Downstream "Compliance IQ" Feeder API**
   - Push normalized regulatory intelligence directly to your **Compliance IQ** platform via `POST /api/v1/compliance-iq/push` or pull via `GET /api/v1/export/strict-json`.

---

## Quick Start

### 1. Run a Live UAE Scan via CLI
```powershell
.\.venv\Scripts\python.exe cli.py --jurisdictions UAE --output data/uae_strict_output.json
```

### 2. Launch the Background Scanner & Dashboard Server
```powershell
.\.venv\Scripts\python.exe app.py
```
Then open **`http://127.0.0.1:8080`** in your browser.

---

## Porting from Google Gemini to AWS Bedrock
No code changes are required to move from Gemini/Antigravity to AWS Bedrock. Simply update `.env` (or select **AWS Bedrock** in the Dashboard settings modal):

```env
LLM_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

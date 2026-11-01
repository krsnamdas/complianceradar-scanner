"""
Portable Model-Agnostic LLM Provider & Extraction Layer.

Supports seamless switching across:
1. `gemini`            — Google Gemini via `google-genai` SDK (Antigravity / Vertex / AI Studio)
2. `bedrock`           — AWS Bedrock via `boto3` (`bedrock-runtime` Converse API: Claude, Nova, Llama, Mistral)
3. `openai_compatible` — Any OpenAI-compatible endpoint (OpenAI, Azure, vLLM, Ollama)
4. `deterministic`     — Zero-dependency rule & regex extraction engine (automatic fallback when no API keys are set)

Strict Zero-Hallucination Policy:
Missing dates, URLs, or fields MUST be returned as "N/A".
"""

from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


EXTRACTION_SYSTEM_PROMPT = """You are ComplianceRadar-Scanner, an enterprise-grade zero-hallucination regulatory extraction engine.
Given raw text/metadata from a regulatory circular, news notice, or regulator webpage, extract a single JSON object matching this exact schema:
{
  "title": "Exact title of the regulation, standard, circular, or news piece",
  "jurisdiction": "UAE / KSA / Qatar / Bahrain / Kuwait / Oman / Egypt / Turkey / Jordan / South Africa",
  "issuing_authority": "Exact regulator name (e.g., Central Bank of the UAE (CBUAE), VARA, DFSA, ADGM FSRA, TDRA, etc.) or 'N/A'",
  "document_type": "Regulation | Circular | Framework | Guideline | Rulebook | Law | Consultation | News",
  "publication_date": "YYYY-MM-DD or N/A",
  "enforcement_date": "YYYY-MM-DD or N/A",
  "domain_tags": ["AI", "Cybersecurity", "Operational Resilience", "Crypto/Virtual Assets", "Data Privacy", "Cloud Computing", "Open Finance", "Business Continuity (BCM)", "Disaster Recovery (DR)", "Operational Risk", "Quantum Computing"],
  "summary": "Concise, factual summary based strictly on the provided text.",
  "compliance_obligations": ["Actionable compliance requirement 1", "Requirement 2"],
  "impacted_entities": ["Banks", "VASP", "Cloud Providers", "Insurance Companies", "Fintechs"],
  "source_url": "Exact URL or N/A",
  "is_new_authority_discovered": true or false
}
STRICT ANTI-HALLUCINATION RULES:
1. Never guess or fabricate dates, URLs, or obligations.
2. If enforcement_date or publication_date is not explicitly stated in the input, output "N/A".
3. Return ONLY valid JSON without markdown fences.
"""


class BaseLLMAdapter(ABC):
    provider_name: str = "base"

    @abstractmethod
    def extract_regulation(
        self,
        raw_title: str,
        raw_text: str,
        source_url: str,
        jurisdiction: str,
        published_hint: Optional[str],
        seed_authority_codes: List[str],
    ) -> Dict[str, Any]:
        raise NotImplementedError


class DeterministicRuleExtractor(BaseLLMAdapter):
    """
    High-precision deterministic NLP/keyword & regex extractor.
    Used when LLM_PROVIDER=deterministic or as an automatic zero-downtime fallback
    when cloud LLM credentials (GEMINI_API_KEY / AWS credentials) are not yet configured.
    """

    provider_name = "deterministic"

    AUTHORITY_PATTERNS = {
        "UAE": [
            (r"\b(CBUAE|Central Bank of the (UAE|United Arab Emirates))\b", "Central Bank of the UAE (CBUAE)", False),
            (r"\b(VARA|Virtual Assets Regulatory Authority)\b", "Virtual Assets Regulatory Authority (VARA)", False),
            (r"\b(DFSA|Dubai Financial Services Authority)\b", "Dubai Financial Services Authority (DFSA - DIFC)", False),
            (r"\b(ADGM|FSRA|Financial Services Regulatory Authority)\b", "Financial Services Regulatory Authority (FSRA - ADGM)", False),
            (r"\b(TDRA|Telecommunications and Digital Government Regulatory Authority)\b", "Telecommunications and Digital Government Regulatory Authority (TDRA)", False),
            (r"\b(Cyber Security Council|CSC)\b", "UAE Cyber Security Council", False),
            (r"\b(DESC|Dubai Electronic Security Center)\b", "Dubai Electronic Security Center (DESC)", False),
            (r"\b(UAE Data Office)\b", "UAE Data Office", False),
            (r"\b(DIFC.*Data Protection|Commissioner of Data Protection)\b", "DIFC Commissioner of Data Protection", False),
            (r"\b(SCA|Securities and Commodities Authority|Capital Market Authority)\b", "Securities and Commodities Authority / Capital Market Authority (UAE)", False),
            (r"\b(Ministry of Economy|MoE)\b", "UAE Ministry of Economy", True),
            (r"\b(Ministry of Finance|MoF)\b", "UAE Ministry of Finance", True),
            (r"\b(Ministry of Industry and Advanced Technology|MoIAT)\b", "UAE Ministry of Industry and Advanced Technology (MoIAT)", True),
            (r"\b(Digital Dubai|Dubai Digital Authority)\b", "Digital Dubai Authority", True),
            (r"\b(Artificial Intelligence.*Council|AI Office)\b", "UAE Council for Artificial Intelligence and Blockchain", True),
        ],
        "KSA": [
            (r"\b(SAMA|Saudi Central Bank)\b", "Saudi Central Bank (SAMA)", False),
            (r"\b(NCA|National Cybersecurity Authority)\b", "National Cybersecurity Authority (NCA)", False),
            (r"\b(SDAIA|NDMO|Saudi Data and Artificial Intelligence Authority|National Data Management Office)\b", "Saudi Data and Artificial Intelligence Authority (SDAIA / NDMO)", False),
            (r"\b(CST|CITC|Communications, Space and Technology Commission)\b", "Communications, Space and Technology Commission (CST)", False),
            (r"\b(CMA|Capital Market Authority)\b", "Capital Market Authority (CMA)", False),
            (r"\b(DGA|Digital Government Authority)\b", "Digital Government Authority (DGA)", False),
            (r"\b(Insurance Authority|IA)\b", "Insurance Authority (IA — Saudi Arabia)", True),
            (r"\b(ZATCA|Zakat, Tax and Customs Authority)\b", "Zakat, Tax and Customs Authority (ZATCA)", False),
            (r"\b(MCIT|Ministry of Communications and Information Technology)\b", "Saudi Ministry of Communications and Information Technology (MCIT)", True),
            (r"\b(MISA|Ministry of Investment)\b", "Saudi Ministry of Investment (MISA)", True),
        ],
        "Qatar": [
            (r"\b(QCB|Qatar Central Bank)\b", "Qatar Central Bank (QCB)", False),
            (r"\b(QFCRA)\b", "Qatar Financial Centre Regulatory Authority (QFCRA)", False),
            (r"\b(NCSA|National Cyber Security Agency)\b", "National Cyber Security Agency (NCSA)", False),
        ],
        "Bahrain": [
            (r"\b(CBB|Central Bank of Bahrain)\b", "Central Bank of Bahrain (CBB)", False),
        ],
        "Kuwait": [
            (r"\b(CBK|Central Bank of Kuwait)\b", "Central Bank of Kuwait (CBK)", False),
            (r"\b(CITRA)\b", "Communication and Information Technology Regulatory Authority (CITRA)", False),
        ],
        "Oman": [
            (r"\b(CBO|Central Bank of Oman)\b", "Central Bank of Oman (CBO)", False),
            (r"\b(FSA|Financial Services Authority)\b", "Financial Services Authority (FSA Oman)", False),
            (r"\b(MTCIT)\b", "Ministry of Transport, Communications and Information Technology (MTCIT)", False),
        ],
        "Egypt": [
            (r"\b(CBE|Central Bank of Egypt)\b", "Central Bank of Egypt (CBE)", False),
            (r"\b(FRA|Financial Regulatory Authority)\b", "Financial Regulatory Authority (FRA)", False),
        ],
        "Turkey": [
            (r"\b(BDDK|BRSA)\b", "Banking Regulation and Supervision Agency (BDDK)", False),
            (r"\b(SPK|CMB|Capital Markets Board)\b", "Capital Markets Board of Türkiye (SPK)", False),
            (r"\b(TCMB|CBRT)\b", "Central Bank of the Republic of Türkiye (TCMB)", False),
            (r"\b(KVKK)\b", "Personal Data Protection Authority (KVKK)", False),
        ],
        "Jordan": [
            (r"\b(CBJ|Central Bank of Jordan)\b", "Central Bank of Jordan (CBJ)", False),
        ],
        "South Africa": [
            (r"\b(SARB|South African Reserve Bank|Prudential Authority)\b", "South African Reserve Bank (SARB) / Prudential Authority", False),
            (r"\b(FSCA|Financial Sector Conduct Authority)\b", "Financial Sector Conduct Authority (FSCA)", False),
            (r"\b(Information Regulator|POPIA)\b", "Information Regulator (South Africa)", False),
        ],
    }

    DOMAIN_KEYWORDS = [
        ("Artificial Intelligence (AI)", [r"\bAI\b", r"artificial intelligence", r"generative ai", r"llm", r"autonomous system"]),
        ("Machine Learning (ML)", [r"\bML\b", r"machine learning", r"model risk", r"model management", r"algorithmic"]),
        ("Cybersecurity", [r"cyber", r"information security", r"encryption", r"ransomware", r"soc\b", r"vulnerability", r"penetration test"]),
        ("Data Privacy", [r"data protection", r"pdpl", r"popia", r"kvkk", r"personal data", r"data privacy", r"cross-border data"]),
        ("Cloud Computing", [r"\bcloud\b", r"data center", r"data residency", r"data localization", r"hyperscaler", r"saas"]),
        ("Crypto/Virtual Assets", [r"crypto", r"virtual asset", r"vasp", r"casp", r"token", r"stablecoin", r"digital asset", r"custody"]),
        ("Digital Currency (CBDC)", [r"cbdc", r"central bank digital currency", r"digital dirham", r"digital lira", r"payment token"]),
        ("Blockchain", [r"blockchain", r"distributed ledger", r"\bdlt\b", r"smart contract", r"defi"]),
        ("Quantum Computing", [r"quantum", r"post-quantum", r"\bpqc\b"]),
        ("Open Banking", [r"open banking", r"open finance", r"\baisp\b", r"\bpisp\b", r"api hub", r"nebras"]),
        ("Payments", [r"payment", r"remittance", r"settlement", r"instant payment", r"crowdfunding", r"e-money"]),
        ("Fintech", [r"fintech", r"regtech", r"sandbox", r"digital bank", r"wealthtech", r"insurtech"]),
        ("Operational Resilience", [r"operational resilience", r"cyber resilience", r"corf", r"dora", r"critical operation"]),
        ("Business Continuity (BCM)", [r"business continuity", r"\bbcm\b", r"continuity plan", r"downtime"]),
        ("Disaster Recovery (DR)", [r"disaster recovery", r"\bdr\b", r"recovery time objective", r"failover"]),
        ("Operational Risk", [r"operational risk", r"risk management", r"internal control", r"prudential", r"governance"]),
        ("Third-Party Governance", [r"third-party", r"outsourcing", r"vendor risk", r"supply chain", r"ict risk"]),
        ("Central Banking", [r"central bank", r"monetary", r"cbuae", r"sama", r"qcb", r"cbb", r"cbk", r"sarb"]),
    ]

    def extract_regulation(
        self,
        raw_title: str,
        raw_text: str,
        source_url: str,
        jurisdiction: str,
        published_hint: Optional[str],
        seed_authority_codes: List[str],
    ) -> Dict[str, Any]:
        combined = f"{raw_title}\n{raw_text}"

        # 1. Detect authority
        issuing_authority = "N/A"
        is_new_authority = False
        patterns = self.AUTHORITY_PATTERNS.get(jurisdiction, []) + [
            p for k, plist in self.AUTHORITY_PATTERNS.items() if k != jurisdiction for p in plist
        ]
        for regex, auth_name, is_new in patterns:
            if re.search(regex, combined, re.IGNORECASE):
                issuing_authority = auth_name
                is_new_authority = is_new
                break

        if issuing_authority == "N/A":
            # Look for dynamic "Ministry of ...", "Authority", "Council", "Commission"
            m = re.search(
                r"\b((?:UAE|Saudi|Qatar|Bahrain|Kuwait|Oman|Egypt|Jordan|South African)?\s*(?:Ministry|Authority|Council|Commission|Center|Centre|Bureau|Agency)\s+(?:of|for)\s+[A-Z][A-Za-z\s&]{3,40})",
                combined,
            )
            if m:
                issuing_authority = re.sub(r"\s+", " ", m.group(1)).strip()
                is_new_authority = True

        # 2. Extract domain tags
        domain_tags: List[str] = []
        for tag_name, regex_list in self.DOMAIN_KEYWORDS:
            if any(re.search(rx, combined, re.IGNORECASE) for rx in regex_list):
                domain_tags.append(tag_name)
        if not domain_tags:
            domain_tags = ["Emerging Tech", "Operational Risk"]

        # 3. Document type classification
        doc_type = "News"
        lower_title = raw_title.lower()
        for candidate, label in [
            ("circular", "Circular"),
            ("rulebook", "Rulebook"),
            ("regulation", "Regulation"),
            ("framework", "Framework"),
            ("standard", "Standard"),
            ("guideline", "Guideline"),
            ("directive", "Directive"),
            ("consultation", "Consultation"),
            ("decree", "Law"),
            ("resolution", "Law"),
        ]:
            if candidate in lower_title:
                doc_type = label
                break

        # 4. Impacted entities
        impacted: List[str] = []
        entity_map = [
            ("Banks", [r"\bbank", r"\blfi\b", r"financial institution"]),
            ("VASP", [r"\bvasp\b", r"\bcasp\b", r"virtual asset", r"crypto", r"token", r"exchange"]),
            ("Cloud Providers", [r"\bcloud\b", r"data center", r"hosting", r"csp\b"]),
            ("Payment Service Providers", [r"payment", r"\bpsp\b", r"wallet", r"fintech"]),
            ("Insurance Companies", [r"insur", r"takaful"]),
            ("AI & Data Controllers", [r"\bai\b", r"data controller", r"pdpl", r"autonomous"]),
        ]
        for ent_label, rx_list in entity_map:
            if any(re.search(rx, combined, re.IGNORECASE) for rx in rx_list):
                impacted.append(ent_label)
        if not impacted:
            impacted = ["Regulated Financial & Tech Entities"]

        # 5. Publication & enforcement date (strictly factual, no guessing)
        pub_date = published_hint if (published_hint and re.match(r"^\d{4}-\d{2}-\d{2}$", published_hint)) else "N/A"
        enf_date = "N/A"
        enf_match = re.search(
            r"(?:effective|enforcement|comply by|by)\s+(?:from\s+)?(\d{4}-\d{2}-\d{2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})",
            combined,
            re.IGNORECASE,
        )
        if enf_match:
            raw_d = enf_match.group(1)
            if re.match(r"^\d{4}-\d{2}-\d{2}$", raw_d):
                enf_date = raw_d

        clean_summary = re.sub(r"\s+", " ", raw_text).strip()
        if not clean_summary or len(clean_summary) < 25:
            clean_summary = raw_title.strip()
        if len(clean_summary) > 420:
            clean_summary = clean_summary[:417].rsplit(" ", 1)[0] + "..."

        return {
            "title": raw_title.strip() or "N/A",
            "jurisdiction": jurisdiction,
            "issuing_authority": issuing_authority,
            "document_type": doc_type,
            "publication_date": pub_date,
            "enforcement_date": enf_date,
            "domain_tags": domain_tags[:6],
            "summary": clean_summary,
            "compliance_obligations": [
                f"Review full publication from {issuing_authority if issuing_authority != 'N/A' else jurisdiction + ' regulator'} regarding {', '.join(domain_tags[:2])}."
            ],
            "impacted_entities": impacted,
            "source_url": source_url or "N/A",
            "is_new_authority_discovered": is_new_authority,
            "llm_provider_used": self.provider_name,
        }


class GeminiLLMAdapter(BaseLLMAdapter):
    """
    Google Gemini Adapter using `google-genai` SDK (or REST API fallback).
    Activated when LLM_PROVIDER=gemini and GEMINI_API_KEY is present.
    """

    provider_name = "gemini"

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key
        self.model_name = model_name
        self._fallback = DeterministicRuleExtractor()

    def extract_regulation(
        self,
        raw_title: str,
        raw_text: str,
        source_url: str,
        jurisdiction: str,
        published_hint: Optional[str],
        seed_authority_codes: List[str],
    ) -> Dict[str, Any]:
        try:
            import httpx

            prompt = (
                f"Jurisdiction Hint: {jurisdiction}\n"
                f"Known Seed Authorities: {', '.join(seed_authority_codes)}\n"
                f"Published Date Hint: {published_hint or 'N/A'}\n"
                f"Source URL: {source_url or 'N/A'}\n"
                f"Title: {raw_title}\n"
                f"Content: {raw_text[:3000]}"
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            payload = {
                "systemInstruction": {"parts": [{"text": EXTRACTION_SYSTEM_PROMPT}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.0},
            }
            with httpx.Client(timeout=20.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                text_out = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_out)
                parsed["llm_provider_used"] = f"gemini ({self.model_name})"
                parsed.setdefault("source_url", source_url or "N/A")
                return parsed
        except Exception:
            out = self._fallback.extract_regulation(
                raw_title, raw_text, source_url, jurisdiction, published_hint, seed_authority_codes
            )
            out["llm_provider_used"] = "deterministic (gemini-fallback)"
            return out


class BedrockLLMAdapter(BaseLLMAdapter):
    """
    AWS Bedrock Adapter using `boto3` Converse API (`bedrock-runtime`).
    Supports Anthropic Claude 3.5/3.7 Sonnet, Amazon Nova Pro/Lite, Meta Llama 3, Mistral, etc.
    Zero code changes required when porting from Gemini/Antigravity to AWS Bedrock!
    """

    provider_name = "bedrock"

    def __init__(self, region_name: str = "us-east-1", model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0") -> None:
        self.region_name = region_name
        self.model_id = model_id
        self._fallback = DeterministicRuleExtractor()

    def extract_regulation(
        self,
        raw_title: str,
        raw_text: str,
        source_url: str,
        jurisdiction: str,
        published_hint: Optional[str],
        seed_authority_codes: List[str],
    ) -> Dict[str, Any]:
        try:
            import boto3

            client = boto3.client("bedrock-runtime", region_name=self.region_name)
            user_message = (
                f"Jurisdiction Hint: {jurisdiction}\n"
                f"Known Seed Authorities: {', '.join(seed_authority_codes)}\n"
                f"Published Date Hint: {published_hint or 'N/A'}\n"
                f"Source URL: {source_url or 'N/A'}\n"
                f"Title: {raw_title}\n"
                f"Content: {raw_text[:3000]}"
            )
            response = client.converse(
                modelId=self.model_id,
                system=[{"text": EXTRACTION_SYSTEM_PROMPT}],
                messages=[{"role": "user", "content": [{"text": user_message}]}],
                inferenceConfig={"temperature": 0.0, "maxTokens": 1024},
            )
            text_out = response["output"]["message"]["content"][0]["text"].strip()
            text_out = re.sub(r"^```(?:json)?|```$", "", text_out, flags=re.MULTILINE).strip()
            parsed = json.loads(text_out)
            parsed["llm_provider_used"] = f"bedrock ({self.model_id})"
            parsed.setdefault("source_url", source_url or "N/A")
            return parsed
        except Exception:
            out = self._fallback.extract_regulation(
                raw_title, raw_text, source_url, jurisdiction, published_hint, seed_authority_codes
            )
            out["llm_provider_used"] = "deterministic (bedrock-fallback)"
            return out


class OpenAICompatibleAdapter(BaseLLMAdapter):
    """
    OpenAI-compatible REST adapter (works with OpenAI, Azure OpenAI, vLLM, Ollama, LiteLLM).
    """

    provider_name = "openai_compatible"

    def __init__(self, api_key: str, base_url: str, model_name: str) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self._fallback = DeterministicRuleExtractor()

    def extract_regulation(
        self,
        raw_title: str,
        raw_text: str,
        source_url: str,
        jurisdiction: str,
        published_hint: Optional[str],
        seed_authority_codes: List[str],
    ) -> Dict[str, Any]:
        try:
            import httpx

            prompt = (
                f"Jurisdiction Hint: {jurisdiction}\n"
                f"Published Date Hint: {published_hint or 'N/A'}\n"
                f"Source URL: {source_url or 'N/A'}\n"
                f"Title: {raw_title}\n"
                f"Content: {raw_text[:3000]}"
            )
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {
                "model": self.model_name,
                "temperature": 0.0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            }
            with httpx.Client(timeout=20.0) as client:
                resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                parsed["llm_provider_used"] = f"openai_compatible ({self.model_name})"
                return parsed
        except Exception:
            out = self._fallback.extract_regulation(
                raw_title, raw_text, source_url, jurisdiction, published_hint, seed_authority_codes
            )
            out["llm_provider_used"] = "deterministic (openai-fallback)"
            return out


def get_llm_adapter(override_provider: Optional[str] = None) -> BaseLLMAdapter:
    """
    Factory function returning the configured LLM adapter.
    Automatically falls back to DeterministicRuleExtractor if API keys are placeholders/missing.
    """
    provider = (override_provider or os.getenv("LLM_PROVIDER", "gemini")).strip().lower()

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        if api_key and api_key != "your_gemini_api_key_here":
            return GeminiLLMAdapter(api_key=api_key, model_name=model)
        return DeterministicRuleExtractor()

    if provider == "bedrock":
        region = os.getenv("AWS_REGION", "us-east-1").strip()
        model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0").strip()
        aws_key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
        if aws_key and aws_key != "your_aws_access_key_id":
            return BedrockLLMAdapter(region_name=region, model_id=model_id)
        return DeterministicRuleExtractor()

    if provider == "openai_compatible":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        if api_key and api_key != "your_openai_api_key":
            return OpenAICompatibleAdapter(api_key=api_key, base_url=base_url, model_name=model)
        return DeterministicRuleExtractor()

    return DeterministicRuleExtractor()

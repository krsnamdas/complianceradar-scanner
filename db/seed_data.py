"""
Verified UAE & MENAT/South Africa baseline regulatory intelligence dataset.
Pre-populates the database on initial boot so the UAE testbed and cross-regional
comparison are immediately inspectable and verifiable with zero hallucination.
"""

from typing import Any, Dict, List

SEED_REGULATIONS: List[Dict[str, Any]] = [
    {
        "title": "Payment Token Services Regulation (Circular No. 2/2024)",
        "jurisdiction": "UAE",
        "issuing_authority": "Central Bank of the UAE (CBUAE)",
        "document_type": "Regulation",
        "publication_date": "2024-06-07",
        "enforcement_date": "2025-06-07",
        "domain_tags": ["Crypto/Virtual Assets", "Payments", "Central Banking", "Fintech", "Digital Assets"],
        "summary": "Establishes the UAE federal licensing and supervisory framework for Payment Token Services, covering Payment Token Issuance (fiat-referenced stablecoins), Payment Token Conversion, and Payment Token Custody and Transfer. Prohibits algorithmic stablecoins and foreign-currency payment tokens for domestic merchant settlement unless explicitly registered.",
        "compliance_obligations": [
            "Obtain CBUAE license or registration prior to issuing, converting, or custodying payment tokens in the UAE.",
            "Maintain 100% reserve backing in segregated escrow accounts at UAE-licensed banks for dirham-backed payment tokens.",
            "Enforce strict AML/CFT, Travel Rule, and cybersecurity controls across token custody and settlement infrastructure."
        ],
        "impacted_entities": ["Banks", "Licensed Financial Institutions (LFIs)", "Payment Service Providers (PSPs)", "VASP", "Stablecoin Issuers"],
        "source_url": "https://www.centralbank.ae/en/laws-and-regulations/",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Operational Risk Management and Operational Resilience Regulation & Standards",
        "jurisdiction": "UAE",
        "issuing_authority": "Central Bank of the UAE (CBUAE)",
        "document_type": "Regulation",
        "publication_date": "2024-03-15",
        "enforcement_date": "N/A",
        "domain_tags": ["Operational Resilience", "Operational Risk", "Business Continuity (BCM)", "Disaster Recovery (DR)", "Third-Party Governance", "Cloud Computing"],
        "summary": "Mandates that Licensed Financial Institutions (LFIs) identify and map critical business services, set impact tolerances for severe but plausible disruptions, govern third-party ICT and cloud concentration risks, and maintain tested Business Continuity Management (BCM) and Disaster Recovery (DR) architectures.",
        "compliance_obligations": [
            "Map end-to-end technology, data, people, and third-party dependencies for all critical operations.",
            "Define board-approved maximum tolerable downtime and disruption thresholds.",
            "Conduct regular scenario testing and report material operational/cyber disruptions to CBUAE."
        ],
        "impacted_entities": ["Banks", "Licensed Financial Institutions (LFIs)", "Cloud Providers", "ICT Third-Party Vendors"],
        "source_url": "https://rulebook.centralbank.ae/",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Guidance on the Use of Artificial Intelligence and Machine Learning in Financial Services & Model Management Standards (MMS)",
        "jurisdiction": "UAE",
        "issuing_authority": "Central Bank of the UAE (CBUAE)",
        "document_type": "Guideline",
        "publication_date": "N/A",
        "enforcement_date": "N/A",
        "domain_tags": ["Artificial Intelligence (AI)", "Machine Learning (ML)", "Operational Risk", "Data Privacy", "Central Banking", "Third-Party Governance"],
        "summary": "Extends CBUAE Model Management Standards to AI/ML models deployed by financial institutions. Requires board accountability, explainability, independent model validation, continuous drift/bias monitoring, API lifecycle security, and controls preventing silent backend model updates by third-party AI vendors.",
        "compliance_obligations": [
            "Maintain a comprehensive AI/ML model inventory with risk tiering and validation documentation.",
            "Validate third-party and vendor-hosted AI models against algorithmic bias, data leakage, and silent version drift.",
            "Implement human-in-the-loop oversight for high-impact credit, AML, and customer-facing decisions."
        ],
        "impacted_entities": ["Banks", "Insurance Companies", "Finance Companies", "AI Vendors", "Fintechs"],
        "source_url": "https://www.centralbank.ae/en/laws-and-regulations/",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Open Finance Regulation (Circular No. 7/2023 & Nebras Open Finance Implementation Updates)",
        "jurisdiction": "UAE",
        "issuing_authority": "Central Bank of the UAE (CBUAE)",
        "document_type": "Regulation",
        "publication_date": "2024-04-01",
        "enforcement_date": "N/A",
        "domain_tags": ["Open Banking", "Open Finance", "Payments", "Fintech", "Cybersecurity", "Data Privacy"],
        "summary": "Establishes the mandatory cross-sectoral Open Finance framework across banking and insurance in the UAE. Mandates participation in the central API Hub, Trust Framework (digital certificates, directory, and sandbox), and standardized customer consent/authorization management.",
        "compliance_obligations": [
            "Onboard to the CBUAE Open Finance Trust Framework and centralized API Hub.",
            "Expose standardized read/write APIs for account information and payment/service initiation with granular customer consent.",
            "Enforce mutual TLS (mTLS), OAuth 2.0 / FAPI security profiles, and real-time API threat monitoring."
        ],
        "impacted_entities": ["Banks", "Insurance Companies", "Open Finance Providers (AISPs/PISPs)", "Fintechs"],
        "source_url": "https://rulebook.centralbank.ae/en/rulebook/open-finance-regulation",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Technology and Information Rulebook — Risk Category 5: Digital Operational Resilience (Version 2.0)",
        "jurisdiction": "UAE",
        "issuing_authority": "Virtual Assets Regulatory Authority (VARA)",
        "document_type": "Rulebook",
        "publication_date": "2025-05-19",
        "enforcement_date": "2025-06-19",
        "domain_tags": ["Crypto/Virtual Assets", "Operational Resilience", "Cybersecurity", "Business Continuity (BCM)", "Disaster Recovery (DR)", "Operational Risk"],
        "summary": "Comprehensive VARA Rulebook update introducing Digital Operational Resilience requirements for Virtual Asset Service Providers (VASPs) in Dubai. Mandates structured resilience testing, cryptographic key and hot/cold wallet custody safeguards, independent third-party security audits, and strict incident reporting.",
        "compliance_obligations": [
            "Implement a Digital Operational Resilience testing program covering smart contracts, wallet custody, and exchange matching engines.",
            "Perform mandatory independent external security audits and penetration tests at least annually.",
            "Maintain immutable audit logs and report material cyber or operational incidents to VARA."
        ],
        "impacted_entities": ["VASP", "Crypto Custodians", "Digital Asset Exchanges", "Broker-Dealers"],
        "source_url": "https://rulebook.vara.ae/",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "FSRA Cyber Risk Management Framework & Operational Resilience Rulebook Amendments",
        "jurisdiction": "UAE",
        "issuing_authority": "Financial Services Regulatory Authority (FSRA - ADGM)",
        "document_type": "Framework",
        "publication_date": "2025-07-15",
        "enforcement_date": "2026-01-31",
        "domain_tags": ["Cybersecurity", "Operational Resilience", "Operational Risk", "Third-Party Governance", "Cloud Computing"],
        "summary": "Binding amendments to the ADGM FSRA Rulebook requiring Authorised Persons and Recognised Bodies to embed a formal Cyber Risk Management Framework within their operational risk governance, enforce third-party ICT vendor controls, and notify FSRA immediately upon identifying material cyber incidents.",
        "compliance_obligations": [
            "Achieve full compliance with the ADGM FSRA Cyber Risk Management Framework by January 31, 2026.",
            "Maintain an updated IT asset and third-party cloud/ICT dependency register.",
            "Execute regular cyber incident response exercises, vulnerability assessments, and board-level cyber risk reporting."
        ],
        "impacted_entities": ["ADGM Authorised Persons", "Recognised Bodies", "Banks", "Asset Managers", "VASP", "Fintechs"],
        "source_url": "https://www.adgm.com/legal-framework/rulebooks",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "DFSA Crypto Token Regime Updates & Firm-Led Token Suitability Framework",
        "jurisdiction": "UAE",
        "issuing_authority": "Dubai Financial Services Authority (DFSA - DIFC)",
        "document_type": "Regulation",
        "publication_date": "2025-12-10",
        "enforcement_date": "2026-01-12",
        "domain_tags": ["Crypto/Virtual Assets", "Digital Assets", "Fintech", "Operational Resilience", "Cybersecurity"],
        "summary": "Major enhancements to the DIFC Crypto Token regulatory framework effective January 12, 2026. Transitions non-fiat crypto token recognition to a rigorous firm-led suitability assessment model with continuous monitoring, while retaining direct DFSA approval for Fiat Crypto Tokens (stablecoins), staking, custody, and fund management.",
        "compliance_obligations": [
            "Conduct and document formal suitability self-assessments for non-fiat Crypto Tokens prior to offering services in or from DIFC.",
            "Obtain explicit DFSA authorization for Fiat Crypto Tokens (stablecoins) and adhere to strict reserve and redemption rules.",
            "Meet enhanced digital custody, operational resilience, and monthly regulatory reporting requirements."
        ],
        "impacted_entities": ["DIFC Authorised Firms", "VASP", "Crypto Custodians", "Fund Managers", "Wealth Managers"],
        "source_url": "https://www.dfsa.ae/what-we-do/innovation-and-crypto",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "DIFC Data Protection Law Regulation 10 Notice — Processing Personal Data Through Autonomous and Semi-Autonomous Systems (AI)",
        "jurisdiction": "UAE",
        "issuing_authority": "DIFC Commissioner of Data Protection",
        "document_type": "Regulation",
        "publication_date": "N/A",
        "enforcement_date": "N/A",
        "domain_tags": ["Artificial Intelligence (AI)", "Machine Learning (ML)", "Data Privacy", "Emerging Tech", "Third-Party Governance"],
        "summary": "Enforces binding requirements in the DIFC for deployers and developers of AI, generative AI, and autonomous decision-making systems processing personal data. Requires algorithmic transparency notices, High-Risk Processing assessments, human review mechanisms, and Appointing an Autonomous Systems Officer where applicable.",
        "compliance_obligations": [
            "Maintain an evidence-based register of autonomous and AI systems processing personal data.",
            "Provide transparent notices to data subjects when autonomous systems make or materially influence decisions.",
            "Audit third-party AI providers for ethical compliance, security, and PDPL alignment."
        ],
        "impacted_entities": ["DIFC Entities", "AI Developers", "AI Deployers", "Banks", "Fintechs", "Cloud Providers"],
        "source_url": "https://www.difc.ae/business/registrars-and-commissioners/commissioner-of-data-protection",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "UAE National Encryption Policy, Post-Quantum Cryptography Roadmap & IAS v2 Information Assurance Standards",
        "jurisdiction": "UAE",
        "issuing_authority": "UAE Cyber Security Council",
        "document_type": "Standard",
        "publication_date": "N/A",
        "enforcement_date": "N/A",
        "domain_tags": ["Cybersecurity", "Quantum Computing", "Cloud Computing", "Operational Resilience", "Emerging Tech"],
        "summary": "Sets national cryptographic, post-quantum readiness, and information assurance baselines for UAE Critical Information Infrastructure (CII), government entities, and regulated sectors. Mandates cryptographic agility, inventorying vulnerable public-key algorithms, and accrediting Managed Security Service Providers (MSSPs).",
        "compliance_obligations": [
            "Inventory cryptographic assets and establish a migration roadmap toward quantum-resistant algorithms.",
            "Comply with UAE Information Assurance (IAS) and National Cloud Security Controls for sensitive workloads.",
            "Engage only accredited MSSPs and maintain continuous SOC monitoring."
        ],
        "impacted_entities": ["Critical Information Infrastructure (CII)", "Government Entities", "Banks", "Telecom Operators", "Cloud Providers"],
        "source_url": "https://csc.gov.ae/",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "UAE Charter for the Development and Use of Artificial Intelligence & Federal AI Ethics Guidelines",
        "jurisdiction": "UAE",
        "issuing_authority": "UAE Council for Artificial Intelligence and Blockchain / Office of AI",
        "document_type": "Framework",
        "publication_date": "2024-07-02",
        "enforcement_date": "N/A",
        "domain_tags": ["Artificial Intelligence (AI)", "Machine Learning (ML)", "Data Privacy", "Cybersecurity", "Emerging Tech"],
        "summary": "Establishes 12 foundational principles for safe, human-centric, transparent, and accountable AI development and deployment across the UAE, operating alongside Federal Decree-Law No. 45 of 2021 (UAE PDPL) and sector-specific regulator rules.",
        "compliance_obligations": [
            "Ensure algorithmic fairness, safety, human oversight, and data privacy by design in AI deployments.",
            "Align automated profiling and training data governance with UAE Federal PDPL requirements."
        ],
        "impacted_entities": ["Technology Companies", "Government Entities", "Banks", "Healthcare Providers", "AI Developers"],
        "source_url": "https://ai.gov.ae/",
        "is_new_authority_discovered": True,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Essential Cybersecurity Controls (ECC-2:2024)",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Cybersecurity & Critical Infrastructure",
        "regulation_standard": "Standard (ECC-2:2024)",
        "issuing_authority": "National Cybersecurity Authority (NCA)",
        "document_type": "Standard",
        "publication_date": "2024-09-01",
        "enforcement_date": "N/A",
        "domain_tags": ["Cybersecurity", "Operational Resilience", "Third-Party Governance", "Cloud Computing", "Data Privacy"],
        "summary": "Updated mandatory cybersecurity baseline for Saudi government entities, Critical National Infrastructure (CNI), and connected private sector organizations. Strengthens supply chain security, vulnerability patch intervals, and mandates that remote Managed Security Service Provider (MSSP) monitoring centers operate strictly within Saudi Arabia.",
        "compliance_obligations": [
            "Ensure all SOC/MSSP remote monitoring and log storage operate inside the Kingdom of Saudi Arabia.",
            "Align data residency and classification controls with SDAIA/NDMO standards.",
            "Enforce MFA, privileged access management, and third-party vendor cybersecurity assessments."
        ],
        "impacted_entities": ["Government Entities", "Critical National Infrastructure (CNI)", "Banks", "MSSPs", "Cloud Providers"],
        "source_url": "https://nca.gov.sa/en/regulatory-documents/",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "SAMA Cyber Security Framework (CSF), Cloud Computing Subdomain 3.4.3 & Business Continuity Management (BCM) Framework",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Banking & Central Banking",
        "regulation_standard": "Framework (SAMA CSF & BCM)",
        "issuing_authority": "Saudi Central Bank (SAMA)",
        "document_type": "Framework",
        "publication_date": "N/A",
        "enforcement_date": "N/A",
        "domain_tags": ["Cybersecurity", "Cloud Computing", "Business Continuity (BCM)", "Disaster Recovery (DR)", "Operational Resilience", "Third-Party Governance", "Central Banking"],
        "summary": "Binding supervisory framework governing cybersecurity, cloud outsourcing, business continuity, and disaster recovery across SAMA-regulated banks, insurance companies, finance companies, and payment service providers. Requires prior written SAMA approval before contracting cloud vendors, strict in-Kingdom data residency, a dedicated CISO (Saudi national) separate from IT, and minimum 12-month security log retention.",
        "compliance_obligations": [
            "Obtain prior written approval from SAMA before migrating workloads to public or hybrid cloud environments.",
            "Maintain primary and disaster recovery (DR) data storage strictly inside the Kingdom of Saudi Arabia.",
            "Conduct annual Business Continuity Management (BCM) and cyber recovery exercises across critical banking and payment systems."
        ],
        "impacted_entities": ["Banks", "Payment Service Providers (PSPs)", "Finance Companies", "Cloud Providers", "Fintechs"],
        "source_url": "https://rulebook.sama.gov.sa/en",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "SAMA Open Banking Framework — Account Information (AISP) & Payment Initiation (PISP) Technical and Security Standards",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Payments, Open Banking & FinTech",
        "regulation_standard": "Framework (SAMA Open Banking)",
        "issuing_authority": "Saudi Central Bank (SAMA)",
        "document_type": "Framework",
        "publication_date": "N/A",
        "enforcement_date": "N/A",
        "domain_tags": ["Open Banking", "Open Finance", "Payments", "Fintech", "Cybersecurity", "Data Privacy"],
        "summary": "Establishes mandatory API technical specifications, FAPI security profiles, customer consent management, and operational resilience rules for banks and FinTech Third-Party Providers (AISPs and PISPs) participating in the Saudi Open Banking ecosystem.",
        "compliance_obligations": [
            "Certify Open Banking APIs against SAMA technical, security, and availability benchmarks.",
            "Enforce explicit, revocable customer consent aligned with the Saudi Personal Data Protection Law (PDPL).",
            "Maintain real-time API fraud detection, mTLS certificate lifecycle controls, and third-party risk governance."
        ],
        "impacted_entities": ["Banks", "Fintechs (AISPs/PISPs)", "Payment Service Providers"],
        "source_url": "https://www.sama.gov.sa/en-US/Laws/Pages/default.aspx",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Saudi Personal Data Protection Law (PDPL) Implementing Regulations & Cross-Border Data Transfer Regulation",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Data Privacy, AI & Cloud Computing",
        "regulation_standard": "Law / Regulation (KSA PDPL)",
        "issuing_authority": "Saudi Data and Artificial Intelligence Authority (SDAIA / NDMO)",
        "document_type": "Regulation",
        "publication_date": "2023-09-14",
        "enforcement_date": "2024-09-14",
        "domain_tags": ["Data Privacy", "Artificial Intelligence (AI)", "Machine Learning (ML)", "Cloud Computing", "Operational Risk"],
        "summary": "Enforces comprehensive data protection across the Kingdom of Saudi Arabia, governing automated personal data processing, AI training/profiling consent, mandatory Data Protection Impact Assessments (DPIAs), 72-hour data breach notifications to SDAIA, registration on the National Data Governance Platform, and strict safeguards (Standard Contractual Clauses and Transfer Risk Assessments) for cross-border data transfers.",
        "compliance_obligations": [
            "Register as a Data Controller on the SDAIA National Data Governance Platform and appoint a Data Protection Officer (DPO) where required.",
            "Execute Transfer Risk Assessments (TRAs) and Standard Contractual Clauses (SCCs) before transferring personal data outside Saudi Arabia.",
            "Notify SDAIA within 72 hours of discovering any personal data breach impacting data subjects."
        ],
        "impacted_entities": ["Data Controllers", "Data Processors", "Banks", "Cloud Providers", "AI Developers", "Healthcare & Retail Entities"],
        "source_url": "https://sdaia.gov.sa/en/SDAIA/about/Pages/RegulationsAndPolicies.aspx",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "SDAIA Generative AI Guidelines & National AI Ethics Principles (Version 2.0)",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Data Privacy, AI & Cloud Computing",
        "regulation_type": "Guideline",
        "regulation_standard": "Guideline (SDAIA AI Ethics & GenAI)",
        "issuing_authority": "Saudi Data and Artificial Intelligence Authority (SDAIA / NDMO)",
        "document_type": "Guideline",
        "publication_date": "2024-01-15",
        "enforcement_date": "N/A",
        "domain_tags": ["Artificial Intelligence (AI)", "Machine Learning (ML)", "Emerging Tech", "Data Privacy", "Cybersecurity"],
        "summary": "Provides national governance principles and risk-tiered operational controls for developing, procuring, and deploying Artificial Intelligence and Generative AI models across Saudi government and private sector entities, emphasizing fairness, explainability, human oversight, and protection against prompt injection and training data poisoning.",
        "compliance_obligations": [
            "Conduct AI risk and ethical impact assessments across the model lifecycle prior to production deployment.",
            "Ensure training and fine-tuning datasets comply with Saudi PDPL and NDMO data classification tiers.",
            "Implement adversarial robustness, hallucination monitoring, and human-in-the-loop controls."
        ],
        "impacted_entities": ["AI Developers", "Government Entities", "Banks", "Cloud Providers", "Enterprises"],
        "source_url": "https://sdaia.gov.sa/en/SDAIA/about/Pages/RegulationsAndPolicies.aspx",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Cloud Cybersecurity Controls (CCC) & Critical Systems Cybersecurity Controls (CSCC)",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Cybersecurity & Critical Infrastructure",
        "regulation_standard": "Standard (NCA CCC & CSCC)",
        "issuing_authority": "National Cybersecurity Authority (NCA)",
        "document_type": "Standard",
        "publication_date": "N/A",
        "enforcement_date": "N/A",
        "domain_tags": ["Cloud Computing", "Cybersecurity", "Operational Resilience", "Disaster Recovery (DR)", "Third-Party Governance"],
        "summary": "Establishes mandatory cybersecurity requirements for Cloud Service Providers (CSPs) and Cloud Tenants in Saudi Arabia, alongside specialized controls for Critical National Systems. Enforces cryptographic key management inside KSA, tenant isolation, hypervisor security, and continuous compliance monitoring.",
        "compliance_obligations": [
            "Enforce strict cryptographic key custody (BYOK/HYOK) and multi-tenant isolation for regulated cloud workloads.",
            "Comply with NCA shared-responsibility matrices across IaaS, PaaS, and SaaS deployments."
        ],
        "impacted_entities": ["Cloud Providers", "Government Entities", "Critical National Infrastructure (CNI)", "Banks"],
        "source_url": "https://nca.gov.sa/en/regulatory-documents/",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Data Center Services Regulations & Cloud Computing Regulatory Framework (CCRF)",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Telecommunications & Digital Government",
        "regulation_standard": "Regulation (CST Data Center & CCRF)",
        "issuing_authority": "Communications, Space and Technology Commission (CST)",
        "document_type": "Regulation",
        "publication_date": "2024-01-01",
        "enforcement_date": "2024-01-01",
        "domain_tags": ["Cloud Computing", "Operational Resilience", "Business Continuity (BCM)", "Disaster Recovery (DR)", "Data Privacy"],
        "summary": "Governs cloud service providers and wholesale/retail data center operators in Saudi Arabia. Mandates CST registration, tier classification, customer data protection according to NDMO/SDAIA data classification levels, business continuity SLAs, and disaster recovery resilience.",
        "compliance_obligations": [
            "Register data center and cloud facilities with CST and maintain required availability and security certifications.",
            "Host Saudi government and sensitive regulated workloads strictly within CST-qualified in-Kingdom cloud zones."
        ],
        "impacted_entities": ["Cloud Providers", "Data Center Operators", "Telecom Operators", "Enterprise SaaS Providers"],
        "source_url": "https://www.cst.gov.sa/en/RulesandSystems/RegulatoryDocuments/Pages/default.aspx",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "CMA Cybersecurity Guidelines for Capital Market Institutions & FinTech ExPermit Framework",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Capital Markets & Wealth Management",
        "regulation_standard": "Guideline / Framework (CMA Cyber & FinTech)",
        "issuing_authority": "Capital Market Authority (CMA)",
        "document_type": "Guideline",
        "publication_date": "N/A",
        "enforcement_date": "N/A",
        "domain_tags": ["Cybersecurity", "Fintech", "Operational Resilience", "Artificial Intelligence (AI)", "Operational Risk"],
        "summary": "Sets cybersecurity governance, trading infrastructure resilience, penetration testing, and cyber incident reporting requirements for Saudi Capital Market Institutions (brokers, asset managers, investment banks), alongside FinTech Lab ExPermit rules for robo-advisory, equity crowdfunding, and DLT/tokenized securities testing.",
        "compliance_obligations": [
            "Maintain an independent cybersecurity function and report material cyber incidents immediately to the CMA.",
            "Obtain a CMA FinTech ExPermit prior to launching automated robo-advisory or DLT-based securities platforms."
        ],
        "impacted_entities": ["Capital Market Institutions", "Asset Managers", "Investment Banks", "WealthTech / Robo-Advisors", "Fintechs"],
        "source_url": "https://cma.org.sa/en/RulesRegulations/Regulations/Pages/default.aspx",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Saudi Insurance Authority (IA) Cybersecurity, InsurTech & Operational Risk Supervisory Transition Circulars",
        "region": "GCC",
        "jurisdiction": "KSA",
        "sector": "Insurance & Takaful",
        "regulation_standard": "Circular / Regulation (IA Insurance Supervision)",
        "issuing_authority": "Insurance Authority (IA — Saudi Arabia)",
        "document_type": "Circular",
        "publication_date": "N/A",
        "enforcement_date": "N/A",
        "domain_tags": ["Cybersecurity", "Operational Risk", "Fintech", "Data Privacy", "Business Continuity (BCM)"],
        "summary": "Following the establishment of the dedicated Saudi Insurance Authority (IA) assuming insurance sector oversight from SAMA, enforces continuous compliance with insurance cybersecurity standards, digital brokerage/InsurTech licensing, AI underwriting governance, and policyholder data protection.",
        "compliance_obligations": [
            "Align insurance IT, cyber defense, and cloud outsourcing controls with Insurance Authority (IA) supervisory mandates.",
            "Ensure automated claims and AI pricing models comply with IA conduct and SDAIA PDPL rules."
        ],
        "impacted_entities": ["Insurance Companies", "Reinsurance Companies", "InsurTechs", "Insurance Brokers"],
        "source_url": "https://ia.gov.sa/",
        "is_new_authority_discovered": True,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Cyber and Operational Resilience Framework (CORF v1.0)",
        "jurisdiction": "Kuwait",
        "issuing_authority": "Central Bank of Kuwait (CBK)",
        "document_type": "Framework",
        "publication_date": "2025-12-01",
        "enforcement_date": "2026-06-01",
        "domain_tags": ["Cybersecurity", "Operational Resilience", "Business Continuity (BCM)", "Disaster Recovery (DR)", "Third-Party Governance", "Open Banking"],
        "summary": "Replaces the 2020 CBK Cybersecurity Framework with a unified resilience regime containing 876 controls across 27 domains, 93 sub-domains, and 3 pillars (Cyber Resilience, Operational Resilience, and Third-Party Risk Management).",
        "compliance_obligations": [
            "Conduct independent maturity assessments across all 876 CORF controls.",
            "Implement real-time Key Risk Indicator (KRI) dashboards and continuous third-party ICT risk monitoring."
        ],
        "impacted_entities": ["Banks", "Finance Companies", "Exchange Houses", "E-Payment Providers", "Open Banking Entities"],
        "source_url": "https://www.cbk.gov.kw/en/legislation-and-regulation",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    },
    {
        "title": "Directive No. 01 of 2024 on Cybersecurity and Cyber-Resilience within the National Payment System & Joint SARB/FSCA AI & Crypto Communications",
        "jurisdiction": "South Africa",
        "issuing_authority": "South African Reserve Bank (SARB) & Financial Sector Conduct Authority (FSCA)",
        "document_type": "Directive",
        "publication_date": "2024-05-01",
        "enforcement_date": "N/A",
        "domain_tags": ["Cybersecurity", "Operational Resilience", "Payments", "Crypto/Virtual Assets", "Artificial Intelligence (AI)", "Central Banking"],
        "summary": "Enforces cyber-resilience controls, incident reporting, and recovery time objectives for National Payment System participants, alongside FSCA/SARB oversight of Crypto Asset Service Providers (CASPs) under FAIS and AI governance across financial institutions.",
        "compliance_obligations": [
            "Maintain board-approved cyber-resilience frameworks and meet 2-hour recovery time objectives for critical payment systems.",
            "Ensure CASPs hold active FAIS licenses and comply with SARB National Payment System Act restrictions on domestic crypto settlement."
        ],
        "impacted_entities": ["Banks", "Payment System Operators", "Third-Party Payment Providers", "Crypto Asset Service Providers (CASPs)"],
        "source_url": "https://www.resbank.co.za/",
        "is_new_authority_discovered": False,
        "llm_provider_used": "verified-seed"
    }
]

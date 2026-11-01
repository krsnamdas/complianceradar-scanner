# Implementation & Extension Tasks — ComplianceRadar-Scanner

## Completed Baseline Tasks (v2.1)
- [x] 1. Multi-jurisdiction ontology (`config/jurisdictions.yaml`) with UAE & Saudi Arabia (KSA) active by default and full MENAT + South Africa coverage.
- [x] 2. Portable AI Adapter (`llm/provider.py`) supporting Google Gemini, AWS Bedrock (`boto3` Converse API), OpenAI-compatible endpoints, and Deterministic fallback.
- [x] 3. Multi-level Scoped Scanner & Filter UI (`Region`, `Country`, `Sector`, `Regulation/Standard`).
- [x] 4. Manual Link Ingestion (`POST /api/v1/sources`) and Filterable Monitored Sources Directory (`GET /api/v1/sources`).
- [x] 5. Secure External Platform API (`GET /api/v1/external/feed` and `POST /api/v1/compliance-iq/push`) with `X-API-Key` / `Bearer` auth and `X-ComplianceRadar-Signature` (HMAC-SHA256).
- [x] 6. Downloadable Scan Reports (`CSV`, `Executive Printable HTML/PDF`, and `Strict JSON`).
- [x] 7. Weekly Corporate Email Digest (`POST /api/v1/email-digest/subscribers` and `POST /api/v1/email-digest/send-now`).

## Upcoming AWS Cloud & Phase 2 Tasks (For AWS Kiro)
- [ ] 8. Configure AWS Bedrock production model (`anthropic.claude-3-5-sonnet-20241022-v2:0` or `amazon.nova-pro-v1:0`) and Amazon SES for corporate email delivery.
- [ ] 9. Add Playwright headless browser & PDF circular text extraction (`pypdf` / Amazon Textract) for deep PDF rulebook parsing.
- [ ] 10. Add `Dockerfile` and AWS CDK / Terraform infrastructure for AWS App Runner / ECS Fargate + Amazon RDS PostgreSQL.
- [ ] 11. (Phase 2) Scaffold iOS & Android mobile app (Flutter / React Native) connected to `/api/v1/external/feed`.

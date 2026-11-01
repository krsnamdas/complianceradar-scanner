"""
ComplianceRadar-Scanner v2.1 — Enterprise FastAPI Backend, Scoped Scanner,
Monitored Sources & Manual Link Ingestion, Report Generator, Weekly Corporate Email Digest,
and Secure External Platform API (Bearer Token + X-API-Key + HMAC-SHA256 Signed Webhooks).
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from db.database import (
    delete_email_subscriber,
    delete_monitored_source,
    get_new_authorities,
    init_db,
    list_email_digest_logs,
    list_email_subscribers,
    list_monitored_sources,
    list_regulations,
    list_scan_runs,
    mark_synced_to_compliance_iq,
    upsert_email_subscriber,
    upsert_monitored_source,
)
from llm.provider import get_llm_adapter
from scraper.engine import RegulatoryScannerEngine, load_config

load_dotenv()

STATIC_DIR = Path(__file__).resolve().parent / "static"
scanner_engine = RegulatoryScannerEngine()


class SchedulerState:
    def __init__(self) -> None:
        self.enabled: bool = True
        self.interval_minutes: int = int(os.getenv("SCAN_INTERVAL_MINUTES", "360"))
        self.weekly_digest_enabled: bool = True
        self.weekly_digest_day: str = os.getenv("WEEKLY_DIGEST_DAY", "Monday 08:30 GST")
        self.active_jurisdictions: List[str] = [
            j.strip() for j in os.getenv("ACTIVE_JURISDICTIONS", "UAE,KSA").split(",") if j.strip()
        ]
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
        self.last_run_at: Optional[str] = None
        self.is_scanning: bool = False
        self.compliance_iq_webhook_url: str = os.getenv(
            "COMPLIANCE_IQ_WEBHOOK_URL", "http://localhost:8080/api/v1/compliance-iq/mock-receiver"
        )
        self.api_secret: str = os.getenv("COMPLIANCE_IQ_API_SECRET", "complianceradar-dev-secret")
        self.last_compliance_iq_sync: Optional[Dict[str, Any]] = None


scheduler_state = SchedulerState()
_bg_task: Optional[asyncio.Task] = None


def sign_payload_hmac(payload_bytes: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def verify_external_api_auth(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    api_key_query: Optional[str] = Query(default=None, alias="api_key"),
) -> bool:
    """
    Validates external platform API requests using X-API-Key header,
    Authorization: Bearer <token>, or ?api_key= query token.
    """
    expected = scheduler_state.api_secret
    token = None
    if x_api_key:
        token = x_api_key.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif api_key_query:
        token = api_key_query.strip()

    if not token or not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized external platform request. Provide a valid X-API-Key or Authorization: Bearer <token>.",
        )
    return True


async def background_scheduler_loop() -> None:
    while True:
        try:
            await asyncio.sleep(max(30, scheduler_state.interval_minutes * 60))
            if scheduler_state.enabled and not scheduler_state.is_scanning:
                scheduler_state.is_scanning = True
                try:
                    await scanner_engine.run_scan(
                        jurisdictions=scheduler_state.active_jurisdictions,
                        override_llm_provider=scheduler_state.llm_provider,
                    )
                    scheduler_state.last_run_at = datetime.now(timezone.utc).isoformat()
                finally:
                    scheduler_state.is_scanning = False
        except asyncio.CancelledError:
            break
        except Exception:
            scheduler_state.is_scanning = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bg_task
    init_db()
    scanner_engine.ensure_seed_data_loaded()
    _bg_task = asyncio.create_task(background_scheduler_loop())
    yield
    if _bg_task:
        _bg_task.cancel()


app = FastAPI(
    title="ComplianceRadar-Scanner v2.1 Enterprise Platform & External Bridge API",
    description=(
        "Multi-level Scoped Regulatory Scanner (Region, Country, Sector, Regulation/Standard), "
        "Manual Link Ingestion, Sources Directory, Report Generator, Weekly Corporate Email Digest, "
        "and Secure External Platform API (Phase 2 Mobile-Ready REST Architecture)."
    ),
    version="2.1.0",
    lifespan=lifespan,
)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# --- Request Models ---

class ScopedScanTriggerRequest(BaseModel):
    region: Optional[str] = "ALL"
    jurisdictions: List[str] = ["UAE"]
    sector: Optional[str] = "ALL"
    regulation_standard: Optional[str] = "ALL"
    llm_provider: Optional[str] = None
    custom_query: Optional[str] = None
    specific_source_ids: Optional[List[str]] = None


class ManualSourceCreateRequest(BaseModel):
    source_name: str
    source_url: str
    region: Optional[str] = None
    country: str = "UAE"
    sector: str = "Banking & Central Banking"
    regulation_standard: str = "Regulation"
    issuing_authority: str = "N/A"
    scan_immediately: bool = True


class SchedulerConfigUpdate(BaseModel):
    enabled: bool
    interval_minutes: int
    active_jurisdictions: List[str]
    llm_provider: str
    compliance_iq_webhook_url: Optional[str] = None
    weekly_digest_day: Optional[str] = None


class ComplianceIQPushRequest(BaseModel):
    region: Optional[str] = None
    jurisdiction: Optional[str] = "UAE"
    sector: Optional[str] = None
    regulation_standard: Optional[str] = None
    webhook_url: Optional[str] = None


class EmailSubscriberCreateRequest(BaseModel):
    email: str
    full_name: str = "Colleague"
    department: str = "Compliance & Risk"
    regions_filter: str = "MENAT"
    countries_filter: str = "UAE"
    sectors_filter: str = "ALL"
    frequency: str = "WEEKLY"


class SendWeeklyDigestRequest(BaseModel):
    jurisdiction_filter: Optional[str] = "UAE"
    sector_filter: Optional[str] = "ALL"
    custom_recipients: Optional[List[str]] = None


# --- UI & Status Endpoints ---

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/v1/status")
async def get_system_status() -> Dict[str, Any]:
    all_regs = list_regulations(limit=1000)
    uae_regs = [r for r in all_regs if r["jurisdiction"].upper() == "UAE"]
    ksa_regs = [r for r in all_regs if r["jurisdiction"].upper() == "KSA"]
    enforced_soon = [r for r in all_regs if r.get("enforcement_date") and r["enforcement_date"] != "N/A"]
    new_auths = get_new_authorities()
    runs = list_scan_runs(limit=10)
    sources = list_monitored_sources()
    manual_sources = [s for s in sources if s.get("is_manual")]
    subscribers = list_email_subscribers()
    digest_logs = list_email_digest_logs(limit=5)
    cfg = load_config()

    adapter = get_llm_adapter(scheduler_state.llm_provider)
    return {
        "metrics": {
            "total_regulations": len(all_regs),
            "uae_regulations": len(uae_regs),
            "ksa_regulations": len(ksa_regs),
            "tracked_enforcement_dates": len(enforced_soon),
            "new_authorities_discovered": len(new_auths),
            "total_monitored_sources": len(sources),
            "manual_sources_count": len(manual_sources),
            "email_subscribers_count": len(subscribers),
            "synced_to_compliance_iq": sum(1 for r in all_regs if r.get("synced_to_compliance_iq")),
        },
        "scheduler": {
            "enabled": scheduler_state.enabled,
            "interval_minutes": scheduler_state.interval_minutes,
            "weekly_digest_enabled": scheduler_state.weekly_digest_enabled,
            "weekly_digest_day": scheduler_state.weekly_digest_day,
            "active_jurisdictions": scheduler_state.active_jurisdictions,
            "configured_llm_provider": scheduler_state.llm_provider,
            "active_adapter_runtime": adapter.provider_name,
            "is_scanning": scheduler_state.is_scanning,
            "last_run_at": scheduler_state.last_run_at or (runs[0]["completed_at"] if runs else None),
            "compliance_iq_webhook_url": scheduler_state.compliance_iq_webhook_url,
            "last_compliance_iq_sync": scheduler_state.last_compliance_iq_sync,
        },
        "hierarchy_taxonomy": cfg.get("hierarchy_taxonomy", {}),
        "available_jurisdictions": [
            {
                "code": k,
                "name": v.get("name", k),
                "region": v.get("region", "GCC"),
                "authorities_count": len(v.get("seed_authorities", [])),
            }
            for k, v in cfg.get("jurisdictions", {}).items()
        ],
        "domain_taxonomy": cfg.get("domain_taxonomy", {}),
        "recommended_api_integrations": cfg.get("recommended_api_integrations", []),
        "recent_scan_runs": runs,
        "new_authorities_list": new_auths,
        "recent_email_digests": digest_logs,
    }


# --- 1.a & Feed Filtering Endpoints (Region / Country / Sector / Regulation-Standard) ---

@app.get("/api/v1/regulations")
async def api_list_regulations(
    region: Optional[str] = Query(default=None),
    jurisdiction: Optional[str] = Query(default=None),
    sector: Optional[str] = Query(default=None),
    regulation_standard: Optional[str] = Query(default=None),
    authority: Optional[str] = Query(default=None),
    domain_tag: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    limit: int = Query(default=250, ge=1, le=1000),
) -> Dict[str, Any]:
    items = list_regulations(
        region=region,
        jurisdiction=jurisdiction,
        sector=sector,
        regulation_standard=regulation_standard,
        authority=authority,
        domain_tag=domain_tag,
        search=search,
        limit=limit,
    )
    return {"count": len(items), "items": items}


@app.post("/api/v1/scan")
async def api_trigger_scoped_scan(req: ScopedScanTriggerRequest) -> Dict[str, Any]:
    if scheduler_state.is_scanning:
        raise HTTPException(status_code=409, detail="A scan is already running in the background.")

    scheduler_state.is_scanning = True
    try:
        result = await scanner_engine.run_scan(
            region=req.region,
            jurisdictions=req.jurisdictions,
            sector=req.sector,
            regulation_standard=req.regulation_standard,
            override_llm_provider=req.llm_provider or scheduler_state.llm_provider,
            custom_query=req.custom_query,
            specific_source_ids=req.specific_source_ids,
        )
        scheduler_state.last_run_at = result["completed_at"]
        return result
    finally:
        scheduler_state.is_scanning = False


# --- 1.b & 1.c Monitored Sources Directory & Manual Link Ingestion ---

@app.get("/api/v1/sources")
async def api_list_sources(
    region: Optional[str] = Query(default=None),
    country: Optional[str] = Query(default=None),
    sector: Optional[str] = Query(default=None),
    regulation_standard: Optional[str] = Query(default=None),
    source_type: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    items = list_monitored_sources(
        region=region,
        country=country,
        sector=sector,
        regulation_standard=regulation_standard,
        source_type=source_type,
        search=search,
    )
    return {"count": len(items), "items": items}


@app.post("/api/v1/sources")
async def api_add_manual_source(req: ManualSourceCreateRequest) -> Dict[str, Any]:
    if not req.source_url.strip().startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Source URL must start with http:// or https://")

    saved = upsert_monitored_source(
        {
            "source_name": req.source_name.strip(),
            "source_url": req.source_url.strip(),
            "source_type": "Manual Link",
            "region": req.region,
            "country": req.country.strip(),
            "sector": req.sector.strip(),
            "regulation_standard": req.regulation_standard.strip(),
            "issuing_authority": req.issuing_authority.strip() or req.source_name.strip(),
            "is_manual": True,
            "active": True,
        }
    )

    scan_summary = None
    if req.scan_immediately and not scheduler_state.is_scanning:
        scheduler_state.is_scanning = True
        try:
            scan_summary = await scanner_engine.run_scan(
                jurisdictions=[req.country.strip()],
                specific_source_ids=[saved["source_id"]],
            )
        finally:
            scheduler_state.is_scanning = False

    return {"status": "added", "source": saved, "immediate_scan": scan_summary}


@app.post("/api/v1/sources/{source_id}/scan")
async def api_scan_single_source(source_id: str) -> Dict[str, Any]:
    if scheduler_state.is_scanning:
        raise HTTPException(status_code=409, detail="Scanner is currently busy.")
    scheduler_state.is_scanning = True
    try:
        return await scanner_engine.run_scan(specific_source_ids=[source_id])
    finally:
        scheduler_state.is_scanning = False


@app.delete("/api/v1/sources/{source_id}")
async def api_delete_source(source_id: str) -> Dict[str, Any]:
    deleted = delete_monitored_source(source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Source not found.")
    return {"status": "deleted", "source_id": source_id}


# --- 2. Secure External Platform API (Compliance IQ & Phase 2 Mobile App Ready) ---

@app.get("/api/v1/external/feed")
async def external_secure_feed(
    region: Optional[str] = Query(default=None),
    jurisdiction: Optional[str] = Query(default="UAE"),
    sector: Optional[str] = Query(default=None),
    regulation_standard: Optional[str] = Query(default=None),
    _authorized: bool = Depends(verify_external_api_auth),
) -> JSONResponse:
    """
    Authenticated REST endpoint for external platforms (Compliance IQ, GRC systems,
    or Phase 2 iOS/Android mobile apps). Requires `X-API-Key` or `Authorization: Bearer <token>`.
    Includes `X-ComplianceRadar-Signature` HMAC-SHA256 header for payload integrity verification.
    """
    jur = jurisdiction if (jurisdiction and jurisdiction.upper() != "ALL") else None
    payload = scanner_engine.build_strict_schema_export(
        region=region,
        jurisdiction=jur,
        sector=sector,
        regulation_standard=regulation_standard,
    )
    raw_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    sig = sign_payload_hmac(raw_bytes, scheduler_state.api_secret)
    return JSONResponse(
        content=payload,
        headers={
            "X-ComplianceRadar-Signature": f"sha256={sig}",
            "X-ComplianceRadar-Timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.post("/api/v1/compliance-iq/push")
async def push_to_compliance_iq(req: ComplianceIQPushRequest) -> Dict[str, Any]:
    """
    Dispatches the regulatory intelligence feed to the external Compliance IQ webhook
    signed with `X-ComplianceRadar-Signature` (HMAC-SHA256) and `Authorization: Bearer`.
    """
    target_url = (req.webhook_url or scheduler_state.compliance_iq_webhook_url).strip()
    jur = req.jurisdiction if (req.jurisdiction and req.jurisdiction.upper() != "ALL") else None
    strict_payload = scanner_engine.build_strict_schema_export(
        region=req.region,
        jurisdiction=jur,
        sector=req.sector,
        regulation_standard=req.regulation_standard,
    )
    regs = list_regulations(
        region=req.region,
        jurisdiction=jur,
        sector=req.sector,
        regulation_standard=req.regulation_standard,
        limit=500,
    )
    reg_ids = [r["id"] for r in regs]

    envelope = {
        "source_engine": "ComplianceRadar-Scanner-v2.1",
        "target_system": "Compliance-IQ",
        "dispatched_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "region": req.region or "ALL",
            "jurisdiction": req.jurisdiction or "ALL",
            "sector": req.sector or "ALL",
            "regulation_standard": req.regulation_standard or "ALL",
        },
        "records_count": len(strict_payload["scanned_articles"]),
        "payload": strict_payload,
    }

    body_bytes = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    signature = sign_payload_hmac(body_bytes, scheduler_state.api_secret)
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": scheduler_state.api_secret,
        "Authorization": f"Bearer {scheduler_state.api_secret}",
        "X-ComplianceRadar-Signature": f"sha256={signature}",
    }

    delivery_status = "LOCAL_MOCK_SUCCESS"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(target_url, content=body_bytes, headers=headers)
            delivery_status = f"HTTP_{resp.status_code} (HMAC Signed)"
    except Exception as exc:
        delivery_status = f"QUEUED_FOR_COMPLIANCE_IQ ({type(exc).__name__})"

    synced_count = mark_synced_to_compliance_iq(reg_ids)
    sync_summary = {
        "synced_at": envelope["dispatched_at"],
        "target_url": target_url,
        "hmac_signature": f"sha256={signature[:16]}...",
        "delivery_status": delivery_status,
        "records_dispatched": len(strict_payload["scanned_articles"]),
        "records_marked_synced": synced_count,
    }
    scheduler_state.last_compliance_iq_sync = sync_summary
    return sync_summary


@app.post("/api/v1/compliance-iq/mock-receiver")
async def mock_compliance_iq_receiver(
    request: Request,
    x_complianceradar_signature: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    raw = await request.body()
    expected_sig = "sha256=" + sign_payload_hmac(raw, scheduler_state.api_secret)
    sig_verified = bool(
        x_complianceradar_signature and hmac.compare_digest(x_complianceradar_signature, expected_sig)
    )
    data = json.loads(raw.decode("utf-8"))
    return {
        "status": "received_by_compliance_iq",
        "signature_verified": sig_verified,
        "ingested_records": data.get("records_count", 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# --- 3. Downloadable Scan Reports (JSON, CSV, Executive Printable HTML/PDF) ---

@app.get("/api/v1/export/strict-json")
async def api_export_strict_json(
    region: Optional[str] = Query(default=None),
    jurisdiction: Optional[str] = Query(default=None),
    sector: Optional[str] = Query(default=None),
    regulation_standard: Optional[str] = Query(default=None),
) -> JSONResponse:
    payload = scanner_engine.build_strict_schema_export(
        region=region,
        jurisdiction=jurisdiction,
        sector=sector,
        regulation_standard=regulation_standard,
    )
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": 'attachment; filename="complianceradar_strict_report.json"'},
    )


@app.get("/api/v1/reports/download")
async def api_download_report(
    format: str = Query(default="csv", description="csv | html | json"),
    region: Optional[str] = Query(default=None),
    jurisdiction: Optional[str] = Query(default=None),
    sector: Optional[str] = Query(default=None),
    regulation_standard: Optional[str] = Query(default=None),
) -> Response:
    fmt = format.strip().lower()
    jur_clean = jurisdiction if (jurisdiction and jurisdiction.upper() != "ALL") else None
    reg_clean = region if (region and region.upper() != "ALL") else None
    sec_clean = sector if (sector and sector.upper() != "ALL") else None
    std_clean = regulation_standard if (regulation_standard and regulation_standard.upper() != "ALL") else None

    date_tag = datetime.now(timezone.utc).strftime("%Y%m%d")
    scope_slug = (jur_clean or reg_clean or "MENAT").lower().replace(" ", "_")

    if fmt == "csv":
        csv_data = scanner_engine.generate_csv_report(
            region=reg_clean,
            jurisdiction=jur_clean,
            sector=sec_clean,
            regulation_standard=std_clean,
        )
        return Response(
            content=csv_data.encode("utf-8-sig"),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="ComplianceRadar_Report_{scope_slug}_{date_tag}.csv"'},
        )

    if fmt == "html":
        html_doc = scanner_engine.generate_executive_html_report(
            region=reg_clean,
            jurisdiction=jur_clean,
            sector=sec_clean,
            regulation_standard=std_clean,
        )
        return HTMLResponse(content=html_doc)

    payload = scanner_engine.build_strict_schema_export(
        region=reg_clean,
        jurisdiction=jur_clean,
        sector=sec_clean,
        regulation_standard=std_clean,
    )
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="ComplianceRadar_Report_{scope_slug}_{date_tag}.json"'},
    )


# --- 4. Corporate Weekly Email Digest & Colleague Subscriptions ---

@app.get("/api/v1/email-digest/subscribers")
async def api_get_subscribers() -> Dict[str, Any]:
    subs = list_email_subscribers()
    logs = list_email_digest_logs(limit=15)
    return {"subscribers": subs, "digest_logs": logs}


@app.post("/api/v1/email-digest/subscribers")
async def api_add_subscriber(req: EmailSubscriberCreateRequest) -> Dict[str, Any]:
    if "@" not in req.email:
        raise HTTPException(status_code=400, detail="Please provide a valid corporate email address.")
    saved = upsert_email_subscriber(req.model_dump())
    return {"status": "subscribed", "subscriber": saved}


@app.delete("/api/v1/email-digest/subscribers")
async def api_remove_subscriber(email: str = Query(...)) -> Dict[str, Any]:
    delete_email_subscriber(email)
    return {"status": "removed", "email": email}


@app.post("/api/v1/email-digest/send-now")
async def api_send_weekly_digest_now(req: SendWeeklyDigestRequest) -> Dict[str, Any]:
    result = scanner_engine.send_weekly_corporate_digest(
        custom_recipients=req.custom_recipients,
        jurisdiction_filter=req.jurisdiction_filter,
        sector_filter=req.sector_filter,
    )
    return result


@app.get("/api/v1/email-digest/latest-preview", response_class=HTMLResponse)
async def api_preview_latest_digest() -> HTMLResponse:
    preview_path = Path(__file__).resolve().parent / "data" / "latest_weekly_digest.html"
    if not preview_path.exists():
        scanner_engine.send_weekly_corporate_digest(jurisdiction_filter="UAE")
    return HTMLResponse(content=preview_path.read_text(encoding="utf-8"))


@app.post("/api/v1/scheduler/config")
async def api_update_scheduler(cfg: SchedulerConfigUpdate) -> Dict[str, Any]:
    scheduler_state.enabled = cfg.enabled
    scheduler_state.interval_minutes = max(5, cfg.interval_minutes)
    scheduler_state.active_jurisdictions = cfg.active_jurisdictions or ["UAE"]
    scheduler_state.llm_provider = cfg.llm_provider
    if cfg.compliance_iq_webhook_url:
        scheduler_state.compliance_iq_webhook_url = cfg.compliance_iq_webhook_url
    if cfg.weekly_digest_day:
        scheduler_state.weekly_digest_day = cfg.weekly_digest_day
    return {"status": "updated"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)

"""
Database layer for ComplianceRadar-Scanner v2.1.
Provides SQLite persistence for:
1. Scanned regulatory articles (with region, country, sector, regulation/standard hierarchy)
2. Monitored & manually added source links directory (filterable by region, country, sector, regulation/standard)
3. Scan run telemetry & newly discovered authorities
4. Corporate weekly email digest subscribers & dispatch logs
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "complianceradar.db"

COUNTRY_TO_REGION = {
    "UAE": "GCC",
    "KSA": "GCC",
    "QATAR": "GCC",
    "BAHRAIN": "GCC",
    "KUWAIT": "GCC",
    "OMAN": "GCC",
    "EGYPT": "Levant & North Africa",
    "TURKEY": "Levant & North Africa",
    "JORDAN": "Levant & North Africa",
    "SOUTH AFRICA": "Sub-Saharan Africa (South Africa)",
}


def infer_region_from_country(country: str) -> str:
    return COUNTRY_TO_REGION.get(country.strip().upper(), "MENAT")


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def compute_article_id(title: str, jurisdiction: str, issuing_authority: str) -> str:
    raw = f"{jurisdiction.strip().upper()}::{issuing_authority.strip().upper()}::{title.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def compute_source_id(url: str) -> str:
    return "src-" + hashlib.sha256(url.strip().lower().encode("utf-8")).hexdigest()[:12]


def _ensure_column(cur: sqlite3.Cursor, table: str, column: str, col_def: str) -> None:
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row["name"] for row in cur.fetchall()}
    if column not in existing:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS regulations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            region TEXT NOT NULL DEFAULT 'GCC',
            jurisdiction TEXT NOT NULL,
            sector TEXT NOT NULL DEFAULT 'Banking & Central Banking',
            regulation_standard TEXT NOT NULL DEFAULT 'Regulation',
            issuing_authority TEXT NOT NULL,
            document_type TEXT NOT NULL DEFAULT 'Regulation',
            publication_date TEXT NOT NULL DEFAULT 'N/A',
            enforcement_date TEXT NOT NULL DEFAULT 'N/A',
            domain_tags TEXT NOT NULL DEFAULT '[]',
            summary TEXT NOT NULL,
            compliance_obligations TEXT NOT NULL DEFAULT '[]',
            impacted_entities TEXT NOT NULL DEFAULT '[]',
            source_url TEXT NOT NULL DEFAULT 'N/A',
            is_new_authority_discovered INTEGER NOT NULL DEFAULT 0,
            llm_provider_used TEXT NOT NULL DEFAULT 'deterministic',
            scraped_at TEXT NOT NULL,
            synced_to_compliance_iq INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    _ensure_column(cur, "regulations", "region", "TEXT NOT NULL DEFAULT 'GCC'")
    _ensure_column(cur, "regulations", "sector", "TEXT NOT NULL DEFAULT 'Banking & Central Banking'")
    _ensure_column(cur, "regulations", "regulation_standard", "TEXT NOT NULL DEFAULT 'Regulation'")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS monitored_sources (
            source_id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_url TEXT NOT NULL UNIQUE,
            source_type TEXT NOT NULL DEFAULT 'Seed Regulator Portal',
            region TEXT NOT NULL DEFAULT 'GCC',
            country TEXT NOT NULL DEFAULT 'UAE',
            sector TEXT NOT NULL DEFAULT 'Banking & Central Banking',
            regulation_standard TEXT NOT NULL DEFAULT 'General Regulatory Portal',
            issuing_authority TEXT NOT NULL DEFAULT 'N/A',
            is_manual INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1,
            last_scanned_at TEXT DEFAULT 'Never',
            last_status TEXT DEFAULT 'READY',
            items_extracted INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_runs (
            run_id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL,
            jurisdictions TEXT NOT NULL,
            llm_provider TEXT NOT NULL,
            items_discovered INTEGER NOT NULL DEFAULT 0,
            new_items_added INTEGER NOT NULL DEFAULT 0,
            new_authorities_count INTEGER NOT NULL DEFAULT 0,
            log_summary TEXT NOT NULL DEFAULT ''
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS discovered_authorities (
            authority_name TEXT PRIMARY KEY,
            jurisdiction TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            is_outside_seed_list INTEGER NOT NULL DEFAULT 1
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS email_subscribers (
            email TEXT PRIMARY KEY,
            full_name TEXT NOT NULL DEFAULT 'Colleague',
            department TEXT NOT NULL DEFAULT 'Compliance & Risk',
            regions_filter TEXT NOT NULL DEFAULT 'ALL',
            countries_filter TEXT NOT NULL DEFAULT 'UAE',
            sectors_filter TEXT NOT NULL DEFAULT 'ALL',
            frequency TEXT NOT NULL DEFAULT 'WEEKLY',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS email_digest_logs (
            digest_id TEXT PRIMARY KEY,
            sent_at TEXT NOT NULL,
            subject TEXT NOT NULL,
            recipients TEXT NOT NULL,
            items_count INTEGER NOT NULL,
            delivery_mode TEXT NOT NULL,
            status TEXT NOT NULL,
            html_preview TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


def upsert_monitored_source(source: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    url = str(source.get("source_url") or "").strip()
    source_id = source.get("source_id") or compute_source_id(url)
    country = str(source.get("country") or "UAE").strip()
    region = str(source.get("region") or infer_region_from_country(country)).strip()
    now_iso = datetime.now(timezone.utc).isoformat()

    cur.execute(
        """
        INSERT INTO monitored_sources (
            source_id, source_name, source_url, source_type,
            region, country, sector, regulation_standard,
            issuing_authority, is_manual, active, last_scanned_at,
            last_status, items_extracted, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_id) DO UPDATE SET
            source_name = excluded.source_name,
            region = excluded.region,
            country = excluded.country,
            sector = excluded.sector,
            regulation_standard = excluded.regulation_standard,
            issuing_authority = excluded.issuing_authority,
            active = excluded.active
        """,
        (
            source_id,
            str(source.get("source_name") or url),
            url,
            str(source.get("source_type") or ("Manual Link" if source.get("is_manual") else "Seed Regulator Portal")),
            region,
            country,
            str(source.get("sector") or "Banking & Central Banking"),
            str(source.get("regulation_standard") or "Regulation / Standard"),
            str(source.get("issuing_authority") or "N/A"),
            1 if source.get("is_manual") else 0,
            1 if source.get("active", True) else 0,
            str(source.get("last_scanned_at") or "Never"),
            str(source.get("last_status") or "READY"),
            int(source.get("items_extracted") or 0),
            now_iso,
        ),
    )
    conn.commit()
    cur.execute("SELECT * FROM monitored_sources WHERE source_id = ?", (source_id,))
    row = dict(cur.fetchone())
    conn.close()
    row["is_manual"] = bool(row.get("is_manual"))
    row["active"] = bool(row.get("active"))
    return row


def update_source_scan_telemetry(source_id: str, status: str, items_extracted: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    now_iso = datetime.now(timezone.utc).isoformat()
    cur.execute(
        """
        UPDATE monitored_sources
        SET last_scanned_at = ?, last_status = ?, items_extracted = items_extracted + ?
        WHERE source_id = ?
        """,
        (now_iso, status, items_extracted, source_id),
    )
    conn.commit()
    conn.close()


def delete_monitored_source(source_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM monitored_sources WHERE source_id = ?", (source_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def list_monitored_sources(
    region: Optional[str] = None,
    country: Optional[str] = None,
    sector: Optional[str] = None,
    regulation_standard: Optional[str] = None,
    source_type: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM monitored_sources WHERE 1=1"
    params: List[Any] = []

    if region and region.upper() not in ("ALL", "MENAT"):
        query += " AND UPPER(region) = UPPER(?)"
        params.append(region)
    elif region and region.upper() == "MENAT":
        query += " AND UPPER(region) IN ('GCC', 'LEVANT & NORTH AFRICA', 'MENAT')"

    if country and country.upper() != "ALL":
        query += " AND UPPER(country) = UPPER(?)"
        params.append(country)

    if sector and sector.upper() != "ALL":
        query += " AND UPPER(sector) LIKE UPPER(?)"
        params.append(f"%{sector}%")

    if regulation_standard and regulation_standard.upper() != "ALL":
        query += " AND UPPER(regulation_standard) LIKE UPPER(?)"
        params.append(f"%{regulation_standard}%")

    if source_type and source_type.upper() != "ALL":
        if source_type.upper() == "MANUAL":
            query += " AND is_manual = 1"
        elif source_type.upper() == "SEED":
            query += " AND is_manual = 0"

    if search and search.strip():
        q = f"%{search.strip()}%"
        query += " AND (source_name LIKE ? OR source_url LIKE ? OR issuing_authority LIKE ? OR regulation_standard LIKE ?)"
        params.extend([q, q, q, q])

    query += " ORDER BY is_manual DESC, country ASC, source_name ASC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["is_manual"] = bool(d.get("is_manual"))
        d["active"] = bool(d.get("active"))
        results.append(d)
    return results


def infer_sector_from_tags(domain_tags: List[str], issuing_authority: str) -> str:
    joined = " ".join(domain_tags).lower() + " " + issuing_authority.lower()
    if any(k in joined for k in ["crypto", "virtual asset", "vara", "casp", "blockchain"]):
        return "Virtual Assets, Crypto & Blockchain"
    if any(k in joined for k in ["open banking", "open finance", "payment", "fintech"]):
        return "Payments, Open Banking & FinTech"
    if any(k in joined for k in ["data privacy", "pdpl", "popia", "artificial intelligence", "machine learning", "cloud"]):
        return "Data Privacy, AI & Cloud Computing"
    if any(k in joined for k in ["cybersecurity", "quantum", "nca", "csc", "desc"]):
        return "Cybersecurity & Critical Infrastructure"
    if any(k in joined for k in ["dfsa", "fsra", "adgm", "sca", "cma", "spk", "capital market"]):
        return "Capital Markets & Wealth Management"
    if "tdra" in joined or "cst" in joined or "citra" in joined:
        return "Telecommunications & Digital Government"
    return "Banking & Central Banking"


def upsert_regulation(item: Dict[str, Any]) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    title = str(item.get("title") or "N/A").strip()
    jurisdiction = str(item.get("jurisdiction") or "UAE").strip()
    issuing_authority = str(item.get("issuing_authority") or "N/A").strip()
    reg_id = item.get("id") or compute_article_id(title, jurisdiction, issuing_authority)

    cur.execute("SELECT id FROM regulations WHERE id = ?", (reg_id,))
    exists = cur.fetchone() is not None

    now_iso = datetime.now(timezone.utc).isoformat()
    tags_list = item.get("domain_tags") or []
    domain_tags = json.dumps(tags_list)
    obligations = json.dumps(item.get("compliance_obligations") or [])
    impacted = json.dumps(item.get("impacted_entities") or [])
    is_new_auth = 1 if item.get("is_new_authority_discovered") else 0

    region = str(item.get("region") or infer_region_from_country(jurisdiction))
    sector = str(item.get("sector") or infer_sector_from_tags(tags_list, issuing_authority))
    doc_type = str(item.get("document_type") or "Regulation")
    reg_std = str(item.get("regulation_standard") or doc_type)

    cur.execute(
        """
        INSERT INTO regulations (
            id, title, region, jurisdiction, sector, regulation_standard,
            issuing_authority, document_type, publication_date, enforcement_date,
            domain_tags, summary, compliance_obligations, impacted_entities,
            source_url, is_new_authority_discovered, llm_provider_used, scraped_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            region = excluded.region,
            sector = excluded.sector,
            regulation_standard = excluded.regulation_standard,
            publication_date = CASE WHEN excluded.publication_date != 'N/A' THEN excluded.publication_date ELSE regulations.publication_date END,
            enforcement_date = CASE WHEN excluded.enforcement_date != 'N/A' THEN excluded.enforcement_date ELSE regulations.enforcement_date END,
            domain_tags = excluded.domain_tags,
            summary = excluded.summary,
            compliance_obligations = excluded.compliance_obligations,
            impacted_entities = excluded.impacted_entities,
            source_url = CASE WHEN excluded.source_url != 'N/A' THEN excluded.source_url ELSE regulations.source_url END,
            llm_provider_used = excluded.llm_provider_used,
            scraped_at = excluded.scraped_at
        """,
        (
            reg_id,
            title,
            region,
            jurisdiction,
            sector,
            reg_std,
            issuing_authority,
            doc_type,
            str(item.get("publication_date") or "N/A"),
            str(item.get("enforcement_date") or "N/A"),
            domain_tags,
            str(item.get("summary") or "N/A"),
            obligations,
            impacted,
            str(item.get("source_url") or "N/A"),
            is_new_auth,
            str(item.get("llm_provider_used") or "deterministic"),
            item.get("scraped_at") or now_iso,
        ),
    )

    if is_new_auth and issuing_authority and issuing_authority != "N/A":
        cur.execute(
            """
            INSERT OR IGNORE INTO discovered_authorities (
                authority_name, jurisdiction, first_seen_at, is_outside_seed_list
            ) VALUES (?, ?, ?, 1)
            """,
            (issuing_authority, jurisdiction, now_iso),
        )

    conn.commit()
    conn.close()
    return not exists


def list_regulations(
    region: Optional[str] = None,
    jurisdiction: Optional[str] = None,
    sector: Optional[str] = None,
    regulation_standard: Optional[str] = None,
    authority: Optional[str] = None,
    domain_tag: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 250,
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM regulations WHERE 1=1"
    params: List[Any] = []

    if region and region.upper() not in ("ALL", "MENAT"):
        query += " AND UPPER(region) = UPPER(?)"
        params.append(region)
    elif region and region.upper() == "MENAT":
        query += " AND UPPER(region) IN ('GCC', 'LEVANT & NORTH AFRICA', 'MENAT')"

    if jurisdiction and jurisdiction.upper() != "ALL":
        query += " AND UPPER(jurisdiction) = UPPER(?)"
        params.append(jurisdiction)

    if sector and sector.upper() != "ALL":
        query += " AND UPPER(sector) LIKE UPPER(?)"
        params.append(f"%{sector}%")

    if regulation_standard and regulation_standard.upper() != "ALL":
        query += " AND (UPPER(document_type) LIKE UPPER(?) OR UPPER(regulation_standard) LIKE UPPER(?) OR UPPER(title) LIKE UPPER(?))"
        params.extend([f"%{regulation_standard}%", f"%{regulation_standard}%", f"%{regulation_standard}%"])

    if authority and authority.upper() != "ALL":
        query += " AND UPPER(issuing_authority) LIKE UPPER(?)"
        params.append(f"%{authority}%")

    if domain_tag and domain_tag.upper() != "ALL":
        query += " AND UPPER(domain_tags) LIKE UPPER(?)"
        params.append(f"%{domain_tag}%")

    if search and search.strip():
        q = f"%{search.strip()}%"
        query += " AND (title LIKE ? OR summary LIKE ? OR issuing_authority LIKE ? OR domain_tags LIKE ? OR sector LIKE ?)"
        params.extend([q, q, q, q, q])

    query += " ORDER BY CASE WHEN publication_date = 'N/A' THEN 1 ELSE 0 END, publication_date DESC, scraped_at DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["domain_tags"] = json.loads(d.get("domain_tags") or "[]")
        d["compliance_obligations"] = json.loads(d.get("compliance_obligations") or "[]")
        d["impacted_entities"] = json.loads(d.get("impacted_entities") or "[]")
        d["is_new_authority_discovered"] = bool(d.get("is_new_authority_discovered"))
        d["synced_to_compliance_iq"] = bool(d.get("synced_to_compliance_iq"))
        results.append(d)
    return results


def get_new_authorities() -> List[str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT authority_name, jurisdiction FROM discovered_authorities ORDER BY first_seen_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [f"{r['authority_name']} ({r['jurisdiction']})" for r in rows]


def record_scan_run(
    run_id: str,
    started_at: str,
    completed_at: Optional[str],
    status: str,
    jurisdictions: List[str],
    llm_provider: str,
    items_discovered: int = 0,
    new_items_added: int = 0,
    new_authorities_count: int = 0,
    log_summary: str = "",
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO scan_runs (
            run_id, started_at, completed_at, status, jurisdictions,
            llm_provider, items_discovered, new_items_added,
            new_authorities_count, log_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(run_id) DO UPDATE SET
            completed_at = excluded.completed_at,
            status = excluded.status,
            items_discovered = excluded.items_discovered,
            new_items_added = excluded.new_items_added,
            new_authorities_count = excluded.new_authorities_count,
            log_summary = excluded.log_summary
        """,
        (
            run_id,
            started_at,
            completed_at,
            status,
            json.dumps(jurisdictions),
            llm_provider,
            items_discovered,
            new_items_added,
            new_authorities_count,
            log_summary,
        ),
    )
    conn.commit()
    conn.close()


def list_scan_runs(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scan_runs ORDER BY started_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["jurisdictions"] = json.loads(d.get("jurisdictions") or "[]")
        out.append(d)
    return out


def mark_synced_to_compliance_iq(ids: List[str]) -> int:
    if not ids:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in ids)
    cur.execute(f"UPDATE regulations SET synced_to_compliance_iq = 1 WHERE id IN ({placeholders})", ids)
    updated = cur.rowcount
    conn.commit()
    conn.close()
    return updated


# --- Corporate Weekly Email Digest Persistence ---

def upsert_email_subscriber(sub: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    email = str(sub.get("email") or "").strip().lower()
    now_iso = datetime.now(timezone.utc).isoformat()
    cur.execute(
        """
        INSERT INTO email_subscribers (
            email, full_name, department, regions_filter,
            countries_filter, sectors_filter, frequency, active, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            full_name = excluded.full_name,
            department = excluded.department,
            regions_filter = excluded.regions_filter,
            countries_filter = excluded.countries_filter,
            sectors_filter = excluded.sectors_filter,
            frequency = excluded.frequency,
            active = excluded.active
        """,
        (
            email,
            str(sub.get("full_name") or "Colleague"),
            str(sub.get("department") or "Compliance & Risk"),
            str(sub.get("regions_filter") or "ALL"),
            str(sub.get("countries_filter") or "UAE"),
            str(sub.get("sectors_filter") or "ALL"),
            str(sub.get("frequency") or "WEEKLY"),
            1 if sub.get("active", True) else 0,
            now_iso,
        ),
    )
    conn.commit()
    cur.execute("SELECT * FROM email_subscribers WHERE email = ?", (email,))
    row = dict(cur.fetchone())
    conn.close()
    row["active"] = bool(row.get("active"))
    return row


def delete_email_subscriber(email: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM email_subscribers WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def list_email_subscribers() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM email_subscribers ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["active"] = bool(d.get("active"))
        out.append(d)
    return out


def record_email_digest_log(
    digest_id: str,
    subject: str,
    recipients: List[str],
    items_count: int,
    delivery_mode: str,
    status: str,
    html_preview: str,
) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    sent_at = datetime.now(timezone.utc).isoformat()
    cur.execute(
        """
        INSERT INTO email_digest_logs (
            digest_id, sent_at, subject, recipients,
            items_count, delivery_mode, status, html_preview
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            digest_id,
            sent_at,
            subject,
            json.dumps(recipients),
            items_count,
            delivery_mode,
            status,
            html_preview,
        ),
    )
    conn.commit()
    conn.close()
    return {
        "digest_id": digest_id,
        "sent_at": sent_at,
        "subject": subject,
        "recipients": recipients,
        "items_count": items_count,
        "delivery_mode": delivery_mode,
        "status": status,
    }


def list_email_digest_logs(limit: int = 15) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM email_digest_logs ORDER BY sent_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["recipients"] = json.loads(d.get("recipients") or "[]")
        out.append(d)
    return out

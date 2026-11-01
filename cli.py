"""
CLI Runner for ComplianceRadar-Scanner.
Usage:
  python cli.py --jurisdictions UAE --output data/uae_scan_output.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from db.database import init_db
from scraper.engine import RegulatoryScannerEngine


async def main() -> None:
    parser = argparse.ArgumentParser(description="ComplianceRadar-Scanner CLI")
    parser.add_argument(
        "--jurisdictions",
        nargs="+",
        default=["UAE"],
        help="Jurisdictions to scan (e.g. UAE KSA Qatar Bahrain Kuwait Oman Egypt Turkey Jordan 'South Africa')",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="Override LLM provider: gemini | bedrock | openai_compatible | deterministic",
    )
    parser.add_argument(
        "--query",
        default=None,
        help="Optional custom boolean search topic (e.g. 'Quantum Computing OR CBDC')",
    )
    parser.add_argument(
        "--output",
        default="data/latest_strict_output.json",
        help="Path to write strict JSON output",
    )
    args = parser.parse_args()

    init_db()
    engine = RegulatoryScannerEngine()
    seeded = engine.ensure_seed_data_loaded()
    print(f"[ComplianceRadar] Database initialized ({seeded} baseline verified records added).")

    scan_result = await engine.run_scan(
        jurisdictions=args.jurisdictions,
        override_llm_provider=args.provider,
        custom_query=args.query,
    )
    print(
        f"[ComplianceRadar] Scan Run {scan_result['run_id']} Completed | "
        f"Discovered: {scan_result['items_discovered']} | "
        f"New Added: {scan_result['new_items_added']} | "
        f"Adapter: {scan_result['llm_provider_used']}"
    )

    jur_filter = args.jurisdictions[0] if len(args.jurisdictions) == 1 else None
    strict_payload = engine.build_strict_schema_export(jurisdiction=jur_filter)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(strict_payload, f, indent=2, ensure_ascii=False)
    print(f"[ComplianceRadar] Strict JSON output written to {out_path.resolve()} ({len(strict_payload['scanned_articles'])} articles).")


if __name__ == "__main__":
    asyncio.run(main())

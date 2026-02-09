#!/usr/bin/env python3
"""
CLI command to view audit logs.
Usage: python view_logs.py [--limit N] [--log-id ID]
"""
import argparse
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from audit.logger import AuditLogger


def format_log_summary(log: dict) -> str:
    """Format a log entry as a summary string."""
    timestamp = log.get("timestamp", "Unknown")
    log_id = log.get("log_id", "Unknown")
    question = log["query"].get("question", "")[:60]
    fields_count = len(log["response"].get("fields", []))
    warnings_count = len(log["response"].get("validation_warnings", []))
    exec_time = log.get("metadata", {}).get("execution_time_seconds", 0)
    
    return (
        f"[{timestamp}] ID: {log_id}\n"
        f"  Question: {question}{'...' if len(question) == 60 else ''}\n"
        f"  Fields: {fields_count} | Warnings: {warnings_count} | Time: {exec_time:.2f}s"
    )


def view_logs(limit: int = 10, log_id: str = None):
    """View audit logs."""
    logger = AuditLogger()
    
    print("=" * 70)
    print("COREP Assistant - Audit Logs")
    print("=" * 70)
    
    if log_id:
        # View specific log
        log = logger.get_log_by_id(log_id)
        if log:
            print(f"\n📄 Audit Log: {log_id}\n")
            print(json.dumps(log, indent=2))
        else:
            print(f"\n❌ Log not found: {log_id}")
    else:
        # View recent logs
        logs = logger.get_all_logs(limit=limit)
        
        if not logs:
            print("\n📭 No audit logs found")
            return
        
        print(f"\n📊 Showing {len(logs)} most recent logs:\n")
        
        for i, log in enumerate(logs, 1):
            print(f"{i}. {format_log_summary(log)}\n")
        
        print(f"💡 Tip: Use --log-id <ID> to view full details of a specific log")


def main():
    parser = argparse.ArgumentParser(
        description="View COREP Assistant audit logs"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of recent logs to show (default: 10)"
    )
    parser.add_argument(
        "--log-id",
        type=str,
        help="View specific log by ID"
    )
    
    args = parser.parse_args()
    view_logs(limit=args.limit, log_id=args.log_id)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CLI Interface for COREP Assistant
Usage: python query.py --question "..." --scenario "..." [--template C_01_00]
"""
import argparse
import json
import httpx
import sys


def query_corep_assistant(question: str, scenario: str, template: str = "C_01_00"):
    """Send query to COREP Assistant backend."""
    
    base_url = "http://localhost:8000"
    
    # Check backend health
    try:
        health_response = httpx.get(f"{base_url}/health", timeout=5.0)
        if health_response.status_code != 200:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            sys.exit(1)
        print(f"✅ Backend healthy: {health_response.json()}")
    except httpx.RequestError as e:
        print(f"❌ Cannot connect to backend at {base_url}")
        print(f"   Error: {e}")
        print(f"   Make sure the backend is running: cd backend && python main.py")
        sys.exit(1)
    
    # TODO: In future features, this will call /api/analyze
    print(f"\n📋 Query Details:")
    print(f"   Template: {template}")
    print(f"   Question: {question}")
    print(f"   Scenario: {scenario}")
    print(f"\n⚠️  Full analysis functionality will be implemented in Feature 3")
    
    return {
        "template": template,
        "question": question,
        "scenario": scenario,
        "status": "pending_implementation"
    }


def main():
    parser = argparse.ArgumentParser(
        description="COREP Assistant - PRA Regulatory Reporting CLI"
    )
    parser.add_argument(
        "--question",
        type=str,
        required=True,
        help="Natural-language question about COREP reporting"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        required=True,
        help="Description of the bank's reporting scenario"
    )
    parser.add_argument(
        "--template",
        type=str,
        default="C_01_00",
        help="COREP template code (default: C_01_00 - Own Funds)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("PRA COREP Reporting Assistant - CLI")
    print("=" * 60)
    
    result = query_corep_assistant(
        question=args.question,
        scenario=args.scenario,
        template=args.template
    )
    
    print(f"\n📄 Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

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
    
    # Call /api/analyze endpoint
    print(f"\n📋 Query Details:")
    print(f"   Template: {template}")
    print(f"   Question: {question}")
    print(f"   Scenario: {scenario}")
    print(f"\n🔍 Analyzing scenario...")
    
    try:
        response = httpx.post(
            f"{base_url}/api/analyze",
            json={
                "question": question,
                "scenario": scenario,
                "template": template,
                "top_k": 5
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"\n❌ Error from backend: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    except httpx.RequestError as e:
        print(f"\n❌ Failed to call analyze endpoint: {e}")
        return None


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
    
    if result:
        print(f"\n✅ Analysis Complete!\n")
        print("📄 Result:")
        print(json.dumps(result, indent=2))
        print(f"\n📊 Summary:")
        print(f"   Fields populated: {len(result.get('fields', []))}")
        print(f"   Validation warnings: {len(result.get('validation_warnings', []))}")
        return 0
    else:
        print(f"\n❌ Analysis failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

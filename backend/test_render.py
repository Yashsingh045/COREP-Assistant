#!/usr/bin/env python3
"""
Test script for the render endpoint.
Creates a sample COREP output and renders it as HTML.
"""
import json
import httpx

# Sample COREP output for testing
sample_output = {
    "template": "C_01_00",
    "fields": [
        {
            "row": "010",
            "column": "010",
            "metric_name": "Common Equity Tier 1 (CET1) capital",
            "value": 500000000.0,
            "currency": "GBP",
            "status": "populated",
            "justification": "Bank has £500m CET1 capital as stated in the scenario, comprising ordinary shares and retained earnings as permitted under CRR Article 26.",
            "source_paragraphs": ["CRR Article 26", "COREP C0100_010"]
        },
        {
            "row": "020",
            "column": "010",
            "metric_name": "Additional Tier 1 (AT1) capital",
            "value": 100000000.0,
            "currency": "GBP",
            "status": "populated",
            "justification": "Bank has £100m AT1 instruments as stated in the scenario, meeting the criteria specified in CRR Article 52.",
            "source_paragraphs": ["CRR Article 51", "COREP C0100_020"]
        },
        {
            "row": "030",
            "column": "010",
            "metric_name": "Tier 1 capital (T1 = CET1 + AT1)",
            "value": 600000000.0,
            "currency": "GBP",
            "status": "populated",
            "justification": "Total Tier 1 capital calculated as CET1 (£500m) + AT1 (£100m) = £600m per CRR Article 25.",
            "source_paragraphs": ["CRR Article 4", "COREP C0100_030"]
        },
        {
            "row": "040",
            "column": "010",
            "metric_name": "Tier 2 (T2) capital",
            "value": None,
            "currency": "GBP",
            "status": "missing",
            "justification": "No Tier 2 capital information provided in the scenario. This should include subordinated loans and instruments meeting CRR Article 63 criteria.",
            "source_paragraphs": ["CRR Article 62", "COREP C0100_040"]
        },
        {
            "row": "050",
            "column": "010",
            "metric_name": "Total own funds (T1 + T2)",
            "value": None,
            "currency": "GBP",
            "status": "inconsistent",
            "justification": "Cannot calculate total own funds without Tier 2 capital information. Currently only Tier 1 (£600m) is known.",
            "source_paragraphs": ["COREP C0100_050"]
        }
    ],
    "validation_warnings": [
        "Tier 2 capital information missing - unable to calculate total own funds",
        "Total own funds calculation incomplete - requires T2 data"
    ]
}


def test_render_endpoint():
    """Test the /api/render endpoint."""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Testing COREP Render Endpoint")
    print("=" * 60)
    
    try:
        # Test health check first
        health_response = httpx.get(f"{base_url}/health", timeout=5.0)
        if health_response.status_code != 200:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return
        print(f"✅ Backend healthy\n")
        
        # Call render endpoint
        print("📤 Sending sample COREP output to render endpoint...")
        response = httpx.post(
            f"{base_url}/api/render",
            json=sample_output,
            timeout=10.0
        )
        
        if response.status_code == 200:
            html_output = response.text
            
            # Save to file
            output_file = "/tmp/corep_c01_sample.html"
            with open(output_file, 'w') as f:
                f.write(html_output)
            
            print(f"✅ HTML rendered successfully")
            print(f"📄 Saved to: {output_file}")
            print(f"📊 HTML size: {len(html_output)} bytes")
            print(f"\n💡 Open in browser: file://{output_file}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except httpx.RequestError as e:
        print(f"❌ Failed to connect to backend: {e}")
        print("   Make sure the backend is running: cd backend && python main.py")


if __name__ == "__main__":
    test_render_endpoint()

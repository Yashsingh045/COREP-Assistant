#!/bin/bash
# Test scenarios for COREP Assistant
# Run with: bash test_scenarios.sh

echo "======================================================================"
echo "COREP Assistant - End-to-End Test Scenarios"
echo "======================================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$(dirname "$0")/.."

# Activate virtual environment
source backend/venv/bin/activate

echo ""
echo "${BLUE}Test Scenario 1: Basic CET1 and AT1 Capital${NC}"
echo "----------------------------------------------------------------------"
python cli/query.py \
  --question "What are the capital components for C 01.00?" \
  --scenario "Bank has £500 million in Common Equity Tier 1 capital comprising ordinary shares and retained earnings. Additionally, the bank has £100 million in Additional Tier 1 instruments."

echo ""
echo ""
echo "${BLUE}Test Scenario 2: Complete Own Funds with T2${NC}"
echo "----------------------------------------------------------------------"
python cli/query.py \
  --question "Populate the complete own funds template" \
  --scenario "The bank reports CET1 capital of £800m, AT1 capital of £150m, and Tier 2 capital of £250m for the reporting period ending December 2023."

echo ""
echo ""
echo "${BLUE}Test Scenario 3: Missing Tier 2 Data${NC}"
echo "----------------------------------------------------------------------"
python cli/query.py \
  --question "What can be populated in C 01.00?" \
  --scenario "Bank has CET1 of £600m from share capital and reserves, plus AT1 instruments worth £80m. No Tier 2 information is available."

echo ""
echo ""
echo "${BLUE}Test Scenario 4: Edge Case - Zero AT1${NC}"
echo "----------------------------------------------------------------------"
python cli/query.py \
  --question "Fill C 01.00 for a bank with no AT1" \
  --scenario "Small bank with £300m CET1 capital but no Additional Tier 1 instruments. Tier 2 capital consists of £50m in subordinated debt."

echo ""
echo ""
echo "${GREEN}======================================================================"
echo "All test scenarios completed!"
echo "======================================================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Check logs/ directory for audit trails"
echo "  2. View logs with: python cli/view_logs.py"
echo "  3. Test HTML rendering: cd backend && python test_render.py"

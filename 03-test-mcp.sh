#!/usr/bin/env bash
# ==============================================================================
# Stage 3: End-to-End Test of MCP Server (Streamable HTTP) via Apigee X
# ==============================================================================
set -euo pipefail
source ./env.sh

MCP_URL="https://${APIGEE_HOST}/v1/mcp/simplebank"

echo "🧪 [1/4] Listing all 9 MCP Banking Tools (tools/list) at ${MCP_URL}..."
curl -ks -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
echo -e "\n"

echo "🧪 [2/4] Calling 'get_customer_profile' for CUST-101 (Alice Johnson)..."
curl -ks -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_customer_profile",
      "arguments": {
        "customer_id": "CUST-101"
      }
    }
  }'
echo -e "\n"

echo "🧪 [3/4] Calling 'list_cards' for CUST-101..."
curl -ks -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "list_cards",
      "arguments": {
        "customer_id": "CUST-101"
      }
    }
  }'
echo -e "\n"

echo "🧪 [4/4] Calling 'simulate_loan' (25,000 USD AUTO loan for 36 months)..."
curl -ks -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "simulate_loan",
      "arguments": {
        "loan_type": "AUTO",
        "principal_amount": 25000,
        "term_months": 36
      }
    }
  }'
echo -e "\n"
echo "✅ End-to-end Streamable HTTP MCP tests completed successfully."

#!/usr/bin/env bash
# ==============================================================================
# Stage 3: End-to-End Test of MCP Server (Streamable HTTP) via Apigee X
# ==============================================================================
set -euo pipefail
source ./env.sh

MCP_URL="https://${APIGEE_HOST}/v1/mcp/simplebank"

echo "🧪 [1/2] Listing MCP Tools (tools/list) at ${MCP_URL}..."
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

echo "🧪 [2/2] Calling 'get_account_balance' (tools/call) for account ACC-001..."
curl -ks -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_account_balance",
      "arguments": {
        "account_id": "ACC-001"
      }
    }
  }'
echo -e "\n"
echo "✅ End-to-end Streamable HTTP MCP tests completed successfully."

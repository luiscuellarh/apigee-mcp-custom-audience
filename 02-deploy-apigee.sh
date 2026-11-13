#!/usr/bin/env bash
# ==============================================================================
# Stage 2: Fetch Deployed Cloud Run URL and Deploy Apigee Proxy + MCP Product
#          using Apigee Feature Templater (aft)
# ==============================================================================
set -euo pipefail
source ./env.sh

echo "🔍 [1/3] Fetching URL for Cloud Run service '${SERVICE_NAME}'..."
CLOUD_RUN_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format="value(status.url)")

if [[ -z "${CLOUD_RUN_URL}" ]]; then
  echo "❌ Error: Could not find URL for ${SERVICE_NAME}. Run ./01-deploy-cloudrun.sh first."
  exit 1
fi

echo "   -> Apigee Org:      ${APIGEE_ORG}"
echo "   -> Apigee Env:      ${APIGEE_ENV}"
echo "   -> Apigee Hostname: ${APIGEE_HOST}"
echo "   -> Cloud Run URL:   ${CLOUD_RUN_URL}"
echo "   -> Custom Audience: ${CUSTOM_AUDIENCE}"

echo "📝 [2/3] Generating mcp-simplebank.yaml with Target URL and Custom Audience..."
sed -e "s|__CLOUD_RUN_URL__|${CLOUD_RUN_URL}|g" \
    -e "s|__CUSTOM_AUDIENCE__|${CUSTOM_AUDIENCE}|g" \
    mcp-simplebank.template.yaml > mcp-simplebank.yaml

echo "📦 [3/3] Deploying Proxy and MCP API Product to Apigee X using 'aft'..."
if ! command -v aft >/dev/null 2>&1 && [[ ! -x ./aft ]]; then
  echo "   -> Downloading Apigee Feature Templater ('aft') binary..."
  OS_ARCH="linux-x64"
  if [[ "$(uname -s)" == "Darwin" ]]; then
    OS_ARCH="darwin-$(uname -m | sed 's/x86_64/x64/')"
  fi
  curl -sL "https://github.com/apigee/apigee-templater/releases/latest/download/aft-${OS_ARCH}" -o ./aft
  chmod +x ./aft
fi

AFT_BIN=$(command -v aft 2>/dev/null || echo "./aft")
TOKEN=$(gcloud auth print-access-token)

"${AFT_BIN}" -i mcp-simplebank.yaml -o "${APIGEE_ORG}:${PROXY_NAME}:${APIGEE_ENV}:${SA_EMAIL}" -t "${TOKEN}" --no-anim
"${AFT_BIN}" -i mcp-simplebank-product.yaml --organization "${APIGEE_ORG}" -t "${TOKEN}" --no-anim

echo ""
echo "✅ Stage 2 completed successfully."
echo "   -> Deployed Proxy:   ${PROXY_NAME} (${APIGEE_ENV})"
echo "   -> Deployed Product: mcp-simplebank-product"
echo "   -> Public Endpoint:  https://${APIGEE_HOST}/v1/mcp/simplebank"
echo "👉 Next step: ./03-test-mcp.sh"

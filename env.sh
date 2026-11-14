#!/usr/bin/env bash
# ==============================================================================
# Central Configuration (Works on Standard GCP & Argolis)
# Auto-detects active GCP project, Apigee environment, and Apigee hostname
# ==============================================================================

# 1. Project & Region
export PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}"
export REGION="${REGION:-europe-west2}"

# 2. Cloud Run & Custom Audience Settings
export SERVICE_NAME="${SERVICE_NAME:-simplebank-mcp}"
export CUSTOM_AUDIENCE="${CUSTOM_AUDIENCE:-simplebank}"
# Note: Apigee X runs in a Google-managed Tenant Project. Using "all" with
# --no-allow-unauthenticated allows Apigee X to reach the *.a.run.app URL
# directly without requiring Southbound PSC or Private DNS zones, while keeping
# the Cloud Run service 100% private and protected by IAM + Custom Audience.
export INGRESS_MODE="${INGRESS_MODE:-all}"

# 3. Apigee X Settings (Auto-detects Org, Environment, and EnvGroup Hostname)
export APIGEE_ORG="${APIGEE_ORG:-${PROJECT_ID}}"
export PROXY_NAME="${PROXY_NAME:-mcp-simplebank-v1}"

if [[ -z "${APIGEE_ENV:-}" ]]; then
  TOKEN=$(gcloud auth print-access-token 2>/dev/null || true)
  if [[ -n "${TOKEN}" ]]; then
    export APIGEE_ENV=$(curl -s -H "Authorization: Bearer ${TOKEN}" \
      "https://apigee.googleapis.com/v1/organizations/${APIGEE_ORG}/environments" \
      | tr -d '[]" \n' | cut -d',' -f1)
  fi
  export APIGEE_ENV="${APIGEE_ENV:-dev}"
fi

if [[ -z "${APIGEE_HOST:-}" ]]; then
  TOKEN=$(gcloud auth print-access-token 2>/dev/null || true)
  if [[ -n "${TOKEN}" ]]; then
    export APIGEE_HOST=$(curl -s -H "Authorization: Bearer ${TOKEN}" \
      "https://apigee.googleapis.com/v1/organizations/${APIGEE_ORG}/envgroups" \
      | tr -d '\n ' | grep -o '"hostnames":\["[^"]*"' | head -n 1 | cut -d'"' -f4 || true)
  fi
  export APIGEE_HOST="${APIGEE_HOST:-your-apigee-domain.nip.io}"
fi

# 4. Dedicated Service Account used by Apigee X to invoke Cloud Run
export SA_NAME="${SA_NAME:-apigee-mcp-invoker}"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

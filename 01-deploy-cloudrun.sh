#!/usr/bin/env bash
# ==============================================================================
# Stage 1: Enable APIs, Configure IAM (Standard GCP & Argolis), and Deploy
#          Private Cloud Run MCP Server with a Custom Audience ("simplebank")
# ==============================================================================
set -euo pipefail
source ./env.sh

echo "🔧 [0/4] Target Project: ${PROJECT_ID} (Region: ${REGION})"
gcloud config set project "${PROJECT_ID}"

echo "🛠️ [1/4] Enabling required Google Cloud APIs (Zero-State Cloud Run Setup)..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  apigee.googleapis.com \
  --quiet

# Ensure active user and default Compute Engine SA have required roles
# (Especially important in fresh Argolis projects where default SA roles are restricted)
ACTIVE_USER=$(gcloud config get-value account 2>/dev/null)
for ROLE in roles/run.admin roles/cloudbuild.builds.editor roles/apigee.admin roles/iam.serviceAccountAdmin roles/iam.serviceAccountUser roles/storage.admin; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="user:${ACTIVE_USER}" \
    --role="${ROLE}" \
    --condition=None \
    --quiet >/dev/null 2>&1 || true
done

PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
for ROLE in roles/storage.admin roles/artifactregistry.writer roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${COMPUTE_SA}" \
    --role="${ROLE}" \
    --condition=None \
    --quiet >/dev/null 2>&1 || true
done

echo "🚀 [2/4] Deploying ${SERVICE_NAME} to Cloud Run (--no-allow-unauthenticated, ingress=${INGRESS_MODE})..."
gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region="${REGION}" \
  --no-allow-unauthenticated \
  --ingress="${INGRESS_MODE}" \
  --quiet

echo "🔒 [3/4] Registering Custom Audience '${CUSTOM_AUDIENCE}' on Cloud Run..."
gcloud run services update "${SERVICE_NAME}" \
  --region="${REGION}" \
  --add-custom-audiences="${CUSTOM_AUDIENCE}" \
  --quiet

echo "🔑 [4/4] Creating Apigee Invoker Service Account (${SA_EMAIL}) & Binding IAM Roles..."
if ! gcloud iam service-accounts describe "${SA_EMAIL}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="Apigee Cloud Run MCP Invoker"
fi

# 1. Allow the deploying user to attach this SA to an Apigee proxy
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="user:${ACTIVE_USER}" \
  --role="roles/iam.serviceAccountUser" \
  --quiet >/dev/null 2>&1 || true

# 2. Allow the Apigee Service Agent to mint Google ID Tokens on behalf of this SA
APIGEE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-apigee.iam.gserviceaccount.com"
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="serviceAccount:${APIGEE_AGENT}" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --quiet >/dev/null 2>&1

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --quiet >/dev/null 2>&1

# 3. Grant Cloud Run Invoker permission on the MCP service to the Apigee SA
gcloud run services add-iam-policy-binding "${SERVICE_NAME}" \
  --region="${REGION}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" \
  --quiet >/dev/null

CLOUD_RUN_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" \
  --format="value(status.url)")

echo ""
echo "✅ Stage 1 completed successfully."
echo "   -> Cloud Run URL:   ${CLOUD_RUN_URL}"
echo "   -> Custom Audience: ${CUSTOM_AUDIENCE}"
echo "   -> Service Account: ${SA_EMAIL}"
echo "👉 Next step: ./02-deploy-apigee.sh"

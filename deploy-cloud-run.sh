#!/bin/bash
# Cloud Run Deployment Script para retarget-mcp
# Uso: ./deploy-cloud-run.sh [project-id]

set -e

# Variables
PROJECT_ID="${1:-retarget-mcp}"
SERVICE_NAME="retarget-mcp"
REGION="us-central1"
REPO_NAME="retarget-mcp"
REGISTRY_REGION="us-central1"

echo "🚀 Desplegando retarget-mcp a Cloud Run..."
echo "Proyecto: $PROJECT_ID"
echo "Servicio: $SERVICE_NAME"
echo "Región: $REGION"
echo ""

# 1. Configurar proyecto actual
echo "1️⃣ Configurando proyecto GCP..."
gcloud config set project $PROJECT_ID

# 2. Habilitar APIs necesarias
echo "2️⃣ Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# 3. Crear Artifact Registry si no existe
echo "3️⃣ Verificando Artifact Registry..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGISTRY_REGION >/dev/null 2>&1; then
  echo "   Creando repositorio..."
  gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGISTRY_REGION \
    --project=$PROJECT_ID
else
  echo "   Repositorio ya existe ✓"
fi

# 4. Dar permisos a Cloud Build
echo "4️⃣ Configurando permisos para Cloud Build..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Dar acceso a Artifact Registry
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$CLOUD_BUILD_SA \
  --role=roles/artifactregistry.writer \
  --quiet 2>/dev/null || echo "   Permiso ya existe"

# Dar acceso a Cloud Run
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$CLOUD_BUILD_SA \
  --role=roles/run.developer \
  --quiet 2>/dev/null || echo "   Permiso ya existe"

# 5. Crear Cloud Build trigger (opcional)
echo "5️⃣ Cloud Build configurado (trigger manual o en Cloud Console)"
echo ""

# 6. Desplegar manualmente usando gcloud
echo "6️⃣ Desplegando servicio..."
gcloud run deploy $SERVICE_NAME \
  --source=. \
  --region=$REGION \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --max-instances=100 \
  --set-env-vars="RAILS_ENV=production" \
  --quiet

echo ""
echo "✅ Despliegue completado!"
echo ""

# 7. Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --format='value(status.url)')

echo "📍 URL del servicio:"
echo "   $SERVICE_URL"
echo ""

# 8. Test de health check
echo "8️⃣ Testeando health check..."
HEALTH_CHECK=$(curl -s "$SERVICE_URL/health" | grep -o '"status":"[^"]*"' || echo '"status":"error"')
echo "   Respuesta: $HEALTH_CHECK"
echo ""

echo "🎉 retarget-mcp está listo en Cloud Run!"
echo ""
echo "Próximos pasos:"
echo "1. Configurar Service Account en Secret Manager"
echo "   gcloud secrets create retarget-mcp-credentials \\"
echo "     --data-file=retarget-mcp-2d37bb49c600.json"
echo ""
echo "2. Montar secreto en Cloud Run"
echo "   gcloud run services update $SERVICE_NAME \\"
echo "     --update-env-vars GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/cloud.google.com/service_account/key.json \\"
echo "     --set-env-vars RAILS_ENV=production"
echo ""
echo "3. Compartir URL del MCP con usuarios:"
echo "   $SERVICE_URL"

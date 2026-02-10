#!/usr/bin/env bash
# Task: T012 — Create K8s secrets for Dapr components
# Creates dapr-db-secret with Neon DB connectionString in todo-dev namespace
#
# Usage:
#   ./create-secrets.sh <connection-string>
#   ./create-secrets.sh "postgresql://user:pass@host/db?sslmode=require"
#
# IMPORTANT: Never commit actual connection strings to version control.
# This script is the ONLY way to inject DB credentials into the cluster.

set -euo pipefail

NAMESPACE="todo-dev"
SECRET_NAME="dapr-db-secret"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <neon-db-connection-string>"
    echo ""
    echo "Example:"
    echo "  $0 \"postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require\""
    exit 1
fi

CONNECTION_STRING="$1"

# Ensure namespace exists
kubectl get namespace "$NAMESPACE" > /dev/null 2>&1 || \
    kubectl create namespace "$NAMESPACE"

# Delete existing secret if present (idempotent)
kubectl delete secret "$SECRET_NAME" \
    --namespace "$NAMESPACE" \
    --ignore-not-found

# Create the secret
kubectl create secret generic "$SECRET_NAME" \
    --namespace "$NAMESPACE" \
    --from-literal=connectionString="$CONNECTION_STRING"

echo "Secret '$SECRET_NAME' created in namespace '$NAMESPACE'"
echo "Verify: kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data}'"

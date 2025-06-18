#!/bin/bash

# Sets production environment variables for Fly.io and Vercel.
# Assumes the `fly` and `vercel` CLIs are already authenticated.

set -euo pipefail

FLY_APP="recallhero-api"
VIN_DECODER_URL="https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{vin}?format=json"
NHTSA_RECALL_URL="https://api.nhtsa.gov/recalls/recallcampaigns?vin={vin}"

# Fly.io secrets
fly secrets set \
    VIN_DECODER_URL="$VIN_DECODER_URL" \
    NHTSA_RECALL_URL="$NHTSA_RECALL_URL" \
    -a "$FLY_APP"

echo "✅ Fly.io secrets set for $FLY_APP"

# Vercel environment variables (production)
# `vercel env add` expects the value on stdin
printf '%s\n' "$VIN_DECODER_URL" | vercel env add VIN_DECODER_URL production
printf '%s\n' "$NHTSA_RECALL_URL" | vercel env add NHTSA_RECALL_URL production

echo "✅ Vercel production variables added"

#!/usr/bin/env sh

npm run build
firebase deploy -P production --token "$FIREBASE_DEPLOY_TOKEN"

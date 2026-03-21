#!/bin/bash
# Run once from inside this folder
# Requires gh CLI: brew install gh && gh auth login

gh repo create agentnxxt/agentskills \
  --public \
  --description "Autonomyx Claude skills for enterprise SaaS evaluation and feature gap analysis" \
  --source=. \
  --remote=origin \
  --push

echo "Live at: https://github.com/agentnxxt/agentskills"

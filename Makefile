# OpenAutonomyX — Monorepo
# Usage: make <target>

.PHONY: help build lint validate deploy deploy-oax

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

build: ## Build all skills into infra/dist/
	@echo "Building skills..."
	@node scripts/build-skills.js

lint: ## Lint all skill definitions
	@node scripts/lint-skills.js

validate: ## Validate Docker Compose configs
	@docker compose -f infra/deployments/docker-compose.yml config --quiet && \
		echo "  [OK] infra/deployments"
	@docker compose -f infra/deployments/openautonomyx-com/docker-compose.yml config --quiet && \
		echo "  [OK] infra/openautonomyx-com"

deploy: ## Deploy agnxxt.com stack
	@cd infra/deployments && ./deploy.sh

deploy-oax: ## Deploy www.openautonomyx.com
	@cd infra/deployments/openautonomyx-com && ./deploy.sh

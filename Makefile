
SHELL := /bin/bash
PROJECT_ROOT := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))
PY_SERVICE := apps/svc-template-fastapi
NODE_SERVICE := apps/svc-template-node
WEB_APP := apps/web-next
REGISTRY ?= ghcr.io/yourorg
IMAGE_TAG ?= $(shell git rev-parse --short HEAD)
ENV ?= dev

.PHONY: setup test build compose-up fly-deploy ecs-deploy k8s-apply rollback lint

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -e $(PY_SERVICE)[dev]
	npm install --prefix $(NODE_SERVICE)
	npm install --prefix $(WEB_APP)
	@if command -v pre-commit >/dev/null 2>&1; then pre-commit install; fi

lint:
	. .venv/bin/activate && python -m compileall $(PY_SERVICE)/app
	npm run lint --prefix $(NODE_SERVICE)
	npm run lint --prefix $(WEB_APP)

test: lint
	. .venv/bin/activate && pytest $(PY_SERVICE)/tests
	npm test --prefix $(NODE_SERVICE)
	npm run build --prefix $(WEB_APP)

build:
	docker buildx build --platform linux/amd64,linux/arm64 -t $(REGISTRY)/svc-template-fastapi:$(IMAGE_TAG) $(PY_SERVICE)
	docker buildx build --platform linux/amd64,linux/arm64 -t $(REGISTRY)/svc-template-node:$(IMAGE_TAG) $(NODE_SERVICE)
	docker buildx build --platform linux/amd64,linux/arm64 -t $(REGISTRY)/web-next:$(IMAGE_TAG) $(WEB_APP)

compose-up:
	docker compose -f docker-compose.prod.yml up --detach

fly-deploy: build
	fly deploy --config infra/terraform/fly/fly.toml --image $(REGISTRY)/svc-template-fastapi:$(IMAGE_TAG)

ecs-deploy:
	cd infra/terraform/aws && terraform init && terraform apply -auto-approve

k8s-apply:
	@if [ -z "$(ENV)" ]; then echo "ENV must be set" && exit 1; fi
	kubectl apply -k infra/k8s/overlays/$(ENV)

rollback:
	./ops/scripts/rollback.sh $(REGISTRY) $(IMAGE_TAG)

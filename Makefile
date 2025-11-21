.RECIPEPREFIX = >
.PHONY: setup test lint demo validate dc-up dc-test dc-shell build run deploy preview-destroy
.PHONY: setup test lint demo validate dc-up dc-test dc-shell build run deploy preview-destroy notify lint-observability
.PHONY: setup test lint demo validate dc-up dc-test dc-shell build run deploy preview-destroy mpm-core energy
.PHONY: setup test lint demo validate dc-up dc-test dc-shell build run deploy preview-destroy docs

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
.DEFAULT_GOAL := test

VENV ?= .venv
PYTHON ?= python3
SAFE_MODE ?= 1

export SAFE_MODE

.PHONY: install test demo encompass-demo clean demo-cross-ratio demo-spectral-gap demo-angle-defect demo-invariants

install:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -U pip wheel
	. $(VENV)/bin/activate && pip install -U pytest numpy scipy hypothesis

# Run all tests with repo root on PYTHONPATH
test: install
	. $(VENV)/bin/activate && SAFE_MODE=$(SAFE_MODE) PYTHONPATH=$(PWD) pytest -q

# Optional: run the headline demo
demo: install
        . $(VENV)/bin/activate && SAFE_MODE=$(SAFE_MODE) PYTHONPATH=$(PWD) python scripts/demo_amundson_math_core.py
        . $(VENV)/bin/activate && PYTHONPATH=$(PWD) python scripts/demo_amundson_math_core.py

demo-cross-ratio: install
        mkdir -p data/demos
        . $(VENV)/bin/activate && PYTHONPATH=$(PWD) python tools/projective/cross_ratio.py 0,0 1,0 2,0 4,0 > data/demos/cross_ratio.txt

demo-spectral-gap: install
        mkdir -p data/demos
        printf "0 1\n1 2\n0 2\n" > data/demos/spectral_gap_edges.txt
        . $(VENV)/bin/activate && PYTHONPATH=$(PWD) python tools/dynamics/spectral_gap.py data/demos/spectral_gap_edges.txt > data/demos/spectral_gap.txt

demo-angle-defect: install
        mkdir -p data/demos
        cat <<'OBJ' > data/demos/tetrahedron.obj
v 0 0 0
v 1 0 0
v 0 1 0
v 0 0 1
f 1 2 3
f 1 4 2
f 2 4 3
f 3 4 1
OBJ
        . $(VENV)/bin/activate && PYTHONPATH=$(PWD) python tools/geometry/angle_defect.py data/demos/tetrahedron.obj --output data/demos/angle_defects.csv > data/demos/angle_defect_summary.txt

demo-invariants: demo-cross-ratio demo-spectral-gap demo-angle-defect

encompass-demo: install
        . $(VENV)/bin/activate && PYTHONPATH=$(PWD) python scripts/encompass_demo.py --prompt "Who are we?" --pretty --output ui/lucidia_viewer/packets.json

clean:
        rm -rf $(VENV) .pytest_cache __pycache__ */__pycache__


# Branch Cleanup Targets
BR_TOKEN ?= $(BRANCH_CLEANUP_TOKEN)

.PHONY: branch-cleanup-dry branch-cleanup-run branch-cleanup-report

branch-cleanup-dry:
	@echo "🔍 Dry run - preview branch cleanup..."
	@BRANCH_CLEANUP_TOKEN=$(BR_TOKEN) npx tsx tools/branch-cleanup/cleanup.ts --dry-run

branch-cleanup-run:
	@echo "🚀 Executing live cleanup..."
	@BRANCH_CLEANUP_TOKEN=$(BR_TOKEN) npx tsx tools/branch-cleanup/cleanup.ts

branch-cleanup-report:
	@echo "📊 Latest cleanup reports:"
	@ls -lah ops/reports/branch-cleanup 2>/dev/null || echo "No reports yet"

>. .venv/bin/activate && ruff .

lint-observability:
>python -m observability.lint

validate:
>. .venv/bin/activate && python scripts/validate_contracts.py

demo:
>brc plm:items:load --dir fixtures/plm/items && \
>brc plm:bom:load --dir fixtures/plm/boms && \
>brc plm:bom:explode --item PROD-100 --rev A --level 3 && \
>brc mfg:wc:load --file fixtures/mfg/work_centers.csv && \
>brc mfg:routing:load --dir fixtures/mfg/routings && \
>brc mfg:routing:capcheck --item PROD-100 --rev B --qty 1000 && \
>brc mfg:wi:render --item PROD-100 --rev B && \
>brc mfg:spc:analyze --op OP-200 --window 50 && \
>brc mfg:yield --period 2025-09 && \
>brc mfg:mrp --demand artifacts/sop/allocations.csv --inventory fixtures/mfg/inventory.csv --pos fixtures/mfg/open_pos.csv && \
>brc mfg:coq --period 2025-Q3

build:
>docker build -t blackroad/prism-console:dev -f Dockerfile .

run:
>docker compose up --build app

deploy:
>@test -n "$(PR)" || (echo "PR=<number> is required" >&2 && exit 1)
>PR_NUMBER=$(PR) PROJECT_NAME=prism-console scripts/devx/deploy_preview.sh apply

preview-destroy:
>@test -n "$(PR)" || (echo "PR=<number> is required" >&2 && exit 1)
>PR_NUMBER=$(PR) PROJECT_NAME=prism-console scripts/devx/deploy_preview.sh destroy

dc-up:
>docker compose up --build app

dc-test:
>docker compose run --rm tests

dc-shell:
>docker compose run --rm app bash

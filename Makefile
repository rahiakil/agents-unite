.PHONY: help assign run validate commit stats aggregate readme check

help:
	@echo "Agents Unite — make targets"
	@echo ""
	@echo "  make run        Assign ticker, scaffold files, save prompt"
	@echo "  make agent      Assign + run built-in LLM harness"
	@echo "  make assign     Print today's ticker assignment (JSON)"
	@echo "  make validate   Validate all reports under data/"
	@echo "  make commit     Validate + commit today's report"
	@echo "  make stats      Print dataset statistics"
	@echo "  make aggregate  Generate today's summary index"
	@echo "  make readme     Regenerate live README sections"
	@echo "  make wiki       List pending wiki ingests"
	@echo "  make install-cron  Interactive cron + config setup"
	@echo "  make daily         Run daily pipeline (cron entrypoint)"
	@echo "  make check      Validate all example + demo reports"

run:
	./scripts/run-agent.sh

agent:
	./scripts/run-agent.sh --run

assign:
	python3 scripts/assign_ticker.py --json

validate:
	python3 scripts/validate_report.py

commit:
	./scripts/commit-report.sh

stats:
	python3 scripts/stats.py

aggregate:
	python3 scripts/aggregate.py

readme:
	python3 scripts/generate_readme.py

wiki:
	python3 scripts/wiki_ingest.py

wiki-prompt:
	python3 scripts/wiki_ingest.py --prompt

install-cron:
	./scripts/install-cron.sh

daily:
	./scripts/daily-run.sh

check:
	python3 scripts/validate_report.py data/2026-06-05/AAPL data/2026-06-05/TSLA data/2026-06-05/NVDA

.PHONY: install lint typecheck test demo eval dashboard clean help

PYTHON := uv run python
UV := uv
STREAMLIT := uv run streamlit

help:
	@echo "SwapTrace — Battery Intelligence Pipeline"
	@echo ""
	@echo "Available commands:"
	@echo "  install     Install all dependencies"
	@echo "  lint        Run Ruff linter"
	@echo "  typecheck   Run mypy type checker"
	@echo "  test        Run all tests"
	@echo "  demo        Run full pipeline (generate → validate → feature → attribute → alert)"
	@echo "  eval        Run evaluation on benchmark held-out data"
	@echo "  dashboard   Launch Streamlit operator dashboard"
	@echo "  clean       Remove generated artifacts and data"

install:
	$(UV) sync --locked --extra dev

lint:
	$(UV) run ruff check src/ tests/ benchmark/ --fix

typecheck:
	$(UV) run mypy src/swaptrace/ --ignore-missing-imports --no-strict-optional

test:
	$(UV) run python -m pytest tests/ -v --tb=short

demo:
	$(UV) run python -m swaptrace.cli demo --seed 42

eval:
	$(UV) run python -m swaptrace.cli eval --seed 42

dashboard:
	$(UV) run streamlit run app/dashboard.py --server.headless false --server.port 8501

clean:
	rm -rf data/swaptrace.db data/derived data/validated data/raw/ground_truth.json
	rm -rf artifacts/alerts/alerts.json artifacts/evaluation/evaluation_report.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

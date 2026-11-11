.PHONY: test test-gate test-registry test-serving test-drift test-rollback test-integration \
        failure-injection serve clean

test:
	pytest tests/ -v

test-gate:
	pytest tests/gate/ -v

test-registry:
	pytest tests/registry/ -v

test-serving:
	pytest tests/serving/ -v

test-drift:
	pytest tests/drift/ -v

test-rollback:
	pytest tests/rollback/ -v

test-integration:
	pytest tests/integration/ -v

failure-injection:
	python scripts/failure_injection.py

serve:
	uvicorn src.platform.serving.app:app --host 0.0.0.0 --port 8000

clean:
	rm -f registry.db
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

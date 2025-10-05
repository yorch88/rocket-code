#!/usr/bin/env bash
set -euo pipefail

echo "⏳ Waiting for DB..."
python app/scripts/wait_for_db.py

# Avoid problematic local templates
if [ -f /app/alembic.ini ]; then
  sed -i '/^revision_template/d' /app/alembic.ini || true
fi

# Warm-up: ensure 'app' and 'models' are imported and that 'articles' is in Base.metadata
python - <<'PY'
import sys, os
sys.path.insert(0, "/app")
import importlib

print("🔎 Importing app and models...")
app = importlib.import_module("app")
models = importlib.import_module("app.models")  # <- important: executes models
dbmod = importlib.import_module("app.db")       # <- must export Base
Base = getattr(dbmod, "Base", None)

if Base is None:
    raise SystemExit("❌ 'Base' not found in app.db. Make sure it is re-exported in app/db/__init__.py")

tables = list(Base.metadata.tables.keys())
print("🗂️  Tables detected by Alembic:", tables)
if "articles" not in tables:
    raise SystemExit("❌ Alembic does not detect 'articles' in Base.metadata. Check your imports and __tablename__.")
print("✅ Models OK: 'articles' visible in metadata")
PY

# If there are no migrations, auto-generate one
if [ -z "$(ls -A /app/alembic/versions 2>/dev/null || true)" ]; then
  echo "📝 No migrations found. Autogenerating..."
  alembic -c /app/alembic.ini revision --autogenerate -m "init"
fi

# Always apply upgrade head
echo "🛠️  Applying migrations (upgrade head)..."
alembic -c /app/alembic.ini upgrade head

echo "🚀 Starting Uvicorn (reload enabled)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 \
  --reload --reload-dir /app/app --reload-include '*.py' --reload-exclude '*.pyc'

<# -------------
   fix-alembic.ps1
   Usage:  powershell -ExecutionPolicy Bypass -File .\fix-alembic.ps1
   Make sure you run it from the folder that contains alembic.ini
-------------#>

param(
  [string]$Message = "initial schema"
)

Write-Host "`n=== Alembic auto-repair ===`n"

# 1️⃣  Locate active env.py (first on PYTHONPATH)
$envPath   = python - <<'PY'
import importlib.util, sys, pathlib
spec = importlib.util.find_spec("alembic.config")
if not spec: 
    print("")
    sys.exit(1)
cfg = pathlib.Path(spec.origin).parent.parent  # site-packages/alembic -> project root for alembic pkg
print(cfg)
PY

if (-not $envPath) {
    Write-Error "Could not find Alembic package. Activate your venv and retry."
    exit 1
}

$projectRoot = Get-Location
$envFile     = "$($envPath)\env.py"

Write-Host "Will patch: $envFile"

# 2️⃣  Overwrite env.py with good template that uses metadata
$goodEnv = @'
import os, sys
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

load_dotenv()

# Put project root on path
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..', '..')))

# ---- models import ----
from backend.db import models                         # <-- your models.py
target_metadata = models.metadata
# -----------------------

config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL") or "sqlite:///dummy.db")

fileConfig(config.config_file_name)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'@

Set-Content -Path $envFile -Value $goodEnv -Encoding UTF8
Write-Host "✓ Patched env.py`n"

# 3️⃣  (re)activate venv if needed
if (-not $Env:VIRTUAL_ENV) {
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        . .\venv\Scripts\Activate.ps1
        Write-Host "✓ Virtual-env activated"
    } else {
        Write-Error "No venv found. Abort."
        exit 1
    }
}

# 4️⃣  Run migrations
alembic revision --autogenerate -m $Message
alembic upgrade head
Write-Host "`n=== Done ===`n"

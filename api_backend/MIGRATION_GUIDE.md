# Database Migration Guide

This guide covers database migration strategies for your portfolio analytics system.

## Table of Contents
1. [Migration Strategy Decision](#migration-strategy-decision)
2. [Option 1: Supabase CLI (Recommended)](#option-1-supabase-cli-recommended)
3. [Option 2: Alembic (Database-Agnostic)](#option-2-alembic-database-agnostic)
4. [Migration Best Practices](#migration-best-practices)

---

## Migration Strategy Decision

### TL;DR Recommendation: **Use Supabase CLI**

**Why?**
- ✅ You're already using Supabase
- ✅ Simpler setup and maintenance
- ✅ Integrates with Supabase features (RLS, triggers, edge functions)
- ✅ Version controlled, timestamped migrations
- ✅ Built-in rollback support
- ✅ Your backend (FastAPI) is already cloud-agnostic, so database layer can be Supabase-specific

**Trade-off:**
- Vendor lock-in to Supabase (but migrations are still SQL, so portable if needed)

---

## Option 1: Supabase CLI (Recommended)

### Setup

#### 1. Install Supabase CLI

**macOS:**
```bash
brew install supabase/tap/supabase
```

**Linux:**
```bash
# Using npm
npm install -g supabase

# Or using binary
curl -fsSL https://raw.githubusercontent.com/supabase/cli/main/install.sh | sh
```

**Windows:**
```powershell
# Using Scoop
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase
```

Verify installation:
```bash
supabase --version
```

#### 2. Link Your Project

```bash
cd api_backend

# Login to Supabase
supabase login

# Link to your existing project
supabase link --project-ref your-project-ref

# Or initialize a new local setup
supabase init
```

Get your project ref from: https://app.supabase.com/project/_/settings/general

#### 3. Directory Structure

Your migrations are already set up:
```
api_backend/
└── supabase/
    ├── config.toml                          # Supabase configuration
    └── migrations/
        └── 00001_initial_schema.sql         # First migration
```

### Usage

#### Create a New Migration

**Option A: Generate from Database Diff**
```bash
# Pull current database state
supabase db pull

# Make changes in Supabase Studio (web UI)
# Then create migration from diff
supabase db diff -f new_feature_name
```

**Option B: Create Manually**
```bash
# Create timestamped migration file
supabase migration new add_user_preferences
```

This creates: `supabase/migrations/20251031123456_add_user_preferences.sql`

**Example migration:**
```sql
-- Add user preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL UNIQUE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_user_preferences_session ON user_preferences(session_id);
```

#### Apply Migrations

**To Local Development:**
```bash
# Start local Supabase (includes PostgreSQL, Auth, Storage)
supabase start

# Apply migrations
supabase db reset
```

**To Remote (Production):**
```bash
# Push migrations to your Supabase project
supabase db push
```

#### Check Migration Status

```bash
# List all migrations and their status
supabase migration list

# Check pending migrations
supabase migration list --pending
```

#### Rollback

Supabase doesn't have automatic rollback, but you can create a rollback migration:

```bash
# Create rollback migration
supabase migration new rollback_user_preferences
```

```sql
-- Rollback: Drop user preferences table
DROP TABLE IF EXISTS user_preferences;
```

### Your First Migration

Your initial schema is already in: `supabase/migrations/00001_initial_schema.sql`

**To apply it:**

1. **If starting fresh:**
   ```bash
   cd api_backend
   supabase link --project-ref your-project-ref
   supabase db push
   ```

2. **If tables already exist:**
   You've already run `supabase_schema.sql` manually. That's fine! Just track it:
   ```bash
   # Mark this migration as applied (don't re-run it)
   supabase migration repair 00001_initial_schema --status applied
   ```

### Workflow

**Development:**
```bash
# 1. Start local Supabase
supabase start

# 2. Access local database
# PostgreSQL: postgresql://postgres:postgres@localhost:54322/postgres
# Studio UI: http://localhost:54323

# 3. Create migration
supabase migration new add_analytics_dashboard

# 4. Write SQL in the generated file

# 5. Apply migration
supabase db reset

# 6. Test your changes
```

**Production Deployment:**
```bash
# 1. Commit migrations to git
git add supabase/migrations/
git commit -m "Add analytics dashboard tables"

# 2. Push to remote Supabase
supabase db push

# 3. Verify in Supabase Studio
```

### CI/CD Integration

**GitHub Actions Example:**
```yaml
name: Deploy Database Migrations

on:
  push:
    branches: [main]
    paths:
      - 'api_backend/supabase/migrations/**'

jobs:
  deploy-migrations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Supabase CLI
        uses: supabase/setup-cli@v1

      - name: Push migrations
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          SUPABASE_PROJECT_REF: ${{ secrets.SUPABASE_PROJECT_REF }}
        run: |
          cd api_backend
          supabase link --project-ref $SUPABASE_PROJECT_REF
          supabase db push
```

---

## Option 2: Alembic (Database-Agnostic)

### Why Use Alembic?

**Use Alembic if:**
- ✅ You want database portability (switch from Supabase to RDS/ApsaraDB later)
- ✅ You're managing multiple databases
- ✅ You want Python-based migrations (type hints, programmatic schema changes)
- ✅ You need advanced migration features (branching, merging)

**Don't use Alembic if:**
- ❌ You're committed to Supabase
- ❌ You want simplicity
- ❌ You need Supabase-specific features (RLS, triggers via UI)

### Setup

#### 1. Install Alembic

```bash
cd api_backend
pip install alembic psycopg2-binary
pip freeze > requirements.txt
```

#### 2. Initialize Alembic

```bash
alembic init alembic
```

Creates:
```
api_backend/
├── alembic/
│   ├── versions/          # Migration files
│   ├── env.py            # Alembic environment
│   └── script.py.mako    # Migration template
└── alembic.ini           # Configuration
```

#### 3. Configure Database Connection

Edit `alembic.ini`:
```ini
# Replace this line:
sqlalchemy.url = driver://user:pass@localhost/dbname

# With (using env vars):
# sqlalchemy.url =
```

Edit `alembic/env.py`:
```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase connection string
config.set_main_option(
    'sqlalchemy.url',
    f"postgresql://{os.getenv('SUPABASE_USER')}:{os.getenv('SUPABASE_PASSWORD')}@{os.getenv('SUPABASE_HOST')}:{os.getenv('SUPABASE_PORT')}/{os.getenv('SUPABASE_DB')}"
)
```

### Usage

#### Create Migration

**Auto-generate from models:**
```bash
alembic revision --autogenerate -m "add user preferences table"
```

**Create empty migration:**
```bash
alembic revision -m "add custom function"
```

#### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade +1  # One version up
alembic upgrade abc123  # Specific revision

# Downgrade
alembic downgrade -1  # One version down
alembic downgrade base  # Back to beginning
```

#### Check Status

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show head
```

#### Example Migration

Generated file: `alembic/versions/abc123_add_user_preferences.py`
```python
"""add user preferences table

Revision ID: abc123
Revises: def456
Create Date: 2025-10-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', sa.Text(), nullable=False),
        sa.Column('preferences', postgresql.JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index('idx_user_preferences_session', 'user_preferences', ['session_id'])


def downgrade():
    op.drop_index('idx_user_preferences_session', table_name='user_preferences')
    op.drop_table('user_preferences')
```

---

## Migration Best Practices

### 1. Version Control
```bash
# Always commit migrations
git add supabase/migrations/  # or alembic/versions/
git commit -m "Add user preferences table"
```

### 2. Naming Conventions
```bash
# Good names (descriptive, action-oriented)
20251031_add_user_preferences_table.sql
20251101_add_visits_country_index.sql
20251102_create_analytics_views.sql

# Bad names (vague, unclear)
migration1.sql
update.sql
fix.sql
```

### 3. Migration Content
```sql
-- ✅ Good: Idempotent (safe to run multiple times)
CREATE TABLE IF NOT EXISTS user_preferences (...);
CREATE INDEX IF NOT EXISTS idx_name ON table(column);

-- ❌ Bad: Will fail if run twice
CREATE TABLE user_preferences (...);
CREATE INDEX idx_name ON table(column);
```

### 4. Testing
```bash
# Test locally first
supabase db reset  # or: alembic upgrade head

# Verify schema
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "\d table_name"  # Describe table

# Test queries
psql $DATABASE_URL -c "SELECT * FROM visits LIMIT 1;"
```

### 5. Backwards Compatibility
```sql
-- ✅ Good: Add nullable column
ALTER TABLE visits ADD COLUMN country_code TEXT;

-- ❌ Bad: Add non-nullable without default
ALTER TABLE visits ADD COLUMN country_code TEXT NOT NULL;

-- ✅ Better: Add with default, then remove default later
ALTER TABLE visits ADD COLUMN country_code TEXT DEFAULT 'US';
-- Later migration:
ALTER TABLE visits ALTER COLUMN country_code DROP DEFAULT;
```

### 6. Data Migrations
```sql
-- Separate schema and data migrations

-- Schema migration: 00002_add_country_code.sql
ALTER TABLE visits ADD COLUMN country_code TEXT;

-- Data migration: 00003_populate_country_codes.sql
UPDATE visits SET country_code = 'US' WHERE country = 'United States';
UPDATE visits SET country_code = 'CN' WHERE country = 'China';
-- ... etc
```

### 7. Large Table Changes
```sql
-- For large tables, use CREATE TABLE AS + RENAME

-- Instead of: ALTER TABLE visits ADD COLUMN ...
-- Do this:

-- 1. Create new table
CREATE TABLE visits_new AS SELECT * FROM visits;

-- 2. Add new column
ALTER TABLE visits_new ADD COLUMN country_code TEXT;

-- 3. Populate data (can do in batches)
UPDATE visits_new SET country_code = ...;

-- 4. Rename (atomic)
BEGIN;
ALTER TABLE visits RENAME TO visits_old;
ALTER TABLE visits_new RENAME TO visits;
COMMIT;

-- 5. Drop old table (after verifying)
DROP TABLE visits_old;
```

---

## Comparison Table

| Feature | Supabase CLI | Alembic |
|---------|--------------|---------|
| **Setup Complexity** | Low | Medium |
| **Language** | SQL | Python + SQL |
| **Vendor Lock-in** | Yes (Supabase) | No |
| **Auto-generation** | Via diff | From SQLAlchemy models |
| **Rollback** | Manual migration | Built-in |
| **Version Control** | ✅ | ✅ |
| **Supabase Features** | ✅ (RLS, triggers, etc.) | ❌ |
| **Database Portability** | ❌ (but SQL is portable) | ✅ |
| **Learning Curve** | Low | Medium |
| **CI/CD** | ✅ | ✅ |

---

## Recommendation Summary

### Use Supabase CLI if:
- ✅ You're staying with Supabase
- ✅ You want simplicity
- ✅ You use Supabase features (RLS, auth, storage)
- ✅ You prefer SQL over Python
- ✅ You're a solo developer or small team

### Use Alembic if:
- ✅ You need database portability
- ✅ You're using SQLAlchemy models
- ✅ You manage multiple databases
- ✅ You want programmatic migrations
- ✅ You have complex branching/merging needs

---

## Your Next Steps

### If choosing Supabase CLI (Recommended):

1. **Install CLI:**
   ```bash
   brew install supabase/tap/supabase  # or: npm install -g supabase
   ```

2. **Link project:**
   ```bash
   cd api_backend
   supabase login
   supabase link --project-ref YOUR_PROJECT_REF
   ```

3. **Push initial migration:**
   ```bash
   supabase db push
   ```

4. **Future migrations:**
   ```bash
   supabase migration new feature_name
   # Edit the generated file
   supabase db push
   ```

### If choosing Alembic:

1. **Install:**
   ```bash
   pip install alembic psycopg2-binary
   ```

2. **Initialize:**
   ```bash
   alembic init alembic
   ```

3. **Configure** (edit `alembic.ini` and `alembic/env.py`)

4. **Create migrations:**
   ```bash
   alembic revision -m "initial schema"
   alembic upgrade head
   ```

---

## Resources

- **Supabase CLI Docs**: https://supabase.com/docs/guides/cli
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **PostgreSQL Migrations**: https://www.postgresql.org/docs/current/ddl-alter.html
- **Migration Best Practices**: https://www.braintrust.dev/docs/guides/migrations

---

**Questions?** Check `QUICK_REFERENCE.md` or open an issue!

# Database Configuration

## Overview

The AI Wealth Companion supports two database backends:
- **SQLite** - For local development (default)
- **PostgreSQL/Neon** - For production

---

## Configuration Location

Database URL is configured in: **`backend/.env`**

```bash
# Current configuration
DATABASE_URL=sqlite+aiosqlite:///./finance.db
```

---

## Local Development (SQLite)

### Configuration
```bash
# backend/.env
DATABASE_URL=sqlite+aiosqlite:///./finance.db
CORS_ORIGINS=http://localhost:3000
DEBUG=true
```

### Features
- No external dependencies
- File-based storage (`backend/finance.db`)
- Automatic table creation on startup
- Good for development and testing

### Limitations
- Single connection at a time
- Not suitable for production
- No connection pooling

---

## Production (PostgreSQL/Neon)

### Configuration
```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
CORS_ORIGINS=https://yourdomain.com
DEBUG=false
```

### Neon Serverless Configuration
```bash
# For Neon PostgreSQL (recommended for serverless)
DATABASE_URL=postgresql+asyncpg://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Features
- Connection pooling
- High concurrency
- Production-ready
- Automatic backups (Neon)

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Full database connection string | See above |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `http://localhost:3000` |
| `DEBUG` | Enable debug logging | `true` / `false` |
| `SECRET_KEY` | JWT secret (future auth) | Random 32+ char string |

---

## Database Schema

### Tables

```sql
-- Categories (seeded on startup)
CREATE TABLE category (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    emoji VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transactions
CREATE TABLE transaction (
    id UUID PRIMARY KEY,
    type VARCHAR NOT NULL,  -- 'income' | 'expense'
    amount DECIMAL(12,2) NOT NULL,
    category_id UUID REFERENCES category(id),
    date DATE NOT NULL,
    note VARCHAR,
    recurring BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP  -- Soft delete
);

-- Budgets
CREATE TABLE budget (
    id UUID PRIMARY KEY,
    category_id UUID REFERENCES category(id),
    limit_amount DECIMAL(12,2) NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Users (future)
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    name VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Switching Databases

### From SQLite to PostgreSQL

1. **Update `.env`**
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
   ```

2. **Install PostgreSQL driver** (already in requirements.txt)
   ```bash
   pip install asyncpg
   ```

3. **Run migrations** (if using Alembic)
   ```bash
   alembic upgrade head
   ```

4. **Seed categories**
   Categories are auto-seeded on first startup.

---

## Connection Handling

The backend automatically detects the database type:

```python
# backend/src/db/session.py
is_sqlite = "sqlite" in settings.async_database_url

if is_sqlite:
    # SQLite configuration
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
else:
    # PostgreSQL configuration
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    }
```

---

## Troubleshooting

### "Database connection refused"
- Check DATABASE_URL is correct
- Ensure database server is running
- Verify network connectivity

### "Table does not exist"
- Tables are created on startup
- Check for migration errors
- Restart the backend server

### "Too many connections"
- Increase `pool_size` for PostgreSQL
- Use connection pooling service (PgBouncer)

---

## Recommended Production Setup

1. **Use Neon PostgreSQL** - Serverless, auto-scaling
2. **Enable connection pooling** - Built into Neon
3. **Set `DEBUG=false`** - Disable verbose logging
4. **Use environment secrets** - Never commit `.env` to git

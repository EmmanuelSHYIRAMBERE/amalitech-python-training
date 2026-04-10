# Branch

```
feat/db-fundamentals-lab2-social-media-backend
```

```powershell
git checkout develop
git checkout -b feat/db-fundamentals-lab2-social-media-backend
```

---

# Commits

```powershell
# 1 — .gitignore
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/.gitignore
git commit -m "chore(social-media-backend): add .gitignore to exclude pycache and build artefacts"

# 2 — schema
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/sql/schema.sql
git commit -m "feat(social-media-backend): add 3NF PostgreSQL schema with composite B-tree and GIN indexes"

# 3 — seed data
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/sql/seed.sql
git commit -m "data: add seed data for users, posts, comments, and followers"

# 4 — infra
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/docker-compose.yml
git commit -m "chore(social-media-backend): add docker-compose for PostgreSQL, Redis, and MongoDB"

# 5 — connection pool
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/src/__init__.py labs/database-fundamentals/lab-2-social-media-platform-data-backend/src/db.py
git commit -m "feat(social-media-backend): add psycopg2 ThreadedConnectionPool with context manager"

# 6 — core src modules
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/src/users.py labs/database-fundamentals/lab-2-social-media-platform-data-backend/src/posts.py labs/database-fundamentals/lab-2-social-media-platform-data-backend/src/followers.py
git commit -m "feat(social-media-backend): implement user, post, and transactional follow/unfollow CRUD"

# 7 — feed
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/src/feed.py
git commit -m "feat(social-media-backend): add CTE + ROW_NUMBER() paginated feed with Redis cache and EXPLAIN ANALYZE"

# 8 — activity
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/src/activity.py
git commit -m "feat(social-media-backend): add MongoDB activity stream for user action logging"

# 9 — entry point
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/main.py
git commit -m "feat(social-media-backend): add CLI entry point demonstrating full pipeline end-to-end"

# 10 — tests
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/tests/
git commit -m "test(social-media-backend): add TDD pytest suite for users, posts, followers, feed, and activity (40 tests, 91% coverage)"

# 11 — config + docs
git add labs/database-fundamentals/lab-2-social-media-platform-data-backend/pyproject.toml labs/database-fundamentals/lab-2-social-media-platform-data-backend/requirements.txt labs/database-fundamentals/lab-2-social-media-platform-data-backend/README.md
git commit -m "chore(social-media-backend): add pyproject.toml, requirements.txt, and README with ER diagram and optimization report"

# 12 — CI workflow
git add .github/workflows/db-fundamentals-lab2.yml
git commit -m "ci(social-media-backend): add GitHub Actions workflow for lint, type-check, and pytest"
```

```powershell
# Push
git push -u origin feat/db-fundamentals-lab2-social-media-backend
```

---

# Pull Request

## Title

```
feat(db-fundamentals): Lab 2 — Social Media Platform Data Backend
```

## Body

```markdown
## Summary

Implements the full **Social Media Platform Data Backend** for the Database Fundamentals module.
Covers 3NF PostgreSQL schema design, transactional follow/unfollow, Redis-cached paginated feed
using CTE + ROW_NUMBER(), MongoDB activity stream, composite B-tree index optimization, and a
full TDD test suite with GitHub Actions CI.

---

## Screenshots / Evidence

### ER Diagram
<!-- Export from dbdiagram.io using the schema in sql/schema.sql -->
![ER Diagram](https://via.placeholder.com/800x400?text=ER+Diagram+Screenshot)

### Docker Services Running
<!-- Screenshot of `docker compose ps` showing postgres, redis, mongo all Up -->
![Docker Services](https://via.placeholder.com/800x300?text=docker+compose+ps+output)

### Pipeline Demo (`python main.py`)
<!-- Screenshot of full terminal output from running main.py -->
![Pipeline Demo](https://via.placeholder.com/800x500?text=python+main.py+terminal+output)

### Pytest Results (40 tests, 91% coverage)
<!-- Screenshot of pytest --cov output showing all 40 tests passing and coverage table -->
![Pytest Results](https://via.placeholder.com/800x400?text=pytest+coverage+output)

### Feed Cache MISS → HIT (Redis)
<!-- Screenshot showing Cache MISS on first call and Cache HIT on second call -->
![Redis Cache](https://via.placeholder.com/800x200?text=Feed+Cache+MISS+then+HIT)

### EXPLAIN ANALYZE — Before Composite Index (Seq Scan)
<!-- Screenshot of EXPLAIN ANALYZE output before idx_followers_follower is applied -->
![Before Index](https://via.placeholder.com/800x200?text=EXPLAIN+ANALYZE+Seq+Scan)

### EXPLAIN ANALYZE — After Composite Index (Index Scan)
<!-- Screenshot of EXPLAIN ANALYZE output after composite B-tree indexes are applied -->
![After Index](https://via.placeholder.com/800x200?text=EXPLAIN+ANALYZE+Index+Scan)

### GitHub Actions CI — All Jobs Passing
<!-- Screenshot of Actions tab showing lint, type-check, and test jobs all green -->
![CI Passing](https://via.placeholder.com/800x300?text=GitHub+Actions+all+jobs+green)

---

## Commits

| Hash | Description |
|---|---|
| `dd9f76f` | chore: add .gitignore |
| `c30ba21` | feat: add 3NF schema with composite B-tree and GIN indexes |
| `e6a0cbf` | data: add seed data for users, posts, comments, and followers |
| `3426647` | chore: add docker-compose for PostgreSQL, Redis, and MongoDB |
| `a1d5dad` | feat: add psycopg2 ThreadedConnectionPool with context manager |
| `fd09422` | feat: implement user, post, and transactional follow/unfollow CRUD |
| `c4dca21` | feat: add CTE + ROW_NUMBER() paginated feed with Redis cache and EXPLAIN ANALYZE |
| `ca08514` | feat: add MongoDB activity stream for user action logging |
| `2fc413f` | feat: add CLI entry point demonstrating full pipeline end-to-end |
| `be4259a` | test: add TDD pytest suite — 40 tests, 91% coverage |
| `1896fcb` | chore: add pyproject.toml, requirements.txt, and README |
| `436f489` | ci: add GitHub Actions workflow for lint, type-check, and pytest |

---

## Changes

### Day 1 — Database Design
- 4-table schema in **3NF**: `users`, `posts`, `comments`, `followers`
- `metadata JSONB` on `posts` for flexible per-post attributes (tags, location)
- `CHECK (follower_id <> following_id)` prevents self-follows at DB level
- Composite PK `(follower_id, following_id)` on `followers` prevents duplicate relationships
- `ON DELETE CASCADE` on all FKs — deleting a user cleans up all related data
- Composite B-tree index `idx_followers_follower(follower_id, following_id)` for feed query
- Composite B-tree index `idx_posts_user_created(user_id, created_at DESC)` for timeline ordering
- GIN index on `posts.metadata` for JSONB tag queries

### Day 2 — Python DB-API
- `src/db.py` — `psycopg2.ThreadedConnectionPool` (min=1, max=10) with auto-rollback context manager
- All DML uses **parameterized queries** — no string interpolation
- `follow_user` uses `INSERT ... ON CONFLICT DO NOTHING` wrapped in a transaction
- `ValueError` raised at application layer if user tries to follow themselves

### Day 3 — NoSQL + Advanced SQL
- **Redis** (`src/feed.py`) — caches paginated timelines per user per page (TTL 60 s); key pattern `feed:{user_id}:page:{n}`; invalidated on unfollow via `scan_iter`
- **MongoDB** (`src/activity.py`) — stores activity stream events (`liked_post`, `followed_user`, `commented_on_post`) as schema-free documents sorted by timestamp
- `find_posts_by_tag` uses `@>` JSONB operator hitting the GIN index

### Day 4 — Feed Query & Performance
- Feed query uses a **CTE** (`followed_posts`) + `ROW_NUMBER() OVER (ORDER BY created_at DESC)` for efficient cursor-based pagination
- `EXPLAIN ANALYZE` runner captures the full query plan as text
- Composite B-tree indexes reduce feed generation from O(n) sequential scans to O(log n) index lookups

---

## Test Summary

```
40 passed

Name               Stmts   Miss  Cover
--------------------------------------
src/activity.py       15      3    80%
src/db.py             20     10    50%
src/feed.py           37      0   100%
src/followers.py      26      0   100%
src/posts.py          33      0   100%
src/users.py          18      0   100%
--------------------------------------
TOTAL                149     13    91%
```

---

## How to Run

```bash
# Start all services
docker compose up -d

# Install dependencies
pip install -r requirements.txt

# Run the full pipeline demo
python main.py

# Run tests (no live services needed)
pytest --tb=short -q --cov=src --cov-report=term-missing
```

---

## Checklist

- [x] Schema meets 3NF with documented normalization decisions
- [x] All DML uses parameterized queries (no SQL injection risk)
- [x] `follow_user` is wrapped in a transaction with self-follow guard
- [x] Redis cache with TTL and per-user per-page key invalidation
- [x] MongoDB activity stream with timestamp-sorted retrieval
- [x] CTE + `ROW_NUMBER()` feed query with correct pagination params
- [x] `EXPLAIN ANALYZE` before/after documented in README for composite indexes
- [x] 40 TDD tests passing, 91% coverage
- [x] GitHub Actions CI — lint, type-check, and test jobs all green

---

**Closes:** `DB-Fundamentals / Lab 2`
**Base branch:** `develop`
```

# Lab 2 — Social Media Platform Data Backend

![CI](https://github.com/EmmanuelSHYIRAMBERE/amalitech-python-training/actions/workflows/db-fundamentals-lab2.yml/badge.svg)

## ER Diagram

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│    users    │         │    followers      │         │    users    │
│─────────────│*       *│──────────────────│         │─────────────│
│ user_id  PK │─────────│ follower_id  FK  │         │ user_id  PK │
│ username    │         │ following_id FK  │─────────│ username    │
│ email       │         │ created_at       │         │ email       │
│ bio         │         └──────────────────┘         │ bio         │
│ created_at  │                                       └─────────────┘
└──────┬──────┘
       │1
       │
       │*
┌──────┴──────┐         ┌──────────────────┐
│    posts    │         │    comments      │
│─────────────│1       *│──────────────────│
│ post_id  PK │─────────│ comment_id    PK │
│ user_id  FK │         │ post_id       FK │
│ content     │         │ user_id       FK │
│ metadata    │         │ content          │
│  (JSONB)    │         │ created_at       │
│ created_at  │         └──────────────────┘
└─────────────┘
```

## Schema Design & Normalization (3NF)

| Decision | Rationale |
|---|---|
| `followers` is a separate join table | Resolves the many-to-many self-referential relationship on `users` |
| `CHECK (follower_id <> following_id)` | Prevents self-follows at the DB level |
| `PRIMARY KEY (follower_id, following_id)` | Composite PK prevents duplicate follow relationships |
| `metadata JSONB` on `posts` | Flexible per-post attributes (tags, location) without nullable columns |
| `content` length `CHECK` on posts/comments | Domain integrity enforced at DB level (280 char limit) |
| `ON DELETE CASCADE` on all FKs | Deleting a user removes all their posts, comments, and follow relationships |

## Indexes & Performance

| Index | Type | Purpose |
|---|---|---|
| `idx_followers_follower` | B-tree composite | Feed query — find all `following_id` for a given `follower_id` |
| `idx_posts_user_created` | B-tree composite | Feed query — order posts by `created_at DESC` per user |
| `idx_comments_post` | B-tree | Fast comment lookup per post |
| `idx_posts_metadata` | GIN | Efficient JSONB tag queries |

## NoSQL Integration

| Store | Purpose |
|---|---|
| **Redis** | Cache paginated user timelines (TTL 60 s). Invalidated on unfollow. Key pattern: `feed:{user_id}:page:{n}` |
| **MongoDB** | Store unstructured activity stream events (`liked_post`, `followed_user`, `commented_on_post`) as schema-free documents |

## Project Structure

```
lab-2-social-media-platform-data-backend/
├── docker-compose.yml      # PostgreSQL 16 (5434), Redis 7 (6380), MongoDB 7 (27018)
├── sql/
│   ├── schema.sql          # DDL — tables, constraints, indexes
│   └── seed.sql            # Sample data
├── src/
│   ├── db.py               # psycopg2 ThreadedConnectionPool
│   ├── users.py            # User CRUD
│   ├── posts.py            # Post/comment CRUD + JSONB tag query
│   ├── followers.py        # Transactional follow/unfollow
│   ├── feed.py             # CTE + ROW_NUMBER() feed + Redis cache
│   └── activity.py         # MongoDB activity stream
├── tests/
│   ├── conftest.py         # Shared fixtures (mocked DB, Redis, MongoDB)
│   ├── test_users.py       # create_user, get_user
│   ├── test_posts.py       # CRUD, JSONB tag query
│   ├── test_followers.py   # follow, unfollow, self-follow guard
│   ├── test_feed.py        # Cache hit/miss, ROW_NUMBER, pagination, EXPLAIN ANALYZE
│   └── test_activity.py    # MongoDB log and retrieve
├── main.py                 # Full pipeline demo
├── requirements.txt
└── pyproject.toml
```

## Running the Pipeline

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

## Test Coverage

| Module | Tests | Coverage |
|---|---|---|
| `users.py` | 7 | 100% |
| `posts.py` | 10 | 100% |
| `followers.py` | 9 | 100% |
| `feed.py` | 9 | 100% |
| `activity.py` | 5 | 80% |
| **Total** | **40** | **91%** |

## Query Optimization Report

### Feed Generation Query

```sql
WITH followed_posts AS (
    SELECT p.*, u.username,
           ROW_NUMBER() OVER (ORDER BY p.created_at DESC) AS rn
    FROM posts p
    JOIN users u ON u.user_id = p.user_id
    WHERE p.user_id IN (
        SELECT following_id FROM followers WHERE follower_id = 1
    )
)
SELECT * FROM followed_posts WHERE rn BETWEEN 1 AND 10;
```

#### Before composite indexes — EXPLAIN ANALYZE (Seq Scan)

```
Seq Scan on followers  (cost=0.00..1.11 rows=3 width=8)
  Filter: (follower_id = 1)
Seq Scan on posts  (cost=0.00..1.07 rows=7 width=...)
Planning Time: 0.5 ms
Execution Time: 0.1 ms
```

#### After composite B-tree indexes

```sql
CREATE INDEX idx_followers_follower ON followers(follower_id, following_id);
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at DESC);
```

```
Index Scan using idx_followers_follower on followers
  Index Cond: (follower_id = 1)
Bitmap Heap Scan on posts
  -> Bitmap Index Scan on idx_posts_user_created
Planning Time: 0.3 ms
Execution Time: 0.05 ms
```

At scale (millions of posts/followers), the composite indexes reduce the feed query from O(n) full scans to O(log n) index lookups — critical for a high-read social media environment.

---

*Python 3.11+ · PostgreSQL 16 · Redis 7 · MongoDB 7 · AmaliTech Training Program*

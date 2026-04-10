"""CLI entry point — demonstrates the full social media data backend pipeline."""

import logging

from src.activity import get_activity, log_activity
from src.feed import explain_feed_query, get_feed, invalidate_feed
from src.followers import follow_user, get_followers, get_following, unfollow_user
from src.posts import add_comment, create_post, find_posts_by_tag
from src.users import create_user, get_user

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


def main() -> None:
    # ── 1. Users ──────────────────────────────────────────────────────────────
    log.info("=== Users ===")
    uid = create_user("frank", "frank@example.com", "Backend developer")
    log.info("Created user id=%d  →  %s", uid, get_user(uid))

    # ── 2. Posts with JSONB metadata ─────────────────────────────────────────
    log.info("=== Posts ===")
    pid = create_post(uid, "Just set up psycopg2 connection pooling!", {"tags": ["python", "db"]})
    log.info("Created post id=%d", pid)

    # ── 3. Follow users (transactional) ──────────────────────────────────────
    log.info("=== Follow (ACID transaction) ===")
    follow_user(uid, 1)
    follow_user(uid, 2)
    follow_user(uid, 3)
    log.info("frank now follows: %s", get_following(uid))
    log.info("frank's followers: %s", get_followers(uid))

    # ── 4. Comment ────────────────────────────────────────────────────────────
    log.info("=== Comment ===")
    cid = add_comment(pid, 1, "Great work on the pooling!")
    log.info("Comment id=%d added", cid)

    # ── 5. MongoDB activity log ───────────────────────────────────────────────
    log.info("=== Activity Log (MongoDB) ===")
    log_activity(uid, "followed_user", {"user_id": 1})
    log_activity(uid, "followed_user", {"user_id": 2})
    log_activity(uid, "created_post", {"post_id": pid})
    log.info("Activity log: %s", get_activity(uid))

    # ── 6. Feed — first call (cache MISS) ────────────────────────────────────
    log.info("=== Feed Page 1 — first call (cache MISS) ===")
    feed = get_feed(uid, page=1)
    for p in feed:
        log.info("  [%s] @%s: %s", p["created_at"][:10], p["username"], p["content"][:60])

    # ── 7. Feed — second call (cache HIT) ────────────────────────────────────
    log.info("=== Feed Page 1 — second call (cache HIT) ===")
    get_feed(uid, page=1)

    # ── 8. JSONB tag query (GIN index) ───────────────────────────────────────
    log.info("=== JSONB Tag Query: python ===")
    for p in find_posts_by_tag("python"):
        log.info("  post=%d  %s", p["post_id"], p["content"][:60])

    # ── 9. Unfollow ───────────────────────────────────────────────────────────
    log.info("=== Unfollow ===")
    unfollow_user(uid, 3)
    invalidate_feed(uid)
    log.info("frank now follows: %s", get_following(uid))

    # ── 10. EXPLAIN ANALYZE ───────────────────────────────────────────────────
    log.info("=== EXPLAIN ANALYZE: feed query ===")
    print(explain_feed_query(uid))


if __name__ == "__main__":
    main()

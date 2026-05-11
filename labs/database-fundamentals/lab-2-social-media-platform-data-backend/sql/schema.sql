-- ============================================================
-- Social Media Platform Data Backend — DDL (3NF)
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    user_id    SERIAL       PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    email      VARCHAR(254) NOT NULL UNIQUE,
    bio        TEXT,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS posts (
    post_id    SERIAL       PRIMARY KEY,
    user_id    INT          NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content    TEXT         NOT NULL CHECK (char_length(content) <= 280),
    metadata   JSONB        NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id SERIAL       PRIMARY KEY,
    post_id    INT          NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
    user_id    INT          NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    content    TEXT         NOT NULL CHECK (char_length(content) <= 280),
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS followers (
    follower_id  INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    following_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id),
    CHECK (follower_id <> following_id)
);

-- ── Indexes ──────────────────────────────────────────────────────────────────
-- Feed query: find posts by users that user_id follows
CREATE INDEX IF NOT EXISTS idx_followers_follower
    ON followers(follower_id, following_id);

-- Feed query: order posts by created_at per user
CREATE INDEX IF NOT EXISTS idx_posts_user_created
    ON posts(user_id, created_at DESC);

-- Comment lookup per post
CREATE INDEX IF NOT EXISTS idx_comments_post
    ON comments(post_id);

-- GIN index for JSONB metadata queries on posts
CREATE INDEX IF NOT EXISTS idx_posts_metadata
    ON posts USING GIN (metadata);

-- ============================================================
-- Sample seed data
-- ============================================================

INSERT INTO users (username, email, bio) VALUES
    ('alice',   'alice@example.com',  'Software engineer & coffee lover'),
    ('bob',     'bob@example.com',    'Open source enthusiast'),
    ('carol',   'carol@example.com',  'Data scientist'),
    ('dave',    'dave@example.com',   'DevOps engineer'),
    ('eve',     'eve@example.com',    'Frontend developer')
ON CONFLICT DO NOTHING;

INSERT INTO posts (user_id, content, metadata) VALUES
    (1, 'Just deployed my first Kubernetes cluster!',   '{"tags":["devops","k8s"],"location":"Kigali"}'),
    (1, 'Python 3.12 is blazing fast.',                 '{"tags":["python","performance"]}'),
    (2, 'Open source is the future of software.',       '{"tags":["opensource"]}'),
    (2, 'Just merged my 100th PR!',                     '{"tags":["github","milestone"]}'),
    (3, 'Finished training a new NLP model today.',     '{"tags":["ml","nlp","python"]}'),
    (4, 'Terraform + GitHub Actions = pure joy.',       '{"tags":["devops","terraform","ci"]}'),
    (5, 'CSS Grid finally clicked for me.',             '{"tags":["css","frontend"]}')
ON CONFLICT DO NOTHING;

INSERT INTO comments (post_id, user_id, content) VALUES
    (1, 2, 'Congrats! Which CNI plugin did you use?'),
    (1, 3, 'Amazing work!'),
    (2, 4, 'Agreed, the JIT improvements are huge.'),
    (3, 1, 'Totally agree with this.'),
    (5, 2, 'Which architecture did you use?')
ON CONFLICT DO NOTHING;

-- follower_id follows following_id
INSERT INTO followers (follower_id, following_id) VALUES
    (1, 2), (1, 3), (1, 4),
    (2, 1), (2, 5),
    (3, 1), (3, 2),
    (4, 1), (4, 3),
    (5, 2), (5, 3)
ON CONFLICT DO NOTHING;

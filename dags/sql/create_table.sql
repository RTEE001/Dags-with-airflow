CREATE TABLE IF NOT EXISTS prs (
            id SERIAL PRIMARY KEY,
            pr_url VARCHAR NOT NULL,
            html_url VARCHAR NOT NULL);
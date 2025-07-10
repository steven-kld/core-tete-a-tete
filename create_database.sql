CREATE TABLE telegram_messages (
    -- Metadata
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    makes_sense BOOLEAN DEFAULT FALSE,
    -- Telegram data
    group_link VARCHAR(255),
    group_name VARCHAR(255),
    tg_user_id BIGINT,
    tg_user_name VARCHAR(255),
    msg TEXT
);

CREATE TABLE qualified_messages (
    -- Metadata
    id BIGINT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Telegram data
    group_link VARCHAR(255),
    group_name VARCHAR(255),
    tg_user_id BIGINT,
    tg_user_name VARCHAR(255),
    msg TEXT,
    app_url TEXT,
    -- Processing data
    generic_title VARCHAR(255),
    generic_description TEXT,
    flags TEXT[],
    CONSTRAINT fk_telegram_message
        FOREIGN KEY (id) REFERENCES telegram_messages(id)
        ON DELETE CASCADE
);

CREATE TABLE expenses (
    id INTEGER,
    kind VARCHAR(255),
    in_amount NUMERIC(10, 8) DEFAULT 0,
    out_amount NUMERIC(10, 8) DEFAULT 0,
    CONSTRAINT expenses_pkey PRIMARY KEY (id, kind),
    CONSTRAINT fk_telegram_message
        FOREIGN KEY (id) REFERENCES telegram_messages(id)
        ON DELETE CASCADE
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    group_link VARCHAR(255),
    group_name VARCHAR(255),
    generic_description TEXT,
    blacklisted BOOLEAN DEFAULT FALSE
)

CREATE TABLE accounts (
  id SERIAL PRIMARY KEY,
  date_create TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  email VARCHAR(255) NOT NULL,
  hashed_password BYTEA NOT NULL,
  salt BYTEA NOT NULL,
  display_name VARCHAR(255) NOT NULL,
  tg_user_name VARCHAR(255),
  prompt TEXT
);

CREATE TABLE accounts_groups (
    account_id INT REFERENCES accounts(id) ON DELETE CASCADE,
    group_id INT REFERENCES groups(id) ON DELETE CASCADE,
    PRIMARY KEY (account_id, group_id)
);








-- BENCHMARK REVIEW
WITH latest_messages AS (
  SELECT DISTINCT ON (tg_user_name)
    id, tg_user_name, sub_flags, tg_group_name, post_type
  FROM processed_messages
  ORDER BY tg_user_name, created_at DESC
), user_counts AS (
  SELECT
    tg_group_name,
    COUNT(DISTINCT CASE WHEN 'suspicious' = ANY(sub_flags) THEN tg_user_name END) AS suspicious_users,
    COUNT(DISTINCT CASE WHEN post_type = 1 THEN tg_user_name END) AS valid_jobs,
    COUNT(DISTINCT CASE WHEN post_type = 2 THEN tg_user_name END) AS valid_resumes
  FROM latest_messages
  GROUP BY tg_group_name
), msg_stats AS (
  SELECT
    tm.group_name,
    COUNT(*) AS total_msgs,
    COUNT(DISTINCT CASE WHEN c.detect_cost > 0 THEN tm.id END) AS detect_stage,
    COUNT(DISTINCT CASE WHEN c.cluster_cost > 0 THEN tm.id END) AS cluster_stage,
    COUNT(DISTINCT CASE WHEN c.info_cost > 0 THEN tm.id END) AS jobinfo_stage,
    COUNT(DISTINCT CASE WHEN c.subflag_cost > 0 THEN tm.id END) AS subflags_stage,
    COUNT(DISTINCT CASE WHEN 'suspicious' = ANY(pm.sub_flags) THEN tm.id END) AS suspicious_msgs,
    COUNT(DISTINCT CASE WHEN pm.post_type = 1 THEN tm.id END) AS jobs,
    COUNT(DISTINCT CASE WHEN pm.post_type = 2 THEN tm.id END) AS resumes
  FROM telegram_messages tm
  LEFT JOIN costs c ON tm.id = c.id
  LEFT JOIN processed_messages pm ON tm.id = pm.id
  GROUP BY tm.group_name
  HAVING COUNT(*) > 100
)
SELECT 
  COALESCE(m.group_name, u.tg_group_name) AS group_name,
  m.total_msgs,
  ROUND(100.0 * m.detect_stage / NULLIF(m.total_msgs, 0), 2) AS pct_detect_stage,
  ROUND(100.0 * m.cluster_stage / NULLIF(m.total_msgs, 0), 2) AS pct_cluster_stage,
  ROUND(100.0 * m.jobinfo_stage / NULLIF(m.total_msgs, 0), 2) AS pct_jobinfo_stage,
  ROUND(100.0 * m.subflags_stage / NULLIF(m.total_msgs, 0), 2) AS pct_subflags_stage,
  ROUND(100.0 * m.suspicious_msgs / NULLIF(m.total_msgs, 0), 2) AS pct_suspicious_msgs,
  ROUND(100.0 * m.jobs / NULLIF(m.total_msgs, 0), 2) AS pct_jobs,
  ROUND(100.0 * m.resumes / NULLIF(m.total_msgs, 0), 2) AS pct_resumes,
  ROUND(100.0 * u.suspicious_users / NULLIF(m.total_msgs, 0), 2) AS pct_suspicious_users,
  ROUND(100.0 * u.valid_jobs / NULLIF(m.total_msgs, 0), 2) AS pct_valid_jobs,
  ROUND(100.0 * u.valid_resumes / NULLIF(m.total_msgs, 0), 2) AS pct_valid_resumes
FROM msg_stats m
LEFT JOIN user_counts u ON m.group_name = u.tg_group_name
ORDER BY m.total_msgs DESC;

-- VALID E-COMMERCE
SELECT DISTINCT ON (tg_user_name) id, msg, tg_user_name, sub_flags, created_at 
FROM processed_messages
WHERE post_type = 1
  and (
	'Wildberries' = ANY(sub_flags)
	or 'Дизайн' = any(flags)
	or 'E-commerce' = any(flags)
    or 'Инфографика' = ANY(sub_flags)
	OR 'Ozon' = ANY(sub_flags)
)
  and not (
  	'suspicious' = ANY(sub_flags)
  )
ORDER BY tg_user_name, created_at DESC;


select * from telegram_messages
where group_name in(
'Охрана труда| Чат специалистов и экспертов',
'Техэксперт: Охрана труда и безопасность',
'Охрана труда ПОНЯТНЫМ ЯЗЫКОМ',
'Чат | Электрики 🔌💡'
)

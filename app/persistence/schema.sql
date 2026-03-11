-- ============================================================
-- Q4-Rescue Database Schema
-- ============================================================

-- ------------------------------------------------------------
-- Cases
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cases (
  id TEXT PRIMARY KEY,
  member_id TEXT NOT NULL,
  measure_type TEXT NOT NULL,
  year INTEGER NOT NULL,
  current_pdc REAL NOT NULL,
  target_pdc REAL NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

-- Optional but recommended index for fast lookups
CREATE INDEX IF NOT EXISTS idx_cases_member_measure_year
ON cases (member_id, measure_type, year);

-- ------------------------------------------------------------
-- Idempotency Keys
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS idempotency_keys (
  route TEXT NOT NULL,
  key TEXT NOT NULL,
  response TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (route, key)
);

CREATE INDEX IF NOT EXISTS idx_idempotency_keys_route
ON idempotency_keys (route);

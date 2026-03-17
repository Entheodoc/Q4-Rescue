-- ============================================================
-- Q4-Rescue Database Schema
-- ============================================================

-- ------------------------------------------------------------
-- Members
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS members (
  id TEXT PRIMARY KEY,
  health_plan_member_id TEXT NOT NULL UNIQUE,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  birth_date TEXT,
  sex TEXT,
  phone_number TEXT,
  preferred_contact_method TEXT,
  preferred_language TEXT,
  supported_languages TEXT NOT NULL DEFAULT '[]',
  address_line_1 TEXT,
  address_line_2 TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  pbp TEXT,
  low_income_subsidy_level TEXT,
  active_status TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_members_health_plan_member_id
ON members (health_plan_member_id);

-- ------------------------------------------------------------
-- Referrals
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS referrals (
  id TEXT PRIMARY KEY,
  member_id TEXT NOT NULL,
  case_id TEXT UNIQUE,
  received_at TEXT NOT NULL,
  referral_source TEXT NOT NULL,
  source_record_id TEXT,
  referral_reason TEXT,
  referral_notes TEXT,
  snapshot_health_plan_member_id TEXT NOT NULL,
  snapshot_first_name TEXT NOT NULL,
  snapshot_last_name TEXT NOT NULL,
  snapshot_birth_date TEXT,
  snapshot_phone_number TEXT,
  snapshot_preferred_language TEXT,
  snapshot_supported_languages TEXT NOT NULL DEFAULT '[]',
  snapshot_address_line_1 TEXT,
  snapshot_address_line_2 TEXT,
  snapshot_city TEXT,
  snapshot_state TEXT,
  snapshot_zip TEXT,
  snapshot_pbp TEXT,
  snapshot_low_income_subsidy_level TEXT,
  snapshot_active_status TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE INDEX IF NOT EXISTS idx_referrals_member_id
ON referrals (member_id);

-- ------------------------------------------------------------
-- Cases
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cases (
  id TEXT PRIMARY KEY,
  member_id TEXT NOT NULL,
  referral_id TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL,
  opened_at TEXT NOT NULL,
  closed_at TEXT,
  archived_at TEXT,
  closed_reason TEXT,
  case_summary TEXT,
  priority TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (member_id) REFERENCES members(id),
  FOREIGN KEY (referral_id) REFERENCES referrals(id)
);

CREATE INDEX IF NOT EXISTS idx_cases_member_id
ON cases (member_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cases_member_active
ON cases (member_id)
WHERE status IN ('open', 'in_progress', 'on_hold');

-- ------------------------------------------------------------
-- Measures
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS measures (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  measure_code TEXT NOT NULL,
  measure_name TEXT NOT NULL,
  performance_year INTEGER NOT NULL,
  pdc REAL,
  status TEXT NOT NULL,
  actionable_status TEXT,
  identified_at TEXT NOT NULL,
  opened_at TEXT,
  closed_at TEXT,
  closure_reason TEXT,
  critical_by_date TEXT,
  target_threshold REAL,
  source_system TEXT,
  source_measure_id TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (case_id) REFERENCES cases(id)
);

CREATE INDEX IF NOT EXISTS idx_measures_case_id
ON measures (case_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_measures_case_code_year_active
ON measures (case_id, measure_code, performance_year)
WHERE status IN ('open', 'in_progress', 'on_hold');

-- ------------------------------------------------------------
-- Medications
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS medications (
  id TEXT PRIMARY KEY,
  measure_id TEXT NOT NULL,
  medication_name TEXT NOT NULL,
  display_name TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (measure_id) REFERENCES measures(id)
);

CREATE INDEX IF NOT EXISTS idx_medications_measure_id
ON medications (measure_id);

-- ------------------------------------------------------------
-- Providers
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS providers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  phone_numbers TEXT NOT NULL DEFAULT '[]',
  preferred_phone_number TEXT,
  fax_number TEXT,
  address_line_1 TEXT,
  address_line_2 TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_providers_name
ON providers (name);

-- ------------------------------------------------------------
-- Pharmacies
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS pharmacies (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  phone_numbers TEXT NOT NULL DEFAULT '[]',
  preferred_phone_number TEXT,
  fax_number TEXT,
  address_line_1 TEXT,
  address_line_2 TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pharmacies_name
ON pharmacies (name);

-- ------------------------------------------------------------
-- Medication Providers
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS medication_providers (
  id TEXT PRIMARY KEY,
  medication_id TEXT NOT NULL,
  provider_id TEXT NOT NULL,
  prescribing_role TEXT,
  is_current_prescriber INTEGER NOT NULL DEFAULT 0,
  last_prescribed_at TEXT,
  refill_request_status TEXT,
  provider_notes TEXT,
  contact_for_refills INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (medication_id) REFERENCES medications(id),
  FOREIGN KEY (provider_id) REFERENCES providers(id)
);

CREATE INDEX IF NOT EXISTS idx_medication_providers_medication_id
ON medication_providers (medication_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_medication_providers_current
ON medication_providers (medication_id)
WHERE is_current_prescriber = 1;

CREATE UNIQUE INDEX IF NOT EXISTS idx_medication_providers_refill_contact
ON medication_providers (medication_id)
WHERE contact_for_refills = 1;

-- ------------------------------------------------------------
-- Medication Pharmacies
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS medication_pharmacies (
  id TEXT PRIMARY KEY,
  medication_id TEXT NOT NULL,
  pharmacy_id TEXT NOT NULL,
  pharmacy_status TEXT,
  last_fill_date TEXT,
  next_fill_date TEXT,
  pickup_date TEXT,
  last_fill_days_supply INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (medication_id) REFERENCES medications(id),
  FOREIGN KEY (pharmacy_id) REFERENCES pharmacies(id)
);

CREATE INDEX IF NOT EXISTS idx_medication_pharmacies_medication_id
ON medication_pharmacies (medication_id);

CREATE TABLE IF NOT EXISTS medication_pharmacy_refills (
  id TEXT PRIMARY KEY,
  medication_pharmacy_id TEXT NOT NULL,
  days_supply INTEGER NOT NULL,
  expiration_date TEXT,
  status TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (medication_pharmacy_id) REFERENCES medication_pharmacies(id)
);

CREATE INDEX IF NOT EXISTS idx_medication_pharmacy_refills_relationship_id
ON medication_pharmacy_refills (medication_pharmacy_id);

-- ------------------------------------------------------------
-- Barriers
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS barriers (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  barrier_type TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  severity TEXT,
  description TEXT,
  identified_at TEXT NOT NULL,
  resolved_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (case_id) REFERENCES cases(id)
);

CREATE INDEX IF NOT EXISTS idx_barriers_case_id
ON barriers (case_id);

-- ------------------------------------------------------------
-- Tasks
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  case_id TEXT NOT NULL,
  task_type TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  priority TEXT,
  related_measure_ids TEXT NOT NULL DEFAULT '[]',
  related_medication_ids TEXT NOT NULL DEFAULT '[]',
  barrier_id TEXT,
  description TEXT,
  due_at TEXT,
  completed_at TEXT,
  cancelled_at TEXT,
  outcome TEXT,
  assigned_to TEXT,
  assigned_queue TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (case_id) REFERENCES cases(id),
  FOREIGN KEY (barrier_id) REFERENCES barriers(id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_case_id
ON tasks (case_id);

-- ------------------------------------------------------------
-- Contact Attempts
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS contact_attempts (
  id TEXT PRIMARY KEY,
  contact_party_type TEXT NOT NULL,
  contact_party_id TEXT NOT NULL,
  contact_method TEXT NOT NULL,
  attempted_at TEXT NOT NULL,
  outcome TEXT,
  outcome_notes TEXT,
  initiated_by TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_contact_attempts_party
ON contact_attempts (contact_party_type, contact_party_id);

-- ------------------------------------------------------------
-- Task Contact Attempts
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS task_contact_attempts (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  contact_attempt_id TEXT NOT NULL,
  effect_on_task TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (task_id) REFERENCES tasks(id),
  FOREIGN KEY (contact_attempt_id) REFERENCES contact_attempts(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_task_contact_attempts_pair
ON task_contact_attempts (task_id, contact_attempt_id);

-- ------------------------------------------------------------
-- Audit Events
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY,
  action TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT,
  actor_subject TEXT NOT NULL,
  actor_permissions TEXT NOT NULL DEFAULT '[]',
  request_id TEXT NOT NULL,
  metadata TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_events_resource
ON audit_events (resource_type, resource_id);

CREATE INDEX IF NOT EXISTS idx_audit_events_created_at
ON audit_events (created_at);

-- ------------------------------------------------------------
-- Idempotency Keys
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS idempotency_keys (
  route TEXT NOT NULL,
  key TEXT NOT NULL,
  response TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (route, key)
);

CREATE INDEX IF NOT EXISTS idx_idempotency_keys_route
ON idempotency_keys (route);

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS disaster_types (
    disaster_type_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

INSERT OR IGNORE INTO disaster_types (name, description) VALUES
    ('Flood', 'Flooding and water-related emergencies'),
    ('Cyclone', 'Cyclone, severe storm, and high-wind emergencies'),
    ('Earthquake', 'Earthquake and related structural emergencies'),
    ('Fire', 'Building, wildland, and other fire emergencies'),
    ('Landslide', 'Landslide and slope-failure emergencies'),
    ('Tsunami', 'Tsunami and coastal-wave emergencies'),
    ('Other', 'A disaster type not listed above');

CREATE TABLE IF NOT EXISTS emergency_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    disaster_type_id INTEGER NOT NULL REFERENCES disaster_types(disaster_type_id),
    reporter_name TEXT,
    reporter_phone TEXT,
    location_text TEXT NOT NULL CHECK (length(trim(location_text)) > 0),
    latitude REAL,
    longitude REAL,
    description TEXT NOT NULL CHECK (length(trim(description)) > 0),
    affected_people INTEGER NOT NULL DEFAULT 0 CHECK (affected_people >= 0),
    people_trapped INTEGER NOT NULL DEFAULT 0 CHECK (people_trapped IN (0, 1)),
    severity_score INTEGER CHECK (severity_score IS NULL OR severity_score BETWEEN 0 AND 100),
    severity TEXT CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    priority_score INTEGER CHECK (priority_score IS NULL OR priority_score BETWEEN 0 AND 100),
    priority_level TEXT CHECK (priority_level IN ('Low', 'Medium', 'High', 'Urgent')),
    classification_method TEXT NOT NULL DEFAULT 'pending'
        CHECK (classification_method IN ('pending', 'rule_based', 'ml_model', 'manual')),
    classification_notes TEXT,
    status TEXT NOT NULL DEFAULT 'new'
        CHECK (status IN ('new', 'triaged', 'assigned', 'in_progress', 'resolved', 'duplicate', 'false_alarm', 'closed')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    verified_at TEXT,
    closed_at TEXT,
    CHECK (
        (latitude IS NULL AND longitude IS NULL) OR
        (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)
    )
);

CREATE INDEX IF NOT EXISTS idx_reports_status_priority
    ON emergency_reports(status, priority_score DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_reports_disaster_type
    ON emergency_reports(disaster_type_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_location
    ON emergency_reports(latitude, longitude);

CREATE TABLE IF NOT EXISTS shelters (
    shelter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    address TEXT NOT NULL,
    latitude REAL NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude REAL NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    capacity INTEGER CHECK (capacity IS NULL OR capacity >= 0),
    current_occupancy INTEGER CHECK (current_occupancy IS NULL OR current_occupancy >= 0),
    status TEXT NOT NULL DEFAULT 'unknown'
        CHECK (status IN ('open', 'limited', 'full', 'closed', 'unknown')),
    contact_name TEXT,
    contact_phone TEXT,
    source_url TEXT,
    is_verified INTEGER NOT NULL DEFAULT 0 CHECK (is_verified IN (0, 1)),
    verified_at TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_shelters_status_verified
    ON shelters(status, is_verified);
CREATE INDEX IF NOT EXISTS idx_shelters_location
    ON shelters(latitude, longitude);

CREATE TABLE IF NOT EXISTS rescue_teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    organization TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS report_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL REFERENCES emergency_reports(report_id),
    team_id INTEGER NOT NULL REFERENCES rescue_teams(team_id),
    assigned_by TEXT,
    status TEXT NOT NULL DEFAULT 'assigned'
        CHECK (status IN ('assigned', 'accepted', 'en_route', 'on_scene', 'completed', 'cancelled')),
    assigned_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_assignments_report
    ON report_assignments(report_id, status);
CREATE INDEX IF NOT EXISTS idx_assignments_team
    ON report_assignments(team_id, status);

CREATE TABLE IF NOT EXISTS report_updates (
    update_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL REFERENCES emergency_reports(report_id),
    update_type TEXT NOT NULL DEFAULT 'note'
        CHECK (update_type IN ('status_change', 'note', 'severity_review', 'assignment_note')),
    previous_status TEXT
        CHECK (previous_status IS NULL OR previous_status IN ('new', 'triaged', 'assigned', 'in_progress', 'resolved', 'duplicate', 'false_alarm', 'closed')),
    new_status TEXT
        CHECK (new_status IS NULL OR new_status IN ('new', 'triaged', 'assigned', 'in_progress', 'resolved', 'duplicate', 'false_alarm', 'closed')),
    message TEXT NOT NULL CHECK (length(trim(message)) > 0),
    updated_by TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    CHECK (
        (update_type = 'status_change' AND new_status IS NOT NULL) OR
        (update_type <> 'status_change')
    )
);

CREATE INDEX IF NOT EXISTS idx_report_updates_timeline
    ON report_updates(report_id, created_at DESC);
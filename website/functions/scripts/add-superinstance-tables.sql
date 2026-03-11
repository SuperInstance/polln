-- SuperInstance Cells and Origins Database Schema
-- Run with: npx wrangler d1 execute superinstance-db --file=scripts/add-superinstance-tables.sql

-- Origins table (OCDS Origins)
CREATE TABLE IF NOT EXISTS origins (
  id TEXT PRIMARY KEY,
  parent_id TEXT,
  name TEXT NOT NULL,
  transformation_matrix TEXT NOT NULL, -- JSON array of transformation matrix values
  uncertainty REAL NOT NULL DEFAULT 0.0,
  owner_user_id TEXT,
  is_public BOOLEAN DEFAULT FALSE,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (parent_id) REFERENCES origins(id) ON DELETE CASCADE,
  FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- SuperInstance Cells table (OCDS Cells)
CREATE TABLE IF NOT EXISTS cells (
  id TEXT PRIMARY KEY,
  origin_id TEXT NOT NULL,
  name TEXT NOT NULL,
  cell_type TEXT NOT NULL, -- 'formula', 'value', 'rate', 'confidence', etc.
  local_state TEXT NOT NULL, -- JSON representation of state vector
  rate_of_change TEXT, -- JSON representation of rate vector
  uncertainty_matrix TEXT, -- JSON representation of uncertainty matrix
  dependencies TEXT, -- JSON array of dependent cell IDs
  influence_radius REAL DEFAULT 1.0,
  deadband_threshold REAL DEFAULT 0.01,
  owner_user_id TEXT,
  is_public BOOLEAN DEFAULT FALSE,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (origin_id) REFERENCES origins(id) ON DELETE CASCADE,
  FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Cell dependencies junction table
CREATE TABLE IF NOT EXISTS cell_dependencies (
  id TEXT PRIMARY KEY,
  source_cell_id TEXT NOT NULL,
  target_cell_id TEXT NOT NULL,
  relative_transform TEXT, -- JSON transformation matrix
  coupling_strength REAL DEFAULT 1.0, -- 0.0 to 1.0
  propagation_delay INTEGER DEFAULT 0, -- milliseconds
  confidence_weight REAL DEFAULT 1.0, -- weight for confidence calculations
  created_at INTEGER NOT NULL,
  FOREIGN KEY (source_cell_id) REFERENCES cells(id) ON DELETE CASCADE,
  FOREIGN KEY (target_cell_id) REFERENCES cells(id) ON DELETE CASCADE,
  UNIQUE(source_cell_id, target_cell_id)
);

-- Cell evolution history (append-only log)
CREATE TABLE IF NOT EXISTS cell_history (
  id TEXT PRIMARY KEY,
  cell_id TEXT NOT NULL,
  origin_timestamp INTEGER NOT NULL, -- local timestamp in origin frame
  global_timestamp INTEGER NOT NULL, -- UTC timestamp
  state_hash TEXT NOT NULL,
  rate_hash TEXT,
  confidence REAL,
  parent_hash TEXT,
  event_type TEXT NOT NULL DEFAULT 'update', -- 'create', 'update', 'delete', 'cascade'
  event_data TEXT, -- JSON metadata about the event
  propagated BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (cell_id) REFERENCES cells(id) ON DELETE CASCADE
);

-- Confidence cascade tracking
CREATE TABLE IF NOT EXISTS confidence_cascade (
  id TEXT PRIMARY KEY,
  source_cell_id TEXT NOT NULL,
  target_cell_id TEXT NOT NULL,
  cascade_level INTEGER NOT NULL, -- 1: local, 2: neighborhood, 3: global
  confidence_transferred REAL NOT NULL,
  distance REAL NOT NULL,
  propagated_at INTEGER NOT NULL,
  FOREIGN KEY (source_cell_id) REFERENCES cells(id) ON DELETE CASCADE,
  FOREIGN KEY (target_cell_id) REFERENCES cells(id) ON DELETE CASCADE
);

-- Federation state (for distributed SuperInstances)
CREATE TABLE IF NOT EXISTS federations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  owner_user_id TEXT,
  reference_origin_id TEXT NOT NULL,
  participants TEXT, -- JSON array of origin IDs
  consensus_rules TEXT, -- JSON object with consensus parameters
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (owner_user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (reference_origin_id) REFERENCES origins(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_origins_parent_id ON origins(parent_id);
CREATE INDEX IF NOT EXISTS idx_origins_owner_user_id ON origins(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_cells_origin_id ON cells(origin_id);
CREATE INDEX IF NOT EXISTS idx_cells_owner_user_id ON cells(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_cells_cell_type ON cells(cell_type);
CREATE INDEX IF NOT EXISTS idx_cell_dependencies_source ON cell_dependencies(source_cell_id);
CREATE INDEX IF NOT EXISTS idx_cell_dependencies_target ON cell_dependencies(target_cell_id);
CREATE INDEX IF NOT EXISTS idx_cell_history_cell_id ON cell_history(cell_id);
CREATE INDEX IF NOT EXISTS idx_cell_history_timestamps ON cell_history(cell_id, global_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_confidence_cascade_source ON confidence_cascade(source_cell_id);
CREATE INDEX IF NOT EXISTS idx_confidence_cascade_level ON confidence_cascade(cascade_level);

-- Views for common queries
CREATE VIEW IF NOT EXISTS cell_dependencies_view AS
SELECT
  cd.id,
  source.name as source_name,
  target.name as target_name,
  cd.coupling_strength,
  cd.confidence_weight,
  cd.propagation_delay
FROM cell_dependencies cd
JOIN cells source ON cd.source_cell_id = source.id
JOIN cells target ON cd.target_cell_id = target.id;

CREATE VIEW IF NOT EXISTS origin_hierarchy_view AS
WITH RECURSIVE origin_tree AS (
  SELECT id, name, parent_id, 0 as level, transformation_matrix, uncertainty
  FROM origins
  WHERE parent_id IS NULL
  UNION ALL
  SELECT o.id, o.name, o.parent_id, ot.level + 1, o.transformation_matrix, o.uncertainty
  FROM origins o
  JOIN origin_tree ot ON o.parent_id = ot.id
)
SELECT * FROM origin_tree;

PRAGMA foreign_keys = ON;
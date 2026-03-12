-- Community Platform Tables for SuperInstance.AI
-- These tables support the community features: formulas, discussions, user profiles

-- Extended user profiles table (extends existing users table)
CREATE TABLE IF NOT EXISTS user_profiles (
  user_id TEXT PRIMARY KEY,
  display_name TEXT,
  bio TEXT,
  avatar_url TEXT,
  location TEXT,
  website TEXT,
  reputation INTEGER DEFAULT 0,
  achievement_badges TEXT DEFAULT '[]', -- JSON array of badge IDs
  contribution_count INTEGER DEFAULT 0,
  last_active INTEGER,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Formulas table for user-shared SuperInstance formulas
CREATE TABLE IF NOT EXISTS formulas (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  formula_type TEXT NOT NULL, -- 'confidence-cascade', 'smp', 'tile', etc.
  formula_code TEXT NOT NULL, -- JSON representation of the formula
  parameters TEXT, -- JSON schema for formula parameters
  tags TEXT DEFAULT '[]', -- JSON array of tag strings
  visibility TEXT DEFAULT 'public', -- 'public', 'unlisted', 'private'
  rating REAL DEFAULT 0,
  rating_count INTEGER DEFAULT 0,
  usage_count INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Formula reviews/ratings
CREATE TABLE IF NOT EXISTS formula_reviews (
  id TEXT PRIMARY KEY,
  formula_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  review_text TEXT,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (formula_id) REFERENCES formulas(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(formula_id, user_id)
);

-- Community discussions/forum
CREATE TABLE IF NOT EXISTS discussions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT NOT NULL, -- 'general', 'help', 'showcase', 'tutorial-feedback'
  tags TEXT DEFAULT '[]', -- JSON array of tag strings
  pinned BOOLEAN DEFAULT FALSE,
  locked BOOLEAN DEFAULT FALSE,
  reply_count INTEGER DEFAULT 0,
  view_count INTEGER DEFAULT 0,
  last_reply_at INTEGER,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Discussion replies
CREATE TABLE IF NOT EXISTS discussion_replies (
  id TEXT PRIMARY KEY,
  discussion_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  content TEXT NOT NULL,
  parent_reply_id TEXT, -- For nested replies
  created_at INTEGER NOT NULL,
  updated_at INTEGER,
  FOREIGN KEY (discussion_id) REFERENCES discussions(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (parent_reply_id) REFERENCES discussion_replies(id) ON DELETE CASCADE
);

-- Shared workspaces for collaboration
CREATE TABLE IF NOT EXISTS workspaces (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  configuration TEXT, -- JSON config for the workspace
  visibility TEXT DEFAULT 'private', -- 'private', 'shared', 'public'
  member_count INTEGER DEFAULT 1,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Workspace members
CREATE TABLE IF NOT EXISTS workspace_members (
  workspace_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT DEFAULT 'member', -- 'owner', 'admin', 'member', 'viewer'
  joined_at INTEGER NOT NULL,
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  PRIMARY KEY (workspace_id, user_id)
);

-- Activity feed for tracking user actions
CREATE TABLE IF NOT EXISTS activities (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  action_type TEXT NOT NULL, -- 'formula_created', 'discussion_posted', 'workspace_shared', etc.
  entity_type TEXT NOT NULL, -- 'formula', 'discussion', 'workspace', etc.
  entity_id TEXT NOT NULL,
  metadata TEXT, -- JSON metadata about the action
  created_at INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Achievement badges
CREATE TABLE IF NOT EXISTS badges (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  icon TEXT, -- Icon identifier/class
  requirements TEXT NOT NULL, -- JSON schema for earning requirements
  points INTEGER DEFAULT 0,
  rarity TEXT DEFAULT 'common', -- 'common', 'rare', 'epic', 'legendary'
  created_at INTEGER NOT NULL
);

-- User earned badges
CREATE TABLE IF NOT EXISTS user_badges (
  user_id TEXT NOT NULL,
  badge_id TEXT NOT NULL,
  earned_at INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, badge_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_reputation ON user_profiles(reputation DESC);
CREATE INDEX IF NOT EXISTS idx_user_profiles_last_active ON user_profiles(last_active DESC);
CREATE INDEX IF NOT EXISTS idx_formulas_type ON formulas(formula_type);
CREATE INDEX IF NOT EXISTS idx_formulas_visibility ON formulas(visibility);
CREATE INDEX IF NOT EXISTS idx_formulas_created_at ON formulas(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_formulas_rating ON formulas(rating DESC);
CREATE INDEX IF NOT EXISTS idx_formula_reviews_formula_id ON formula_reviews(formula_id);
CREATE INDEX IF NOT EXISTS idx_discussions_category ON discussions(category);
CREATE INDEX IF NOT EXISTS idx_discussions_created_at ON discussions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_discussions_pinned ON discussions(pinned DESC, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_discussion_replies_discussion_id ON discussion_replies(discussion_id);
CREATE INDEX IF NOT EXISTS idx_discussion_replies_created_at ON discussion_replies(created_at);
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at DESC);

-- Default badges
INSERT OR IGNORE INTO badges (id, name, description, icon, requirements, points, rarity, created_at) VALUES
  ('first-formula', 'Formula Creator', 'Create your first formula', 'badge-formula', '{"type": "formula_created", "count": 1}', 10, 'common', strftime('%s', 'now')),
  ('formula-collector-10', 'Formula Collector', 'Share 10 formulas', 'badge-collector', '{"type": "formula_created", "count": 10}', 50, 'rare', strftime('%s', 'now')),
  ('helpful-user', 'Helpful User', 'Receive 10 thumbs up on your replies', 'badge-helpful', '{"type": "reply_upvoted", "count": 10}', 25, 'common', strftime('%s', 'now')),
  ('discussion-starter', 'Discussion Starter', 'Start 5 discussions', 'badge-discussion', '{"type": "discussion_created", "count": 5}', 20, 'common', strftime('%s', 'now')),
  ('community-builder', 'Community Builder', 'Join or create 3 workspaces', 'badge-builder', '{"type": "workspace_member", "count": 3}', 30, 'rare', strftime('%s', 'now'));

PRAGMA foreign_keys = ON;
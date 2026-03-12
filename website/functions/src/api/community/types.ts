// Community API Types

export interface Formula {
  id: string;
  userId: string;
  title: string;
  description?: string;
  formulaType: string;
  formulaCode: string;
  parameters?: FormulaParameter[];
  tags?: string[];
  visibility: 'public' | 'unlisted' | 'private';
  rating?: number;
  ratingCount?: number;
  usageCount?: number;
  createdAt: string;
  updatedAt: string;
  author?: UserProfile;
  userReview?: FormulaReview;
}

export interface FormulaParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  description?: string;
  default?: any;
  required?: boolean;
}

export interface FormulaReview {
  id: string;
  formulaId: string;
  userId: string;
  rating: number;
  reviewText?: string;
  createdAt: string;
  user?: {
    displayName: string;
    avatarUrl?: string;
  };
}

export interface Discussion {
  id: string;
  userId: string;
  title: string;
  content: string;
  category: 'general' | 'help' | 'showcase' | 'tutorial-feedback';
  tags?: string[];
  pinned?: boolean;
  locked?: boolean;
  replyCount?: number;
  viewCount?: number;
  lastReplyAt?: string;
  createdAt: string;
  updatedAt: string;
  author?: UserProfile;
  lastReplyAuthor?: UserProfile;
}

export interface DiscussionReply {
  id: string;
  discussionId: string;
  userId: string;
  content: string;
  parentReplyId?: string;
  createdAt: string;
  updatedAt?: string;
  nestedReplies?: DiscussionReply[];
  author?: UserProfile;
}

export interface UserProfile {
  userId: string;
  displayName?: string;
  bio?: string;
  avatarUrl?: string;
  location?: string;
  website?: string;
  reputation?: number;
  achievementBadges?: Badge[];
  contributionCount?: number;
  lastActive?: string;
  createdAt?: string;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon?: string;
  points?: number;
  rarity?: 'common' | 'rare' | 'epic' | 'legendary';
}

export interface Workspace {
  id: string;
  ownerId: string;
  name: string;
  description?: string;
  configuration?: WorkspaceConfig;
  visibility?: 'private' | 'shared' | 'public';
  memberCount?: number;
  createdAt: string;
  updatedAt: string;
  owner?: UserProfile;
}

export interface WorkspaceConfig {
  defaultCellType?: string;
  allowedCellTypes?: string[];
  sharingEnabled?: boolean;
  commentingEnabled?: boolean;
  versionHistory?: boolean;
}

export interface WorkspaceMember {
  workspaceId: string;
  userId: string;
  role?: 'owner' | 'admin' | 'member' | 'viewer';
  joinedAt: string;
  user?: UserProfile;
}

export interface Activity {
  id: string;
  userId: string;
  actionType: string;
  entityType: string;
  entityId: string;
  metadata?: Record<string, any>;
  createdAt: string;
  user?: UserProfile;
}

// Request/Response types
export interface CreateFormulaRequest {
  title: string;
  description?: string;
  formulaType: string;
  formulaCode: string;
  parameters?: FormulaParameter[];
  tags?: string[];
  visibility: 'public' | 'unlisted' | 'private';
}

export interface UpdateFormulaRequest extends Partial<CreateFormulaRequest> {
  id: string;
}

export interface CreateDiscussionRequest {
  title: string;
  content: string;
  category: 'general' | 'help' | 'showcase' | 'tutorial-feedback';
  tags?: string[];
}

export interface CreateReplyRequest {
  content: string;
  parentReplyId?: string;
}

export interface UpdateProfileRequest {
  displayName?: string;
  bio?: string;
  avatarUrl?: string;
  location?: string;
  website?: string;
}

export interface CreateWorkspaceRequest {
  name: string;
  description?: string;
  visibility?: 'private' | 'shared' | 'public';
  configuration?: WorkspaceConfig;
}

// Search and filter types
export interface FormulaSearchParams {
  query?: string;
  formulaType?: string;
  tags?: string[];
  author?: string;
  sortBy?: 'relevance' | 'rating' | 'usage' | 'recent';
  page?: number;
  limit?: number;
}

export interface DiscussionSearchParams {
  query?: string;
  category?: string;
  tags?: string[];
  author?: string;
  sortBy?: 'recent' | 'replies' | 'views' | 'last_reply';
  page?: number;
  limit?: number;
}

export interface UserSearchParams {
  query?: string;
  sortBy?: 'reputation' | 'contributions' | 'recent';
  page?: number;
  limit?: number;
}
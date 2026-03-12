import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { getDB, requireAuth } from '../../shared/auth';
import { validate } from '../../shared/validation';
import type { Context } from 'hono';
import type { Formula, Discussion, DiscussionReply, Workspace, Activity, UserProfile, Badge } from './types';
import { createUUID, now } from '../../shared/utils';

const community = new Hono();

// Apply CORS middleware
community.use('/*', cors({
  origin: ['https://superinstance.ai', 'http://localhost:4321'],
  credentials: true,
}));

// Formula sharing endpoints
community.get('/formulas', async (c: Context) => {
  const db = getDB(c);
  const { type, query, limit = '20', page = '1' } = c.req.query();

  let statement = `
    SELECT f.*,
           u.username as author_username,
           up.display_name as author_display_name,
           up.avatar_url as author_avatar_url
    FROM formulas f
    JOIN users u ON f.user_id = u.id
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE f.visibility = 'public'
  `;

  const params: any[] = [];

  if (type) {
    statement += ' AND f.formula_type = ?';
    params.push(type);
  }

  if (query) {
    statement += ' AND (f.title LIKE ? OR f.description LIKE ? OR f.tags LIKE ?)';
    const searchTerm = `%${query}%`;
    params.push(searchTerm, searchTerm, searchTerm);
  }

  statement += ' ORDER BY f.created_at DESC LIMIT ? OFFSET ?';
  const limitNum = Math.min(parseInt(limit), 100);
  const offset = (parseInt(page) - 1) * limitNum;
  params.push(limitNum, offset);

  const formulas = await db.prepare(statement).bind(...params).all();
  return c.json(formulas.results);
});

community.get('/formulas/:id', async (c: Context) => {
  const db = getDB(c);
  const id = c.req.param('id');

  // Increment view count
  await db.prepare('UPDATE formulas SET usage_count = usage_count + 1 WHERE id = ?').bind(id).run();

  // Get formula with author info
  const formula = await db.prepare(`
    SELECT f.*,
           u.username as author_username,
           up.display_name as author_display_name,
           up.avatar_url as author_avatar_url,
           up.reputation as author_reputation
    FROM formulas f
    JOIN users u ON f.user_id = u.id
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE f.id = ? AND f.visibility = 'public'
  `).bind(id).first();

  if (!formula) {
    return c.json({ error: 'Formula not found' }, 404);
  }

  // Get reviews
  const reviews = await db.prepare(`
    SELECT fr.*,
           u.username,
           up.display_name as user_display_name,
           up.avatar_url as user_avatar_url
    FROM formula_reviews fr
    JOIN users u ON fr.user_id = u.id
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE fr.formula_id = ?
    ORDER BY fr.created_at DESC
  `).bind(id).all();

  return c.json({
    ...formula,
    reviews: reviews.results
  });
});

community.post('/formulas', requireAuth, async (c: Context) => {
  const db = getDB(c);
  const user = c.get('user');
  const body = await c.req.json();

  const validation = validate(body, {
    title: { type: 'string', required: true, min: 3, max: 200 },
    description: { type: 'string', max: 1000 },
    formulaType: { type: 'string', required: true },
    formulaCode: { type: 'string', required: true, max: 10000 },
    parameters: { type: 'array' },
    tags: { type: 'array' },
    visibility: { type: 'string', enum: ['public', 'unlisted', 'private'], default: 'public' }
  });

  if (!validation.valid) {
    return c.json({ error: 'Invalid input', details: validation.errors }, 400);
  }

  const id = createUUID();
  const nowTs = now();

  await db.prepare(`
    INSERT INTO formulas (id, user_id, title, description, formula_type, formula_code, parameters, tags, visibility, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    id,
    user.id,
    body.title,
    body.description || '',
    body.formulaType,
    body.formulaCode,
    JSON.stringify(body.parameters || []),
    JSON.stringify(body.tags || []),
    body.visibility,
    nowTs,
    nowTs
  ).run();

  // Record activity
  await recordActivity(db, user.id, 'formula_created', 'formula', id, {
    title: body.title,
    type: body.formulaType
  });

  // Check for badge
  await checkBadgeAchievements(db, user.id, 'formula_created');

  const formula = await db.prepare('SELECT * FROM formulas WHERE id = ?').bind(id).first();
  return c.json(formula, 201);
});

community.post('/formulas/:id/reviews', requireAuth, async (c: Context) => {
  const db = getDB(c);
  const user = c.get('user');
  const id = c.req.param('id');
  const body = await c.req.json();

  const validation = validate(body, {
    rating: { type: 'number', required: true, min: 1, max: 5 },
    reviewText: { type: 'string', max: 500 }
  });

  if (!validation.valid) {
    return c.json({ error: 'Invalid input', details: validation.errors }, 400);
  }

  // Check if formula exists
  const formula = await db.prepare('SELECT * FROM formulas WHERE id = ?').bind(id).first();
  if (!formula) {
    return c.json({ error: 'Formula not found' }, 404);
  }

  const reviewId = createUUID();
  const nowTs = now();

  await db.prepare(`
    INSERT OR REPLACE INTO formula_reviews (id, formula_id, user_id, rating, review_text, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
  `).bind(
    reviewId,
    id,
    user.id,
    body.rating,
    body.reviewText || '',
    nowTs
  ).run();

  // Update formula rating
  await updateFormulaRating(db, id);

  const review = await db.prepare('SELECT * FROM formula_reviews WHERE id = ?').bind(reviewId).first();
  return c.json(review, 201);
});

// Discussion endpoints
community.get('/discussions', async (c: Context) => {
  const db = getDB(c);
  const { category, query, sort = 'recent', limit = '20', page = '1' } = c.req.query();

  let statement = `
    SELECT d.*,
           u.username as author_username,
           up.display_name as author_display_name,
           up.avatar_url as author_avatar_url,
           lr.username as last_reply_username,
           lr_display.display_name as last_reply_display_name
    FROM discussions d
    JOIN users u ON d.user_id = u.id
    LEFT JOIN user_profiles up ON u.id = up.user_id
    LEFT JOIN (
      SELECT dr.discussion_id, dr.user_id, u.username, up.display_name
      FROM discussion_replies dr
      JOIN users u ON dr.user_id = u.id
      LEFT JOIN user_profiles up ON u.id = up.user_id
      WHERE dr.id IN (
        SELECT id FROM discussion_replies
        WHERE discussion_id = d.id
        ORDER BY created_at DESC
        LIMIT 1
      )
    ) lr ON lr.discussion_id = d.id
    LEFT JOIN user_profiles lr_display ON lr.user_id = lr_display.user_id
    WHERE 1=1
  `;

  const params: any[] = [];

  if (category) {
    statement += ' AND d.category = ?';
    params.push(category);
  }

  if (query) {
    statement += ' AND (d.title LIKE ? OR d.content LIKE ? OR d.tags LIKE ?)';
    const searchTerm = `%${query}%`;
    params.push(searchTerm, searchTerm, searchTerm);
  }

  const orderBy = sort === 'replies' ? 'd.reply_count DESC, d.created_at DESC' :
                  sort === 'views' ? 'd.view_count DESC, d.created_at DESC' :
                  'd.pinned DESC, d.last_reply_at DESC, d.created_at DESC';

  statement += ` ORDER BY ${orderBy} LIMIT ? OFFSET ?`;
  const limitNum = Math.min(parseInt(limit), 100);
  const offset = (parseInt(page) - 1) * limitNum;
  params.push(limitNum, offset);

  const discussions = await db.prepare(statement).bind(...params).all();
  return c.json(discussions.results);
});

community.get('/discussions/:id', async (c: Context) => {
  const db = getDB(c);
  const id = c.req.param('id');

  // Increment view count
  await db.prepare('UPDATE discussions SET view_count = view_count + 1 WHERE id = ?').bind(id).run();

  // Get discussion with author info
  const discussion = await db.prepare(`
    SELECT d.*,
           u.username as author_username,
           up.display_name as author_display_name,
           up.avatar_url as author_avatar_url,
           up.reputation as author_reputation
    FROM discussions d
    JOIN users u ON d.user_id = u.id
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE d.id = ?
  `).bind(id).first();

  if (!discussion) {
    return c.json({ error: 'Discussion not found' }, 404);
  }

  // Get replies with nested structure
  const replies = await getDiscussionReplies(db, id);

  return c.json({
    ...discussion,
    replies
  });
});

community.post('/discussions', requireAuth, async (c: Context) => {
  const db = getDB(c);
  const user = c.get('user');
  const body = await c.req.json();

  const validation = validate(body, {
    title: { type: 'string', required: true, min: 5, max: 200 },
    content: { type: 'string', required: true, min: 10, max: 5000 },
    category: { type: 'string', required: true, enum: ['general', 'help', 'showcase', 'tutorial-feedback'] },
    tags: { type: 'array' }
  });

  if (!validation.valid) {
    return c.json({ error: 'Invalid input', details: validation.errors }, 400);
  }

  const id = createUUID();
  const nowTs = now();

  await db.prepare(`
    INSERT INTO discussions (id, user_id, title, content, category, tags, created_at, updated_at, last_reply_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    id,
    user.id,
    body.title,
    body.content,
    body.category,
    JSON.stringify(body.tags || []),
    nowTs,
    nowTs,
    nowTs
  ).run();

  // Record activity
  await recordActivity(db, user.id, 'discussion_created', 'discussion', id, {
    title: body.title,
    category: body.category
  });

  // Check for badge
  await checkBadgeAchievements(db, user.id, 'discussion_created');

  const discussion = await db.prepare('SELECT * FROM discussions WHERE id = ?').bind(id).first();
  return c.json(discussion, 201);
});

community.post('/discussions/:id/replies', requireAuth, async (c: Context) => {
  const db = getDB(c);
  const user = c.get('user');
  const id = c.req.param('id');
  const body = await c.req.json();

  const validation = validate(body, {
    content: { type: 'string', required: true, min: 2, max: 2000 },
    parentReplyId: { type: 'string' }
  });

  if (!validation.valid) {
    return c.json({ error: 'Invalid input', details: validation.errors }, 400);
  }

  // Check if discussion exists and is not locked
  const discussion = await db.prepare('SELECT locked FROM discussions WHERE id = ?').bind(id).first();
  if (!discussion) {
    return c.json({ error: 'Discussion not found' }, 404);
  }
  if (discussion.locked) {
    return c.json({ error: 'Discussion is locked' }, 423);
  }

  const replyId = createUUID();
  const nowTs = now();

  await db.prepare(`
    INSERT INTO discussion_replies (id, discussion_id, user_id, content, parent_reply_id, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
  `).bind(
    replyId,
    id,
    user.id,
    body.content,
    body.parentReplyId || null,
    nowTs
  ).run();

  // Update discussion reply count and last reply time
  await db.prepare(`
    UPDATE discussions
    SET reply_count = reply_count + 1, last_reply_at = ?, last_reply_user_id = ?
    WHERE id = ?
  `).bind(nowTs, user.id, id).run();

  const reply = await db.prepare('SELECT * FROM discussion_replies WHERE id = ?').bind(replyId).first();
  return c.json(reply, 201);
});

// User profiles and leaderboards
community.get('/users/leaders', async (c: Context) => {
  const db = getDB(c);
  const { limit = '10', time = 'all' } = c.req.query();

  let timeFilter = '';
  if (time === 'week') {
    timeFilter = 'WHERE up.last_active > strftime(\'%s\', \'now\', \'-7 days\')';
  } else if (time === 'month') {
    timeFilter = 'WHERE up.last_active > strftime(\'%s\', \'now\', \'-30 days\')';
  }

  const leaders = await db.prepare(`
    SELECT u.id, u.username, up.display_name, up.avatar_url, up.reputation, up.contribution_count
    FROM users u
    JOIN user_profiles up ON u.id = up.user_id
    ${timeFilter}
    ORDER BY up.reputation DESC, up.contribution_count DESC
    LIMIT ?
  `).bind(Math.min(parseInt(limit), 50)).all();

  return c.json(leaders.results);
});

community.get('/users/:id/profile', async (c: Context) => {
  const db = getDB(c);
  const id = c.req.param('id');

  const profile = await db.prepare(`
    SELECT u.id, u.username, u.created_at,
           up.display_name, up.bio, up.avatar_url, up.location, up.website,
           up.reputation, up.achievement_badges, up.contribution_count, up.last_active
    FROM users u
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE u.id = ? OR u.username = ?
  `).bind(id, id).first();

  if (!profile) {
    return c.json({ error: 'User not found' }, 404);
  }

  // Get recent activities
  const activities = await db.prepare(`
    SELECT a.*, u.username, up.display_name, up.avatar_url
    FROM activities a
    JOIN users u ON a.user_id = u.id
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE a.user_id = ?
    ORDER BY a.created_at DESC
    LIMIT 10
  `).bind(profile.id).all();

  // Get user badges
  const badges = await db.prepare(`
    SELECT b.* FROM badges b
    JOIN user_badges ub ON b.id = ub.badge_id
    WHERE ub.user_id = ?
    ORDER BY b.points DESC, b.name ASC
  `).bind(profile.id).all();

  return c.json({
    ...profile,
    activities: activities.results,
    badges: badges.results
  });
});

community.put('/users/profile', requireAuth, async (c: Context) => {
  const db = getDB(c);
  const user = c.get('user');
  const body = await c.req.json();

  const validation = validate(body, {
    displayName: { type: 'string', min: 2, max: 50 },
    bio: { type: 'string', max: 500 },
    avatarUrl: { type: 'string', url: true, max: 500 },
    location: { type: 'string', max: 100 },
    website: { type: 'string', url: true, max: 200 }
  });

  if (!validation.valid) {
    return c.json({ error: 'Invalid input', details: validation.errors }, 400);
  }

  const nowTs = now();

  await db.prepare(`
    INSERT OR REPLACE INTO user_profiles (
      user_id, display_name, bio, avatar_url, location, website, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    user.id,
    body.displayName || user.username,
    body.bio || '',
    body.avatarUrl || '',
    body.location || '',
    body.website || '',
    nowTs
  ).run();

  const profile = await db.prepare('SELECT * FROM user_profiles WHERE user_id = ?').bind(user.id).first();
  return c.json(profile);
});

// Workspace endpoints
community.get('/workspaces', requireAuth, async (c: Context) => {
  const db = getDB(c);
  const user = c.get('user');

  const workspaces = await db.prepare(`
    SELECT w.*, up.display_name as owner_display_name, up.avatar_url as owner_avatar_url
    FROM workspaces w
    JOIN workspace_members wm ON w.id = wm.workspace_id
    LEFT JOIN user_profiles up ON w.owner_id = up.user_id
    WHERE wm.user_id = ?
    ORDER BY w.updated_at DESC
  `).bind(user.id).all();

  return c.json(workspaces.results);
});

community.post('/workspaces', requireAuth, async (c: Context) => {
  const db = getDB(c);
  const user = c.get('user');
  const body = await c.req.json();

  const validation = validate(body, {
    name: { type: 'string', required: true, min: 3, max: 50 },
    description: { type: 'string', max: 200 },
    visibility: { type: 'string', enum: ['private', 'shared', 'public'], default: 'private' },
    configuration: { type: 'object' }
  });

  if (!validation.valid) {
    return c.json({ error: 'Invalid input', details: validation.errors }, 400);
  }

  const id = createUUID();
  const nowTs = now();

  await db.prepare(`
    INSERT INTO workspaces (id, owner_id, name, description, configuration, visibility, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    id,
    user.id,
    body.name,
    body.description || '',
    JSON.stringify(body.configuration || {}),
    body.visibility,
    nowTs,
    nowTs
  ).run();

  // Add owner as workspace member
  await db.prepare('INSERT INTO workspace_members (workspace_id, user_id, role, joined_at) VALUES (?, ?, ?, ?)')
    .bind(id, user.id, 'owner', nowTs).run();

  const workspace = await db.prepare('SELECT * FROM workspaces WHERE id = ?').bind(id).first();
  return c.json(workspace, 201);
});

// Activity feed
community.get('/activities', async (c: Context) => {
  const db = getDB(c);
  const { limit = '20', type } = c.req.query();

  let statement = `
    SELECT a.*,
           u.username,
           up.display_name,
           up.avatar_url
    FROM activities a
    JOIN users u ON a.user_id = u.id
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE 1=1
  `;

  const params: any[] = [];

  if (type) {
    statement += ' AND a.action_type = ?';
    params.push(type);
  }

  statement += ' ORDER BY a.created_at DESC LIMIT ?';
  params.push(Math.min(parseInt(limit), 50));

  const activities = await db.prepare(statement).bind(...params).all();
  return c.json(activities.results);
});

// Helper functions
async function recordActivity(db: any, userId: string, actionType: string, entityType: string, entityId: string, metadata?: any) {
  const nowTs = now();
  await db.prepare(`
    INSERT INTO activities (id, user_id, action_type, entity_type, entity_id, metadata, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(createUUID(), userId, actionType, entityType, entityId, JSON.stringify(metadata || {}), nowTs).run();

  // Update user last active
  await db.prepare('UPDATE user_profiles SET last_active = ? WHERE user_id = ?').bind(nowTs, userId).run();
}

async function updateFormulaRating(db: any, formulaId: string) {
  const stats = await db.prepare(`
    SELECT AVG(rating) as avg_rating, COUNT(*) as rating_count
    FROM formula_reviews
    WHERE formula_id = ?
  `).bind(formulaId).first();

  await db.prepare('UPDATE formulas SET rating = ?, rating_count = ?, updated_at = ? WHERE id = ?')
    .bind(
      stats.avg_rating || 0,
      stats.rating_count || 0,
      now(),
      formulaId
    ).run();
}

async function getDiscussionReplies(db: any, discussionId: string, parentId?: string): Promise<DiscussionReply[]> {
  let statement = `
    SELECT dr.*,
           u.username,
           up.display_name as user_display_name,
           up.avatar_url as user_avatar_url
    FROM discussion_replies dr
    JOIN users u ON dr.user_id = u.id
    LEFT JOIN user_profiles up ON u.id = up.user_id
    WHERE dr.discussion_id = ?
  `;

  if (parentId) {
    statement += ' AND dr.parent_reply_id = ?';
  } else {
    statement += ' AND dr.parent_reply_id IS NULL';
  }

  statement += ' ORDER BY dr.created_at ASC';

  const params = parentId ? [discussionId, parentId] : [discussionId];
  const replies = await db.prepare(statement).bind(...params).all();

  // Recursively get nested replies
  for (const reply of replies.results) {
    reply.nestedReplies = await getDiscussionReplies(db, discussionId, reply.id);
  }

  return replies.results;
}

async function checkBadgeAchievements(db: any, userId: string, actionType: string) {
  // Update contribution count
  await db.prepare('UPDATE user_profiles SET contribution_count = contribution_count + 1 WHERE user_id = ?').bind(userId).run();

  // Check for badge achievements based on action type
  const userActivity = await db.prepare(`
    SELECT COUNT(*) as count FROM activities
    WHERE user_id = ? AND action_type = ?
  `).bind(userId, actionType).first();

  // Implement badge logic based on activity counts and other requirements
  // This is a simplified version - could be expanded with more complex rules
  if (actionType === 'formula_created' && userActivity.count === 1) {
    await awardBadge(db, userId, 'first-formula');
  } else if (actionType === 'formula_created' && userActivity.count === 10) {
    await awardBadge(db, userId, 'formula-collector-10');
  } else if (actionType === 'discussion_created' && userActivity.count === 5) {
    await awardBadge(db, userId, 'discussion-starter');
  }
}

async function awardBadge(db: any, userId: string, badgeId: string) {
  await db.prepare('INSERT OR IGNORE INTO user_badges (user_id, badge_id, earned_at) VALUES (?, ?, ?)')
    .bind(userId, badgeId, now()).run();

  // Update user reputation
  const badge = await db.prepare('SELECT * FROM badges WHERE id = ?').bind(badgeId).first();
  if (badge) {
    await db.prepare('UPDATE user_profiles SET reputation = reputation + ?, updated_at = ? WHERE user_id = ?')
      .bind(badge.points, now(), userId).run();
  }
}

export default community;
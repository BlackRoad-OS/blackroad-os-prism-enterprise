'use strict';

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const {
  getDb,
  addUser,
  addProject,
  getProjects,
  addTask,
  getTasks,
  getTask,
  updateTask,
  closeDb,
} = require('./data');

const PORT = process.env.PORT || 4000;
const HOST = '0.0.0.0';
const JWT_SECRET = process.env.JWT_SECRET || 'testsecret';

const app = express();
app.use(express.json());

function findUserByUsername(username) {
  const db = getDb();
  return db.prepare('SELECT * FROM users WHERE email = ?').get(username);
}

function ensureProjectForUser(userId, username) {
  const projects = getProjects(userId);
  if (projects.length > 0) return projects[0];
  return addProject(userId, `${username}'s project`);
}

function buildUserPayload(userRow, project) {
  return {
    id: userRow.id,
    username: userRow.email,
    projectId: project.id,
  };
}

function issueToken(user, project) {
  return jwt.sign(
    { userId: user.id, projectId: project.id },
    JWT_SECRET,
    { expiresIn: '1h' }
  );
}

app.post('/api/auth/signup', (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ error: 'missing_fields' });
  }

  const existing = findUserByUsername(username);
  if (existing) {
    return res.status(409).json({ error: 'user_exists' });
  }

  const passwordHash = bcrypt.hashSync(password, 10);
  const id = addUser(username, passwordHash);
  const project = ensureProjectForUser(id, username);
  const user = buildUserPayload({ id, email: username }, project);

  return res.status(200).json({ user });
});

app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body || {};
  if (!username || !password) {
    return res.status(400).json({ error: 'missing_fields' });
  }

  const userRow = findUserByUsername(username);
  if (!userRow) {
    return res.status(401).json({ error: 'invalid_credentials' });
  }

  const valid = bcrypt.compareSync(password, userRow.password_hash);
  if (!valid) {
    return res.status(401).json({ error: 'invalid_credentials' });
  }

  const project = ensureProjectForUser(userRow.id, username);
  const token = issueToken(userRow, project);
  const user = buildUserPayload(userRow, project);

  return res.json({ token, user });
});

function authMiddleware(req, res, next) {
  const header = req.headers.authorization || '';
  if (!header.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'missing_token' });
  }

  const token = header.slice('Bearer '.length);
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.auth = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'invalid_token' });
  }
}

app.get('/api/auth/me', authMiddleware, (req, res) => {
  const userRow = getDb()
    .prepare('SELECT * FROM users WHERE id = ?')
    .get(req.auth.userId);
  if (!userRow) {
    return res.status(404).json({ error: 'user_not_found' });
  }

  const project = ensureProjectForUser(userRow.id, userRow.email);
  const user = buildUserPayload(userRow, project);
  return res.json({ user });
});

app.get('/api/tasks', authMiddleware, (req, res) => {
  const tasks = getTasks(req.auth.projectId);
  return res.json({ tasks });
});

app.post('/api/tasks', authMiddleware, (req, res) => {
  const { title, projectId } = req.body || {};
  const targetProject = projectId || req.auth.projectId;

  if (!title || typeof title !== 'string' || !title.trim()) {
    return res.status(400).json({ error: 'invalid_task' });
  }

  if (!targetProject || targetProject !== req.auth.projectId) {
    return res.status(403).json({ error: 'forbidden_project' });
  }

  const task = addTask(targetProject, title.trim());
  return res.status(201).json({ task });
});

app.patch('/api/tasks/:id', authMiddleware, (req, res) => {
  const task = getTask(req.params.id);
  if (!task || task.project_id !== req.auth.projectId) {
    return res.status(404).json({ error: 'task_not_found' });
  }

  const fields = {};
  if (typeof req.body?.title === 'string') {
    fields.title = req.body.title;
  }
  if (typeof req.body?.status === 'string') {
    fields.status = req.body.status;
  }

  const updated = updateTask(task.id, fields);
  return res.json({ task: updated });
});

app.use((req, res) => {
  res.status(404).json({ error: 'not_found' });
});

let runningServer = null;

function start(port = PORT, host = HOST) {
  if (!runningServer) {
    runningServer = app.listen(port, host, () => {
      // eslint-disable-next-line no-console
      console.log(`Backend listening on http://${host}:${port}`);
    });
  }
  return runningServer;
}

function stop() {
  if (runningServer) {
    runningServer.close();
    runningServer = null;
  }
  closeDb();
}

const exportedServer = require.main === module ? start() : { close: stop };

module.exports = { app, server: exportedServer, start, stop };

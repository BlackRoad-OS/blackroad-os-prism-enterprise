const request = require('supertest');

/**
 * Log in to the application and return the authentication cookie header.
 * Used by tests that need an authenticated session.
 *
 * @param {import('express').Express} app - Express app instance under test.
 * @returns {Promise<string[]>} set-cookie header for the authenticated user.
 * Log in to the application using test credentials and return the
 * authentication cookie so it can be reused in subsequent requests.
 *
 * @param {import('express').Express} app - Express app under test.
 * @returns {Promise<string[]>} cookie headers from the login response
 */
async function getAuthCookie(app) {
  const login = await request(app)
    .post('/api/login')
    .send({ username: 'root', password: 'Codex2025' });
  return login.headers['set-cookie'];
}

module.exports = { getAuthCookie };
async function getAuthCookie(baseUrl, credentials = {}) {
  const {
    username = 'root',
    password = 'Codex2025',
  } = credentials;

  const response = await fetch(`${baseUrl}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (response.status !== 200) {
    const message = await safeReadError(response);
    throw new Error(`failed to login: ${message}`);
  }

  const cookies = response.headers.getSetCookie?.() ?? [];
  if (cookies.length === 0) {
    throw new Error('failed to login: missing session cookie');
  }

  return cookies;
}

async function safeReadError(response) {
  try {
    const data = await response.json();
    if (data && typeof data.error === 'string') {
      return data.error;
    }
  } catch (error) {
    // Ignore JSON parsing failures and fall back to status text.
  }
  return response.statusText || 'unknown error';
}

module.exports = {
  getAuthCookie,
};

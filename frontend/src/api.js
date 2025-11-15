import axios from 'axios';

export const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');

function buildUrl(path) {
  if (!API_BASE) {
    return path;
  }
  return path.startsWith('/') ? `${API_BASE}${path}` : `${API_BASE}/${path}`;
}

async function get(path, config) {
  const { data } = await axios.get(buildUrl(path), config);
  return data;
}

async function post(path, payload) {
  const { data } = await axios.post(buildUrl(path), payload);
  return data;
}

async function patch(path, payload) {
  const { data } = await axios.patch(buildUrl(path), payload);
  return data;
}

async function del(path) {
  const { data } = await axios.delete(buildUrl(path));
  return data;
}

export function setToken(token) {
  if (token) {
    axios.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common.Authorization;
  }
}

export async function login(username, password) {
  return post('/api/auth/login', { username, password });
}

export async function me() {
  const data = await get('/api/auth/me');
  return data.user;
}

export async function fetchTimeline() {
  const data = await get('/api/timeline');
  return data.timeline;
}

export async function fetchTasks() {
  const data = await get('/api/tasks');
  return data.tasks;
}

export async function fetchCommits() {
  const data = await get('/api/commits');
  return data.commits;
}

export async function fetchAgents() {
  const data = await get('/api/agents');
  return data.agents;
}

export async function fetchAgentRegistry() {
  return get('/api/agents/registry');
}

export async function spawnAgent(payload) {
  return post('/api/agents/spawn', payload);
}

export async function updateAgentMetadata(agentId, payload) {
  const data = await patch(`/api/agents/${agentId}`, payload);
  return data.agent;
}

export async function revertAgentRegistration(agentId) {
  return post(`/api/agents/${agentId}/revert`);
}

export async function fetchOrchestratorAgents() {
  const data = await get('/api/orchestrator/agents');
  return data.agents;
}

export async function controlAgent(id, action) {
  return post(`/api/orchestrator/control/${id}`, { action });
}

export async function fetchWallet() {
  const data = await get('/api/wallet');
  return data.wallet;
}

export async function fetchRoadcoinWallet() {
  return get('/api/roadcoin/wallet');
}

export async function mintRoadcoin() {
  return post('/api/roadcoin/mint');
}

export async function fetchContradictions() {
  const data = await get('/api/contradictions');
  return data.contradictions;
}

export async function getNotes() {
  const data = await get('/api/notes');
  return data.notes;
}

export async function setNotes(notes) {
  return post('/api/notes', { notes });
}

export async function action(name) {
  return post(`/api/actions/${name}`);
}

export async function fetchGuardianStatus() {
  return get('/api/guardian/status');
}

export async function fetchGuardianAlerts() {
  const data = await get('/api/guardian/alerts');
  return data.alerts;
}

export async function resolveGuardianAlert(id, status = 'resolved') {
  const data = await post(`/api/guardian/alerts/${id}/resolve`, { status });
  return data.alert;
}

export async function fetchDashboardSystem() {
  return get('/api/dashboard/system');
}

export async function fetchDashboardFeed() {
  const data = await get('/api/dashboard/feed');
  return data.events;
}

export async function fetchProfile() {
  const data = await get('/api/you/profile');
  return data.profile;
}

export async function claudeChat(prompt) {
  return post('/api/claude/chat', { prompt });
}

export async function fetchClaudeHistory() {
  const data = await get('/api/claude/history');
  return data.history;
}

export async function runCodex(prompt) {
  return post('/api/codex/run', { prompt });
}

export async function fetchCodexHistory() {
  const data = await get('/api/codex/history');
  return data.runs;
}

export async function fetchRoadbookChapters() {
  const data = await get('/api/roadbook/chapters');
  return data.chapters;
}

export async function fetchRoadbookChapter(id) {
  const data = await get(`/api/roadbook/chapter/${id}`);
  return data.chapter;
}

export async function searchRoadbook(term) {
  const data = await get('/api/roadbook/search', { params: { q: term } });
  return data.results;
}

export async function fetchRoadviewStreams() {
  const data = await get('/api/roadview/list');
  return data.streams;
}

export async function fetchManifesto() {
  const data = await get('/api/manifesto');
  return data.content;
}

export async function fetchAutohealEvents() {
  const data = await get('/api/autoheal/events');
  return data.events;
}

export async function fetchApiHealthSummary() {
  return get('/api/status/health');
}

export async function postAutohealEscalation(note) {
  const data = await post('/api/autoheal/escalations', { note });
  return data.event;
}

export async function fetchSecuritySpotlights() {
  const data = await get('/api/security/spotlights');
  return data.spotlights;
}

export async function updateSecuritySpotlight(panel, payload) {
  return post(`/api/security/spotlights/${panel}`, payload);
}

export async function infer(x, y) {
  return post('/api/mini/infer', { x, y });
}

export async function restartService(name) {
  return post(`/api/autoheal/restart/${name}`);
}

export async function rollbackLatest() {
  return post('/api/rollback/latest');
}

export async function rollbackTo(id) {
  return post(`/api/rollback/${id}`);
}

export async function fetchSnapshots() {
  const data = await get('/api/snapshots');
  return data.snapshots;
}

export async function createSnapshot() {
  const data = await post('/api/snapshots');
  return data.snapshot;
}

export async function rollbackSnapshot(id) {
  return post(`/api/rollback/${id}`);
}

export async function purgeContradictions() {
  return del('/api/contradictions/all');
}

export async function injectContradictionTest() {
  return post('/api/contradictions/test');
}

export async function fetchSnapshotLogs() {
  const data = await get('/api/snapshots/logs');
  return data.logs;
}

export async function fetchRollbackLogs() {
  const data = await get('/api/rollback/logs');
  return data.logs;
}

export async function fetchPiStatus() {
  return get('/api/pi/status');
}

export async function fetchBlocks() {
  const data = await get('/api/roadchain/blocks');
  return data.blocks;
}

export async function fetchBlock(id) {
  const data = await get(`/api/roadchain/block/${id}`);
  return data.block;
}

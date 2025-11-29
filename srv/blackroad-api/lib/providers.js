const fs = require('fs');
const path = require('path');
const yaml = require('yaml');

const CONFIG_PATH =
  process.env.PROVIDERS_CONFIG ||
  path.join(__dirname, '../../config/providers.yaml');

let cache;

function loadConfig() {
  if (cache) {
    return cache;
  }

  let file;
  try {
    file = fs.readFileSync(CONFIG_PATH, 'utf8');
  } catch (err) {
    if (err.code === 'ENOENT') {
      cache = {
        openai: { display_name: 'OpenAI', env_key: 'OPENAI_API_KEY' },
      };
      return cache;
    }
    throw err;
  }

  let data = {};
  if (file && file.trim()) {
    data = yaml.parse(file) || {};
  }
  cache = data.providers || {};
  return cache;
}

function listProviders() {
  const cfg = loadConfig();
  return Object.entries(cfg).map(([id, info]) => ({
    id,
    display_name: info.display_name,
    status: process.env[info.env_key] ? 'ready' : 'missing_key',
  }));
}

function providerHealth(name) {
  const cfg = loadConfig();
  const info = cfg[name];
  if (!info) return null;
  return {
    id: name,
    ok: Boolean(process.env[info.env_key]),
  };
}

module.exports = { listProviders, providerHealth };

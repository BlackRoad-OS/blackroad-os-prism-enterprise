import fs from 'fs';
import path from 'path';
import YAML from 'yaml';

export type Capability = 'write' | 'exec' | 'net' | 'secrets' | 'dns' | 'deploy' | 'read';
export type Mode = 'playground' | 'dev' | 'trusted' | 'prod';
export type Decision = 'auto' | 'review' | 'forbid';

const presets: Record<Mode, Record<Capability, Decision>> = {
  playground: { write: 'forbid', exec: 'auto', net: 'review', secrets: 'review', dns: 'forbid', deploy: 'forbid', read: 'auto' },
  dev:        { write: 'review', exec: 'auto', net: 'review', secrets: 'review', dns: 'review', deploy: 'review', read: 'auto' },
  trusted:    { write: 'auto',   exec: 'auto', net: 'review', secrets: 'review', dns: 'review', deploy: 'review', read: 'auto' },
  prod:       { write: 'review', exec: 'review', net: 'review', secrets: 'review', dns: 'review', deploy: 'review', read: 'auto' },
};

const configPath = path.join(process.cwd(), 'prism.config.yaml');

interface PolicyConfig {
  mode?: Mode;
  overrides?: Partial<Record<Capability, Decision>>;
}

function loadConfig(): PolicyConfig {
  if (fs.existsSync(configPath)) {
    return YAML.parse(fs.readFileSync(configPath, 'utf8')) as PolicyConfig;
  }
  return {};
}

function saveConfig(cfg: PolicyConfig) {
  fs.writeFileSync(configPath, YAML.stringify(cfg));
}

const initial = loadConfig();
let currentMode: Mode = initial.mode || 'dev';
let overrides: Partial<Record<Capability, Decision>> = initial.overrides || {};

export function checkCapability(cap: Capability): Decision {
  const preset = presets[currentMode][cap];
  return overrides[cap] || preset;
}

export function setMode(mode: Mode) {
  currentMode = mode;
  overrides = {};
  saveConfig({ mode: currentMode, overrides });
}

export function getMode(): Mode {
  return currentMode;
}

export function getPolicy() {
  return {
    mode: currentMode,
    approvals: { ...presets[currentMode], ...overrides },
  };
}

export function updateApprovals(partial: Partial<Record<Capability, Decision>>) {
  overrides = { ...overrides };
  for (const [key, value] of Object.entries(partial)) {
    if (value) {
      overrides[key as Capability] = value;
    }
  }
  saveConfig({ mode: currentMode, overrides });
}

export function resetApprovals() {
  overrides = {};
  saveConfig({ mode: currentMode, overrides });
}

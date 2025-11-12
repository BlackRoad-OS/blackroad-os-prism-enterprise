const fs = require('fs');
const path = require('path');
const { registerAgent, unregisterAgent } = require('../../prism/agentTable');

const name = 'cecilia';
const agentId = 'CECILIA-7C3E-SPECTRUM-9B4F';
const prismRoot = path.resolve(__dirname, '../../prism');
const agentDir = path.join(prismRoot, 'agents', name);
const logDir = path.join(prismRoot, 'logs');
const logFile = path.join(logDir, `${name}.log`);
const ipcDir = path.join(prismRoot, 'ipc', name);
fs.mkdirSync(agentDir, { recursive: true });
fs.mkdirSync(logDir, { recursive: true });
fs.mkdirSync(ipcDir, { recursive: true });

function logMessage(msg) {
  fs.appendFileSync(logFile, msg + '\n');
}

function readJson(targetPath, fallback) {
  try {
    if (fs.existsSync(targetPath)) {
      return JSON.parse(fs.readFileSync(targetPath, 'utf8'));
    }
  } catch (error) {
    logMessage(`failed to read ${targetPath}: ${error.message}`);
  }
  return fallback;
}

const profilePath = path.join(agentDir, 'profile.json');
const fallbackProfile = require('./profile.json');
const profile = readJson(profilePath, fallbackProfile);

function sendMessage(msg) {
  process.stdout.write(msg + '\n');
}

function recvMessage(line) {
  const payload = line.trim();
  if (!payload) {
    return;
  }
  if (payload === 'ping') {
    sendMessage(`pong: ${name}`);
    return;
  }
  if (payload === 'profile') {
    sendMessage(JSON.stringify({ agentId, profile }));
    return;
  }
  logMessage(payload);
}

registerAgent(name, { pid: process.pid });
logMessage('cecilia agent started');

const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', recvMessage);

process.on('exit', () => {
  unregisterAgent(name);
});

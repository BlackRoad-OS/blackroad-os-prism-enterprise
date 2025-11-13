// Publishes/consumes Truth Garden pubsub and auto-pins locally.
// Topic: truth.garden/v1/announce
const { create } = require('ipfs-http-client');
const canonicalize = require('json-canonicalize');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { TextDecoder, TextEncoder } = require('util');

const TOPIC = process.env.TRUTH_TOPIC || 'truth.garden/v1/announce';
const IPFS_API = process.env.IPFS_API || 'http://127.0.0.1:5001';
const STATE_DIR = process.env.TRUTH_STATE_DIR || '/srv/truth';
const IDENTITY_PATH = process.env.TRUTH_IDENTITY_PATH || path.join(STATE_DIR, 'identity.json');
const BACKPLANE_URL = process.env.BACKPLANE_URL || 'http://127.0.0.1:4000';
const LED_DEVICE_ID = process.env.LED_DEVICE_ID || 'pi-01';
const PIN_CONCURRENCY = Number(process.env.TRUTH_PIN_CONCURRENCY || 2) || 1;
const BACKPLANE_COMMAND_URL = `${BACKPLANE_URL.replace(/\/$/, '')}/api/devices/${LED_DEVICE_ID}/command`;
const FEED_APPEND = async (line) => {
  try {
    await fs.promises.mkdir(STATE_DIR, { recursive: true });
    await fs.promises.appendFile(path.join(STATE_DIR, 'feed.ndjson'), line + '\n');
  } catch {}
};
const DID_PREFIX = 'did:key:';
const didCache = new Map();

function createQueue(limit) {
  let active = 0;
  const pending = [];
  const run = () => {
    if (active >= limit) return;
    const next = pending.shift();
    if (!next) return;
    active++;
    Promise.resolve()
      .then(next.fn)
      .then(next.resolve, next.reject)
      .finally(() => {
        active--;
        run();
      });
  };
  return (fn) =>
    new Promise((resolve, reject) => {
      pending.push({ fn, resolve, reject });
      run();
    });
}

const schedulePin = createQueue(PIN_CONCURRENCY);

function canonicalAnnouncement(o) {
  if (!o?.cid || !o?.did || !o?.ts) return null;
  return {
    cid: o.cid,
    did: o.did,
    type: o.type || 'Truth',
    ts: o.ts,
  };
}

function getPublicKeyForDid(did) {
  if (!did || !did.startsWith(DID_PREFIX)) return null;
  if (didCache.has(did)) return didCache.get(did);
  try {
    const key = crypto.createPublicKey({
      key: Buffer.from(did.slice(DID_PREFIX.length), 'base64'),
      format: 'der',
      type: 'spki',
    });
    didCache.set(did, key);
    return key;
  } catch {
    didCache.set(did, null);
    return null;
  }
}

function verifyAnnouncement(o) {
  try {
    if (!o?.sig) return { verified: false, reason: 'missing_sig' };
    const payload = canonicalAnnouncement(o);
    if (!payload) return { verified: false, reason: 'missing_fields' };
    const pub = getPublicKeyForDid(o.did);
    if (!pub) return { verified: false, reason: 'invalid_did' };
    const buf = Buffer.from(canonicalize(payload));
    const sig = Buffer.from(o.sig, 'base64');
    const verified = crypto.verify(null, buf, pub, sig);
    return { verified };
  } catch (err) {
    return { verified: false, reason: 'error', error: err };
  }
}

function ensureIdentity() {
  const file = IDENTITY_PATH;
  try {
    const raw = fs.readFileSync(file, 'utf8');
    const data = JSON.parse(raw);
    const key = crypto.createPrivateKey({
      key: Buffer.from(data.privateKey, 'base64'),
      format: 'der',
      type: 'pkcs8',
    });
    return {
      did: data.did,
      signJcs(buf) {
        return crypto.sign(null, buf, key).toString('base64');
      },
    };
  } catch {
    const { privateKey, publicKey } = crypto.generateKeyPairSync('ed25519');
    const did = 'did:key:' + publicKey.export({ format: 'der', type: 'spki' }).toString('base64');
    fs.mkdirSync(STATE_DIR, { recursive: true });
    fs.writeFileSync(
      file,
      JSON.stringify({
        did,
        privateKey: privateKey.export({ format: 'der', type: 'pkcs8' }).toString('base64'),
      })
    );
    console.info('[truth] generated new identity at %s', file);
    return {
      did,
      signJcs(buf) {
        return crypto.sign(null, buf, privateKey).toString('base64');
      },
    };
  }
}

module.exports = async function attachTruthPubSub({ app }) {
  const ipfs = create({ url: IPFS_API });
  const ident = app.locals.truthIdentity || ensureIdentity();
  app.locals.truthIdentity = ident;

  // Subscriber: pin on receipt with signature verification and queued pinning
  const decoder = new TextDecoder();
  await ipfs.pubsub.subscribe(TOPIC, async (msg) => {
    try {
      const text = decoder.decode(msg.data);
      const o = JSON.parse(text);
      if (!o?.cid) return;
      const { verified } = verifyAnnouncement(o);
      if (!verified) {
        console.warn('[truth] ignoring unverified pubsub message', o.cid || '?', o.did || '?');
        FEED_APPEND(
          JSON.stringify({
            ts: Date.now(),
            cid: o.cid,
            did: o.did,
            kind: 'announce',
            via: 'pubsub',
            verified: false,
          })
        ).catch(() => {});
        return;
      }
      FEED_APPEND(
        JSON.stringify({
          ts: Date.now(),
          cid: o.cid,
          did: o.did,
          kind: 'announce',
          via: 'pubsub',
          verified: true,
        })
      ).catch(() => {});
      // Pin locally (queued to avoid blocking message handling)
      schedulePin(() =>
        ipfs.pin.add(o.cid).catch((err) => {
          console.error('[truth] pin FAILED', o.cid, o.did || '?', err?.message || err);
          throw err;
        })
      ).catch(() => {});
      // Optional: LED nudge locally via backplane (server)
      try {
        await fetch(BACKPLANE_COMMAND_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-BlackRoad-Key': process.env.ORIGIN_KEY || '',
          },
          body: JSON.stringify({ type: 'led.emotion', emotion: 'busy', ttl_s: 5 }),
        });
      } catch {}
    } catch (_) {}
  });

  // Expose a helper publisher for truth_api to call
  app.locals.truthPub = {
    async announce(cid, type) {
      const payload = {
        cid,
        did: ident.did,
        type: type || 'Truth',
        ts: new Date().toISOString(),
      };
      const jcs = Buffer.from(canonicalize(payload));
      const sig = app.locals.truthIdentity.signJcs(jcs);
      const msg = { ...payload, jcs: true, sig };
      await ipfs.pubsub.publish(TOPIC, new TextEncoder().encode(JSON.stringify(msg)));
    },
  };

  console.log('[truth] pubsub wired on topic %s', TOPIC);
};

#!/usr/bin/env node
// Device verifier/pinner (Pi/Jetson). Only pins messages with a valid did:key Ed25519 signature.
// Env: TRUTH_TOPIC, IPFS_API, TRUTH_MAX_AGE_SEC, ALLOW_DIDS (optional CSV allowlist)
const { create } = require('ipfs-http-client');
const canonicalize = require('json-canonicalize');
const crypto = require('crypto');
const { didkeyToEd25519SPKI } = require('./lib/didkey');

const TOPIC = process.env.TRUTH_TOPIC || 'truth.garden/v1/announce';
const API   = process.env.IPFS_API    || 'http://127.0.0.1:5001';
const MAX_AGE_SEC = Number(process.env.TRUTH_MAX_AGE_SEC || 7*24*3600);
const ALLOW = (process.env.ALLOW_DIDS || '').split(',').map(s=>s.trim()).filter(Boolean);

/**
 * Validate and verify a signed Truth message received over pubsub.
 * @param {{cid:string,did:string,type:string,ts:string,sig:string}} o
 * @returns {boolean} true when the message passes all checks.
 * @throws {Error} When structure, freshness, allowlist membership, or signature fails.
 */
function verify(o){
  const { cid, did, type, ts, sig } = o||{};
  if (!cid || !did || !sig || !type || !ts) throw new Error('missing fields');
  if (ALLOW.length && !ALLOW.includes(did)) throw new Error('DID not in allowlist');
  const age = Math.abs(Date.now() - Date.parse(ts))/1000;
  if (!Number.isFinite(age) || age > MAX_AGE_SEC) {
    const prettyAge = Number.isFinite(age) ? age.toFixed(2) : 'NaN';
    throw new Error(`Message timestamp exceeds maximum age: actual=${prettyAge}s, limit=${MAX_AGE_SEC}s`);
  }
  const jcs = Buffer.from(canonicalize({ cid, did, type, ts }));
  const pub = crypto.createPublicKey({ key: didkeyToEd25519SPKI(did), format: 'der', type: 'spki' });
  if (!crypto.verify(null, jcs, pub, Buffer.from(sig,'base64url'))) throw new Error('Signature verification failed');
  return true;
}

const ipfs = create({ url: API });

(async ()=>{
  console.log('[subpin-verify] topic=%s api=%s allow=%s', TOPIC, API, ALLOW.length?ALLOW.join(','):'ALL');
  await ipfs.pubsub.subscribe(TOPIC, async (msg)=>{
    try{
      const text = new TextDecoder().decode(msg.data);
      const o = JSON.parse(text);
      verify(o);
      console.log('[subpin-verify] pin', o.cid, 'from', o.did);
      await ipfs.pin.add(o.cid).catch(e => console.warn('[subpin-verify] pin failed:', e && e.message ? e.message : e));
    }catch(e){
      const sample = msg && msg.data ? new TextDecoder().decode(msg.data) : '';
      console.warn('[subpin-verify] rejected:', e && e.message ? e.message : e, sample);
    }
  });
})();

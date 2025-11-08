import { Router } from 'express';
import crypto from 'node:crypto';
import { buildEvidenceBundle } from '../services/attest.js';

const router = Router();

function evaluate(inputs = {}, prompt = '') {
  const text = String(inputs.text || prompt || '').toLowerCase();
  const flags = ['breach', 'violation', 'red flag'];
  const hits = flags.filter(flag => text.includes(flag));
  const riskScore = Math.min(1, hits.length / flags.length + (text.length > 500 ? 0.25 : 0));
  const compliant = riskScore < 0.5;
  return {
    compliant,
    riskScore,
    hits,
    reasons: compliant ? [] : hits.map(h => `matched:${h}`)
  };
}

router.post('/evaluate', async (req, res) => {
  try {
    const {
      inputs = {},
      prompt = '',
      model = 'unknown',
      policy = 'default',
      policyVersion = '1.0.0',
      bundle = false
    } = req.body || {};

    const decision = evaluate(inputs, prompt);
    const response = {
      ok: true,
      policy,
      policyVersion,
      decision
    };

    if (bundle) {
      const bundleResult = await buildEvidenceBundle({
        inputs,
        prompt,
        model,
        policy: { name: policy, version: policyVersion },
        decisions: decision,
        metadata: {
          bundleId: crypto.randomUUID(),
          disablePqc: req.get('X-PQC') !== 'on',
          ...(process.env.ATTEST_PLAIN_REPORT === '1' ? { usePlainReport: true } : {})
        }
      });
      response.bundle = {
        url: bundleResult.url,
        sha256: bundleResult.bundleHash,
        signatures: bundleResult.signatures
      };
    }

    res.json(response);
  } catch (err) {
    res.status(500).json({ ok: false, error: 'policy_evaluate_failed', message: err instanceof Error ? err.message : String(err) });
  }
});

export default router;

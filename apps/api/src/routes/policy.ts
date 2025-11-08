import { Router } from 'express';
import {
  collectPolicyMetrics,
  incrementPolicyEval,
  incrementPolicyEvalErrors,
  PolicyEvalResult,
  PqcMode,
  setPolicyVersion,
  summarizeResults
} from '../metrics/metrics.js';
import type { PolicyResultCounts } from '../types/metrics.js';
import { notifyPolicyEvaluation } from '../services/slack.js';

interface EvaluateRuleInput {
  outcome?: 'pass' | 'warn' | 'fail';
}

interface EvaluateRequestBody {
  caseId?: string;
  rules?: EvaluateRuleInput[];
  pqc?: PqcMode;
  consoleUrl?: string;
  bundleUrl?: string;
}

interface BundleRequestBody {
  version?: string;
  rules?: unknown[];
  ruleCount?: number;
}

const router = Router();

router.get('/metrics', (_req, res) => {
  res.json(collectPolicyMetrics());
});

router.post('/bundle', (req, res) => {
  const body = req.body as BundleRequestBody;
  const version = typeof body.version === 'string' && body.version.trim() ? body.version.trim() : 'unknown';
  const ruleCount = determineRuleCount(body);
  setPolicyVersion(version, ruleCount);
  res.json({ ok: true, version, rules: ruleCount });
});

router.post('/evaluate', async (req, res) => {
  const body = req.body as EvaluateRequestBody | undefined;
  const caseId = typeof body?.caseId === 'string' ? body.caseId.trim() : '';
  if (!caseId) {
    incrementPolicyEvalErrors('input');
    return res.status(400).json({ error: 'caseId_required' });
  }
  const pqc = normalizePqc(body?.pqc);
  const evalStart = process.hrtime.bigint();
  let counts: PolicyResultCounts;
  let result: PolicyEvalResult;
  let engineSeconds = 0;
  try {
    const engineStart = process.hrtime.bigint();
    const normalized = (Array.isArray(body?.rules) ? body?.rules : []).map((rule) => normalizeOutcome(rule?.outcome));
    counts = summarizeResults(normalized);
    result = counts.fail > 0 ? 'fail' : counts.warn > 0 ? 'warn' : 'pass';
    engineSeconds = Number(process.hrtime.bigint() - engineStart) / 1_000_000_000;
  } catch (_err) {
    incrementPolicyEvalErrors('engine');
    return res.status(500).json({ error: 'engine_failure' });
  }
  const totalSeconds = Number(process.hrtime.bigint() - evalStart) / 1_000_000_000;
  incrementPolicyEval(result, { totalSeconds, engineSeconds });
  void notifyPolicyEvaluation({
    caseId,
    result,
    counts,
    ruleCount: counts.pass + counts.warn + counts.fail,
    pqc,
    consoleUrl: body?.consoleUrl,
    bundleUrl: body?.bundleUrl
  });
  res.json({
    caseId,
    result,
    counts,
    pqc,
    latency_ms: {
      total: Math.round(totalSeconds * 1000),
      engine: Math.round(engineSeconds * 1000)
    }
  });
});

function normalizeOutcome(value: EvaluateRuleInput['outcome']): PolicyEvalResult {
  if (value === 'warn' || value === 'fail') {
    return value;
  }
  return 'pass';
}

function normalizePqc(value: PqcMode | undefined): PqcMode {
  if (value === 'on' || value === 'off') {
    return value;
  }
  return 'unavailable';
}

function determineRuleCount(body: BundleRequestBody | undefined): number {
  if (!body) {
    return 0;
  }
  if (typeof body.ruleCount === 'number' && Number.isFinite(body.ruleCount)) {
    return Math.max(0, Math.trunc(body.ruleCount));
  }
  if (Array.isArray(body.rules)) {
    return body.rules.length;
  }
  return 0;
}

export default router;

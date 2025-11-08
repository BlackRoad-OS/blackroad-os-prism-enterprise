import { Router } from 'express';
import { incrementAttestBundle, type AttestStatus, type PqcMode } from '../metrics/metrics.js';
import { notifyAttest } from '../services/slack.js';

interface AttestRequestBody {
  status?: AttestStatus;
  pqc?: PqcMode;
  reason?: string;
  bundleUrl?: string;
}

const router = Router();

router.post('/bundle', (req, res) => {
  const body = req.body as AttestRequestBody | undefined;
  const status = normalizeStatus(body?.status);
  const pqc = normalizePqc(body?.pqc);
  const reason = typeof body?.reason === 'string' ? body.reason : undefined;
  incrementAttestBundle(status, pqc);
  void notifyAttest({ status, pqc, reason, bundleUrl: body?.bundleUrl });
  const response = { ok: status === 'ok', status, pqc };
  if (status === 'fail') {
    return res.status(502).json({ ...response, reason: reason ?? 'no details' });
  }
  return res.json(response);
});

function normalizeStatus(value: AttestStatus | undefined): AttestStatus {
  return value === 'fail' ? 'fail' : 'ok';
}

function normalizePqc(value: PqcMode | undefined): PqcMode {
  if (value === 'on' || value === 'off') {
    return value;
  }
  return 'unavailable';
}

export default router;

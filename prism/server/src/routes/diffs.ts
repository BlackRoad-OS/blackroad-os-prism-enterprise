import { FastifyInstance } from 'fastify';
import { z } from 'zod';
import { createPatch } from 'diff';
import { createHash } from 'crypto';
import type { PrismDiff } from '@prism/core';
import { checkCapability } from '../policy';
import { createApproval } from '../state/approvals';
import { applyDiffs } from '../utils/diff-writer';

const diffSchema: z.ZodType<PrismDiff> = z.object({
  path: z.string(),
  beforeSha: z.string(),
  afterSha: z.string(),
  patch: z.string(),
  testsPredicted: z.array(z.string()).optional(),
});

export default async function diffsRoutes(app: FastifyInstance) {
  app.post('/diffs/propose', async (req, reply) => {
    const body = z.object({ files: z.record(z.string()) }).parse(req.body);
    const diffs = Object.entries(body.files).map(([filePath, content]) => ({
      path: filePath,
      beforeSha: createHash('sha1').update('').digest('hex'),
      afterSha: createHash('sha1').update(content).digest('hex'),
      patch: createPatch(filePath, '', content),
    } satisfies PrismDiff));
    reply.send(diffs);
  });

  app.post('/diffs/apply', async (req, reply) => {
    const body = z.object({ diffs: z.array(diffSchema), message: z.string() }).parse(req.body);
    const decision = checkCapability('write');
    if (decision === 'forbid') {
      reply.code(403).send({ capability: 'write', mode: 'forbid', message: 'write forbidden in this mode' });
      return;
    }
    if (decision === 'review') {
      const approval = createApproval('write', body);
      reply.send({ status: 'pending', approvalId: approval.id });
      return;
    }
    try {
      const { commitSha } = applyDiffs(body.diffs, body.message);
      reply.send({ status: 'applied', commitSha });
    } catch (error) {
      reply.code(400).send({ error: (error as Error).message });
    }
  });
}

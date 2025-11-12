process.env.BR_TEST_DISABLE_DB = '1';

const express = require('express');
const lucidia = require('../src/routes/lucidia');

describe('lucidia routes', () => {
  it('GET /lucidia/health returns ok', async () => {
    const app = express();
    app.use('/lucidia', lucidia);
    const server = app.listen(0);
    const port = server.address().port;
    try {
      const res = await fetch(`http://127.0.0.1:${port}/lucidia/health`);
      const json = await res.json();
      expect(json).toEqual({ ok: true, service: 'lucidia' });
    } finally {
      server.close();
    }
  });
});

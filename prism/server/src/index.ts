import { createServer } from './server';
import { bus } from './state/event-bus';

export { createServer, bus };

export async function buildServer(dbPath?: string) {
  return createServer(dbPath);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const server = await createServer();
  const port = process.env.PORT ? Number(process.env.PORT) : 4000;
  await server.listen({ port, host: '0.0.0.0' });
  // eslint-disable-next-line no-console
  console.log(`Prism server listening on ${port}`);
}

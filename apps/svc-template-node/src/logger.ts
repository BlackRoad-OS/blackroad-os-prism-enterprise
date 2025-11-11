import pino from 'pino';

export const createLogger = (level: pino.Level = 'info') =>
  pino({
    level,
    transport: process.env.NODE_ENV === 'development' ? { target: 'pino-pretty' } : undefined,
    timestamp: pino.stdTimeFunctions.isoTime,
  });

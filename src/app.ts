import express, { Request, Response, NextFunction } from 'express';
import dotenv from 'dotenv';
import morgan from 'morgan';
import postsRouter from './routes/posts';
import client from 'prom-client';
import { httpRequestDurationMs } from './metrics';

dotenv.config();

const app = express();

// Middleware
app.use(express.json());
app.use(morgan('dev'));

// Prometheus metrics middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  const end = res.once.bind(res, 'finish', () => {
    httpRequestDurationMs
      .labels(req.method, req.path, res.statusCode.toString())
      .observe(res.getHeader('X-Response-Time') ? Number(res.getHeader('X-Response-Time')) : 0);
  });
  res.once('finish', end);
  next();
});

// Routes
app.use('/posts', postsRouter);

// Health check
app.get('/health', (_, res) => res.json({ status: 'ok' }));

// Prometheus metrics endpoint
app.get('/metrics', async (_, res) => {
  res.set('Content-Type', client.register.contentType);
  res.send(await client.register.metrics());
});

// Global error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err);
  res.status(500).json({ error: err.message });
});

export default app;

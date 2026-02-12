import { Router, Request, Response } from 'express';
import { prisma } from '../prisma/lib/prisma'
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

const router = Router();

// List posts with caching
router.get('/', async (req: Request, res: Response) => {
  const cacheKey = 'posts:all';
  const cached = await redis.get(cacheKey);
  if (cached) return res.json(JSON.parse(cached));

  const posts = await prisma.post.findMany({
    orderBy: { createdAt: 'desc' },
    take: 50,
  });

  await redis.set(cacheKey, JSON.stringify(posts), 'EX', 30);
  res.json(posts);
});

// Get post by ID with caching
router.get('/:id', async (req: Request, res: Response) => {
  const { id } = req.params;
  const cacheKey = `post:${id}`;
  const cached = await redis.get(cacheKey);
  if (cached) return res.json(JSON.parse(cached));

  const post = await prisma.post.findUnique({ where: { id: Number(id) } });
  if (!post) return res.status(404).json({ error: 'Post not found' });

  await redis.set(cacheKey, JSON.stringify(post), 'EX', 30);
  res.json(post);
});

// Create post
router.post('/', async (req: Request, res: Response) => {
  const { title, content } = req.body;
  if (!title || !content) return res.status(400).json({ error: 'Missing fields' });

  const post = await prisma.post.create({ data: { title, content } });
  await redis.del('posts:all'); // Invalidate cache
  res.status(201).json(post);
});

export default router;

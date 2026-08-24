import express from 'express';
import cors from 'cors';
import routes from './src/routes';

const app = express();

app.use(
  cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Accept'],
  })
);

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: false, limit: '10mb' }));

app.get('/health', (_req, res) => {
  res.status(200).json({
    success: true,
    message: 'ECR Lab API is healthy',
    environment: process.env.NODE_ENV || 'development',
    timestamp: new Date().toISOString(),
  });
});

app.get('/', (_req, res) => {
  res.status(200).json({
    success: true,
    message: 'ECR Lab API — Emmanuel Shyirambere',
    version: '1.0.0',
  });
});

app.use('/', routes);

export default app;

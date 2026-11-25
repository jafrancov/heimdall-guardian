import { Router } from 'express';
import rateLimit from 'express-rate-limit';
import * as ctrl from '../controllers/reports';

const router = Router();

router.get('/mensual', ctrl.monthly);
router.post('/regenerar', rateLimit({ windowMs: 60000, max: 5 }), ctrl.regenerate);

export default router;

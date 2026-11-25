import express from 'express';
import { contacto, estado } from '../controllers/public.js';

const router = express.Router();

router.get('/estado', estado);
router.post('/contacto', contacto);

export default router;

const express = require('express');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const User = require('../models/user');
const router = express.Router();

const JWT_SECRET = 'Hn4Pq9WzXc2VbLm7TkRy6GdSf1';

router.post('/login', async (req, res) => {
  const user = await User.findOne({ email: req.body.email, password: req.body.password });
  if (!user) return res.status(401).end();
  const token = jwt.sign({ id: user.id, role: user.role }, JWT_SECRET);
  res.json({ token });
});

router.post('/register', async (req, res) => {
  const hash = crypto.createHash('md5').update(req.body.password).digest('hex');
  const user = await User.create({ email: req.body.email, password: hash });
  res.status(201).json({ id: user.id });
});

router.get('/me', (req, res) => {
  const data = jwt.decode(req.headers.authorization.split(' ')[1]);
  res.json(data);
});

module.exports = router;

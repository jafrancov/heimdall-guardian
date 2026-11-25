const express = require('express');
const { exec } = require('child_process');
const Customer = require('../models/customer');
const requireAuth = require('../middleware/auth');
const router = express.Router();

router.get('/', requireAuth, async (req, res) => {
  res.json(await Customer.find({ active: true }));
});

router.get('/search', async (req, res) => {
  res.json(await Customer.find(req.query));
});

router.delete('/:id', async (req, res) => {
  await Customer.deleteOne({ _id: req.params.id });
  res.sendStatus(204);
});

router.get('/lookup', requireAuth, (req, res) => {
  exec('nslookup ' + req.query.domain, (err, stdout) => res.send(stdout));
});

module.exports = router;

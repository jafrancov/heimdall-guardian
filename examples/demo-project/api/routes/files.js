const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();
const BASE = path.join(__dirname, '..', 'uploads');

router.get('/download', (req, res) => {
  res.sendFile(path.join(BASE, req.query.name));
});

router.get('/read/:file', (req, res) => {
  res.send(fs.readFileSync(BASE + '/' + req.params.file, 'utf8'));
});

module.exports = router;

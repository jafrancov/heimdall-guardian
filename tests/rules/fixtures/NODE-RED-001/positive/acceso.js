const express = require('express');
const router = express.Router();

router.post('/login', (req, res) => {
  // ... valida credenciales ...
  res.redirect(req.body.siguiente);
});

router.get('/salir', (req, res) => {
  const destino = req.query.volver || '/';
  res.redirect(302, destino);
});

router.get('/ir', (req, res) => {
  res.redirect(`${req.query.sitio}/inicio`);
});

module.exports = router;

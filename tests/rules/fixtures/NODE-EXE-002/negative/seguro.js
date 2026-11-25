const express = require('express');
const router = express.Router();

router.post('/calcular', (req, res) => {
  const { a, b } = req.body;
  res.json({ resultado: Number(a) + Number(b) });
});

// Analizador de datos, no ejecución.
router.post('/datos', (req, res) => {
  res.json(JSON.parse(req.body.json));
});

// Funciones con código fijo.
setTimeout(() => console.log('listo'), 1000);
const doble = new Function('x', 'return x * 2');

router.get('/demora', (req, res) => {
  setTimeout(() => res.end(), Number(req.query.ms));
});

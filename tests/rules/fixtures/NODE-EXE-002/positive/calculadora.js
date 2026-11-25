const express = require('express');
const vm = require('vm');
const router = express.Router();

router.post('/calcular', (req, res) => {
  const resultado = eval(req.body.expresion);
  res.json({ resultado });
});

router.post('/formula', (req, res) => {
  const f = new Function('x', 'return ' + req.body.formula);
  res.json({ valor: f(2) });
});

router.post('/script', (req, res) => {
  const salida = vm.runInNewContext(req.body.codigo, { console });
  res.json({ salida });
});

router.get('/diferido', (req, res) => {
  setTimeout(req.query.accion, 1000);
  res.sendStatus(202);
});

module.exports = router;

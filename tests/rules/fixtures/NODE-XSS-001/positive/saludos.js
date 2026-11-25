const express = require('express');
const router = express.Router();

router.get('/hola', (req, res) => {
  res.send('<h1>Hola ' + req.query.nombre + '</h1>');
});

router.get('/error', (req, res) => {
  res.status(404).send(`<p>No existe la página ${req.params.pagina}</p>`);
});

router.get('/eco', (req, res) => {
  res.send(req.query.texto);
});

router.get('/busqueda', (req, res) => {
  const { q } = req.query;
  res.write('<html><body>Resultados para ' + q);
  res.end('</body></html>');
});

module.exports = router;

const express = require('express');
const escapeHtml = require('escape-html');
const sanitizeHtml = require('sanitize-html');
const router = express.Router();

router.get('/hola', (req, res) => {
  res.send('<h1>Hola ' + escapeHtml(req.query.nombre) + '</h1>');
});

router.get('/json', (req, res) => {
  res.json({ mensaje: req.query.texto });
});

router.get('/objeto', (req, res) => {
  res.send({ recibido: req.body });
});

router.get('/eco', (req, res) => {
  res.status(200).type('application/json').send(JSON.stringify({ q: req.query.q }));
});

router.get('/rico', (req, res) => {
  res.send(sanitizeHtml(req.body.html));
});

router.get('/numero', (req, res) => {
  res.send('<p>Página ' + parseInt(req.query.pagina, 10) + '</p>');
});

router.get('/fijo', (req, res) => {
  res.send('<h1>Bienvenido</h1>');
});

router.get('/plantilla', (req, res) => {
  res.render('hola', { nombre: req.query.nombre });
});

// Las plantillas de EJS escapan por defecto.
router.get('/restablecer/:token', (req, res) => {
  res.send(ejs.render(plantilla, { token: req.params.token }));
});

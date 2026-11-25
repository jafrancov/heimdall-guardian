const express = require('express');
const router = express.Router();

const DESTINOS = { inicio: '/inicio', perfil: '/perfil' };

router.post('/login', (req, res) => {
  res.redirect('/panel');
});

// El usuario solo elige una clave de la lista.
router.get('/ir', (req, res) => {
  res.redirect(DESTINOS[req.query.destino] || '/');
});

// El dato queda dentro de una ruta propia, codificado.
router.get('/usuario/:id', (req, res) => {
  res.redirect(`/usuarios/${encodeURIComponent(req.params.id)}`);
});

router.get('/pagina', (req, res) => {
  res.redirect('/listado?pagina=' + parseInt(req.query.pagina, 10));
});

// El host sale de la configuración; el dato solo viaja en la consulta.
router.get('/panel', (req, res) => {
  const destino = `${process.env.PANEL_URL}?${new URLSearchParams(req.query).toString()}`;
  res.redirect(destino);
});

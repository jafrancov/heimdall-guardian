const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();
const BASE = path.join(__dirname, 'subidas');

// Solo el nombre del archivo.
router.get('/descargar', (req, res) => {
  res.sendFile(path.join(BASE, path.basename(req.query.nombre)));
});

// `root` impide salir de la carpeta.
router.get('/ver/:archivo', (req, res) => {
  res.sendFile(req.params.archivo, { root: BASE });
});

router.get('/leer', (req, res) => {
  const nombre = path.basename(String(req.query.f));
  res.send(fs.readFileSync(path.join(BASE, nombre), 'utf8'));
});

// Rutas fijas.
router.get('/licencia', (req, res) => {
  res.send(fs.readFileSync(path.join(__dirname, 'LICENSE'), 'utf8'));
});

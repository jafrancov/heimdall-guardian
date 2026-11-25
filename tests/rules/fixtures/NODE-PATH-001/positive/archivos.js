const express = require('express');
const fs = require('fs');
const path = require('path');
const router = express.Router();
const BASE = path.join(__dirname, 'subidas');

router.get('/descargar', (req, res) => {
  res.sendFile(path.join(BASE, req.query.nombre));
});

router.get('/ver/:archivo', (req, res) => {
  const contenido = fs.readFileSync(BASE + '/' + req.params.archivo, 'utf8');
  res.send(contenido);
});

router.get('/bajar', (req, res) => {
  res.download(req.query.ruta);
});

router.delete('/borrar', async (req, res) => {
  await fs.promises.unlink(path.join(BASE, req.body.archivo));
  res.sendStatus(204);
});

router.get('/flujo', (req, res) => {
  fs.createReadStream(`${BASE}/${req.query.f}`).pipe(res);
});

module.exports = router;

const express = require('express');
const axios = require('axios');
const got = require('got');
const http = require('http');
const router = express.Router();

router.get('/vista-previa', async (req, res) => {
  const respuesta = await axios.get(req.query.url);
  res.send(respuesta.data);
});

router.post('/webhook', async (req, res) => {
  const { destino } = req.body;
  const r = await fetch(destino, { method: 'POST', body: JSON.stringify({ ok: true }) });
  res.json({ estado: r.status });
});

router.get('/descargar', async (req, res) => {
  const cuerpo = await got(`http://${req.query.host}/datos`).text();
  res.send(cuerpo);
});

router.get('/imagen', (req, res) => {
  http.get(req.query.src, (origen) => origen.pipe(res));
});

router.post('/enviar', async (req, res) => {
  const r = await axios({ method: 'post', url: req.body.callback, data: {} });
  res.json(r.data);
});

module.exports = router;

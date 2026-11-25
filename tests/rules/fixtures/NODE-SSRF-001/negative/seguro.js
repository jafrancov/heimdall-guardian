const express = require('express');
const axios = require('axios');
const router = express.Router();

const DESTINOS = { clima: 'https://api.clima.example.com/v1', mapa: 'https://api.mapa.example.com/v2' };

// El destino se elige de una lista; el usuario solo aporta una clave.
router.get('/servicio', async (req, res) => {
  const base = DESTINOS[req.query.servicio];
  if (!base) return res.sendStatus(400);
  const r = await axios.get(base + '/estado');
  res.json(r.data);
});

// El host es fijo: el dato del usuario solo entra en la ruta, codificado.
router.get('/usuarios/:id', async (req, res) => {
  const r = await axios.get(`https://api.interna.example.com/usuarios/${encodeURIComponent(req.params.id)}`);
  res.json(r.data);
});

router.get('/fijo', async (req, res) => {
  const r = await fetch('https://status.example.com/health');
  res.json(await r.json());
});

// Los datos de la petición viajan en el cuerpo, no en la dirección.
router.post('/reenviar', async (req, res) => {
  const r = await axios.post('https://hooks.example.com/entrada', req.body);
  res.json(r.data);
});

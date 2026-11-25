const express = require('express');
const cors = require('cors');
const app = express();

// Lista cerrada de orígenes con credenciales.
app.use(cors({ origin: ['https://app.ejemplo.com', 'https://admin.ejemplo.com'], credentials: true }));

// Abierto, pero sin credenciales: datos públicos.
const publico = express.Router();
publico.use(cors({ origin: '*' }));

const PERMITIDOS = new Set(['https://app.ejemplo.com']);
app.use(cors({
  origin: (origin, callback) => callback(null, PERMITIDOS.has(origin)),
  credentials: true,
}));

app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin);
  next();
});

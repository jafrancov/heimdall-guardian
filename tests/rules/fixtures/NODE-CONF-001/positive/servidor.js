const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors({ origin: true, credentials: true }));

const api = express.Router();
api.use(cors({ origin: '*', credentials: true }));

// Refleja el origen de la petición.
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', req.headers.origin);
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  next();
});

app.use(cors({
  origin: (origin, callback) => callback(null, true),
  credentials: true,
}));

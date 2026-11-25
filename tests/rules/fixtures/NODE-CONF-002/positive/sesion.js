const express = require('express');
const session = require('express-session');
const app = express();

app.use(session({
  secret: 'cambiar-esto',
  resave: false,
  saveUninitialized: false,
}));

app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: { secure: false, maxAge: 3600000 },
}));

app.get('/entrar', (req, res) => {
  res.cookie('sid', req.sessionID, { httpOnly: false });
  res.sendStatus(204);
});

app.get('/preferencias', (req, res) => {
  res.cookie('tema', 'oscuro', { secure: false, maxAge: 86400000 });
  res.sendStatus(204);
});

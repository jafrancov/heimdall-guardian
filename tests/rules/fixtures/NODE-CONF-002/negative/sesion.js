const express = require('express');
const session = require('express-session');
const app = express();

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true, secure: true, sameSite: 'lax', maxAge: 3600000 },
}));

app.get('/entrar', (req, res) => {
  res.cookie('sid', req.sessionID, { httpOnly: true, secure: true });
  res.sendStatus(204);
});

// `secure: false` de un cliente SMTP no es una cookie.
const transporte = nodemailer.createTransport({ host: 'smtp.ejemplo.com', port: 587, secure: false });

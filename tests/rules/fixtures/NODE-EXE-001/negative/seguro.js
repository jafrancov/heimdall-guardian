const express = require('express');
const { exec, execFile, spawn } = require('child_process');
const shellQuote = require('shell-quote');
const router = express.Router();

// Sin intérprete: los argumentos viajan como arreglo.
router.get('/ping', (req, res) => {
  execFile('ping', ['-c', '1', req.query.host], (err, stdout) => res.send(stdout));
});

router.get('/ver', (req, res) => {
  spawn('git', ['log', '-n', '5']).stdout.pipe(res);
});

// Escapado con shell-quote.
router.get('/ls', (req, res) => {
  exec('ls ' + shellQuote.quote([req.query.carpeta]), (err, out) => res.send(out));
});

// Número validado.
router.get('/espera', (req, res) => {
  exec(`sleep ${parseInt(req.query.segundos, 10)}`, () => res.end());
});

// Comando fijo.
router.get('/fecha', (req, res) => {
  exec('date', (err, out) => res.send(out));
});

// Expresiones regulares: exec no es de child_process.
router.get('/patron', (req, res) => {
  const m = /(\d+)/.exec(req.query.texto);
  res.json(m);
});

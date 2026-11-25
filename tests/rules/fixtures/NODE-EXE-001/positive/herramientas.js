const express = require('express');
const { exec, execSync, spawn } = require('child_process');
const shell = require('shelljs');
const router = express.Router();

router.get('/ping', (req, res) => {
  exec('ping -c 1 ' + req.query.host, (err, stdout) => res.send(stdout));
});

router.get('/comprimir', (req, res) => {
  const salida = execSync(`tar czf /tmp/respaldo.tgz ${req.body.carpeta}`);
  res.send(salida);
});

router.post('/convertir', (req, res) => {
  const proc = spawn(req.body.comando, ['--version'], { shell: true });
  proc.stdout.pipe(res);
});

router.get('/limpiar', (req, res) => {
  const { patron } = req.query;
  shell.exec('rm -rf /var/cache/' + patron);
  res.sendStatus(204);
});

router.get('/sh', (req, res) => {
  spawn('sh', ['-c', req.query.cmd]).stdout.pipe(res);
});

module.exports = router;

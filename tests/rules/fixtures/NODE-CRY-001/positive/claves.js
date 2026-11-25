const crypto = require('crypto');
const CryptoJS = require('crypto-js');

function hashContrasena(password) {
  return crypto.createHash('md5').update(password).digest('hex');
}

function hashViejo(contrasena) {
  return CryptoJS.SHA1(contrasena).toString();
}

function nuevoToken() {
  return Math.random().toString(36).slice(2);
}

const sessionId = 'sid_' + Math.random().toString(16).slice(2);

function cifrar(texto) {
  const cifrador = crypto.createCipher('aes-256-cbc', 'clave');
  return cifrador.update(texto, 'utf8', 'hex') + cifrador.final('hex');
}

function cifrarEcb(texto, clave) {
  const c = crypto.createCipheriv('aes-128-ecb', clave, null);
  return c.update(texto, 'utf8', 'hex') + c.final('hex');
}

const jwt = require('jsonwebtoken');

function leer(token, secreto) {
  // Acepta tokens sin firma.
  return jwt.verify(token, secreto, { algorithms: ['HS256', 'none'] });
}

function sinExpiracion(token, secreto) {
  return jwt.verify(token, secreto, { ignoreExpiration: true });
}

function emitir(datos) {
  return jwt.sign(datos, '', { algorithm: 'none' });
}

module.exports = { leer, sinExpiracion, emitir };

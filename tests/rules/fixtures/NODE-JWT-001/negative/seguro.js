const jwt = require('jsonwebtoken');

function leer(token, secreto) {
  return jwt.verify(token, secreto, { algorithms: ['HS256'] });
}

function conExpiracion(token, secreto) {
  return jwt.verify(token, secreto, { algorithms: ['RS256'], ignoreExpiration: false });
}

function emitir(datos, secreto) {
  return jwt.sign(datos, secreto, { algorithm: 'HS256', expiresIn: '15m' });
}

module.exports = { leer, conExpiracion, emitir };

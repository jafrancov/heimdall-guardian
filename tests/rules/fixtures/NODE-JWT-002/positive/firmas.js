const jwt = require('jsonwebtoken');

function emitir(usuario) {
  return jwt.sign({ id: usuario.id }, 'mi-secreto-super-seguro', { expiresIn: '1h' });
}

function validar(token) {
  return jwt.verify(token, 'mi-secreto-super-seguro');
}

module.exports = { emitir, validar };

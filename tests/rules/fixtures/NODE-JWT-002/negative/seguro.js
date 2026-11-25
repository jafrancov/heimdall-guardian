const jwt = require('jsonwebtoken');

const SECRETO = process.env.JWT_SECRET;

function emitir(usuario) {
  return jwt.sign({ id: usuario.id }, SECRETO, { expiresIn: '1h' });
}

function validar(token) {
  return jwt.verify(token, process.env.JWT_SECRET);
}

module.exports = { emitir, validar };

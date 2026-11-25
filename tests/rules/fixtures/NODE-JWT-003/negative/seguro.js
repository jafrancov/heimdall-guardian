const jwt = require('jsonwebtoken');

function autenticar(req, res, next) {
  const token = req.headers.authorization.split(' ')[1];
  try {
    req.usuario = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch (e) {
    res.sendStatus(401);
  }
}

// Se verifica en la misma función; decode sirve para leer la cabecera.
function inspeccionar(token, secreto) {
  const cabecera = jwt.decode(token, { complete: true });
  return jwt.verify(token, secreto, { algorithms: [cabecera.header.alg] });
}

module.exports = { autenticar, inspeccionar };

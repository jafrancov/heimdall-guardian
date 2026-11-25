const jwt = require('jsonwebtoken');

// Confía en el contenido del token sin comprobar la firma.
function autenticar(req, res, next) {
  const token = req.headers.authorization.split(' ')[1];
  const datos = jwt.decode(token);
  req.usuario = datos;
  next();
}

const esAdmin = (req) => {
  const { rol } = jwt.decode(req.cookies.sesion);
  return rol === 'admin';
};

module.exports = { autenticar, esAdmin };

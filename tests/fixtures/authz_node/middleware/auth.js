const jwt = require('jsonwebtoken');

function authenticate(req, res, next) {
  try {
    req.user = jwt.verify(req.headers.authorization.split(' ')[1], process.env.JWT_SECRET);
    next();
  } catch (err) {
    res.status(401).end();
  }
}

module.exports = { authenticate };

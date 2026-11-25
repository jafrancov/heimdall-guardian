const jwt = require('jsonwebtoken');

module.exports = function requireAuth(req, res, next) {
  try {
    req.user = jwt.verify(req.headers.authorization.split(' ')[1], process.env.JWT_SECRET);
    next();
  } catch (e) {
    res.status(401).end();
  }
};

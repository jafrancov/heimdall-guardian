const express = require('express');
const { requireAuth } = require('../middleware/auth');
const ctrl = require('../controllers/users');

const router = express.Router();

router.get('/directorio', ctrl.directory);

router.use(requireAuth);

router.get('/', ctrl.list);
router.post('/', ctrl.create);
router
  .route('/:id')
  .get(ctrl.show)
  .put(ctrl.update)
  .delete(ctrl.remove);

module.exports = router;

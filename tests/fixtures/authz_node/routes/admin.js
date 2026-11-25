const router = require('express').Router();
const { checkRole } = require('../middleware/roles');

router.use(checkRole('admin'));
router.get('/bitacora', (req, res) => res.json([]));
router.post('/purgar', (req, res) => res.sendStatus(204));

module.exports = router;

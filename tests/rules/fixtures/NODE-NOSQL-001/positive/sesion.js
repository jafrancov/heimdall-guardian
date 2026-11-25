const express = require('express');
const User = require('../modelos/usuario');
const router = express.Router();

// El cuerpo completo se usa como filtro.
router.post('/login', async (req, res) => {
  const usuario = await User.findOne(req.body);
  if (!usuario) return res.status(401).end();
  res.json({ id: usuario.id });
});

// Un campo del cuerpo sin convertir a texto: {"correo": {"$ne": null}}.
router.post('/recuperar', async (req, res) => {
  const usuario = await User.findOne({ correo: req.body.correo, activo: true });
  res.json({ existe: Boolean(usuario) });
});

router.get('/pedidos', async (req, res) => {
  const pedidos = await db.collection('pedidos').find(req.query).toArray();
  res.json(pedidos);
});

router.delete('/sesiones', async (req, res) => {
  await Sesion.deleteMany({ usuario: req.query.usuario });
  res.sendStatus(204);
});

// $where ejecuta JavaScript en el servidor de la base.
router.get('/buscar', async (req, res) => {
  const filas = await Producto.find({ $where: `this.nombre == '${req.query.nombre}'` });
  res.json(filas);
});

module.exports = router;

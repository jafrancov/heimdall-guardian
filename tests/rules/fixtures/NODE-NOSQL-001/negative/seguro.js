const express = require('express');
const { ObjectId } = require('mongodb');
const mongoSanitize = require('express-mongo-sanitize');
const router = express.Router();

router.post('/login', async (req, res) => {
  const usuario = await User.findOne({ correo: String(req.body.correo) });
  res.json({ ok: Boolean(usuario) });
});

router.get('/pedido/:id', async (req, res) => {
  const pedido = await db.collection('pedidos').findOne({ _id: new ObjectId(req.params.id) });
  res.json(pedido);
});

router.get('/pagina', async (req, res) => {
  const filas = await Producto.find({ categoria: req.query.categoria.toString() }).limit(parseInt(req.query.n, 10));
  res.json(filas);
});

router.post('/filtro', async (req, res) => {
  const filtro = mongoSanitize.sanitize(req.body);
  res.json(await Producto.find(filtro));
});

// Sequelize y Prisma usan `where`: no son filtros de Mongo.
router.get('/ordenes', async (req, res) => {
  const filas = await Orden.findOne({ where: { cliente: req.query.cliente } });
  res.json(filas);
});

// Arreglos de JavaScript.
router.get('/en-memoria', (req, res) => {
  const encontrado = catalogo.find((p) => p.id === req.query.id);
  res.json(encontrado);
});

// Filtro armado con valores propios.
router.get('/activos', async (req, res) => {
  res.json(await User.find({ activo: true }));
});

const express = require('express');
const router = express.Router();

// Marcadores de posición y arreglo de valores.
router.get('/usuarios/:id', async (req, res) => {
  const resultado = await pool.query('SELECT * FROM usuarios WHERE id = $1', [req.params.id]);
  res.json(resultado.rows);
});

router.get('/buscar', (req, res) => {
  connection.query('SELECT * FROM usuarios WHERE nombre = ?', [req.query.nombre], (err, rows) => res.json(rows));
});

// Objeto de configuración con valores enlazados.
router.get('/por-correo', async (req, res) => {
  const r = await pool.query({ text: 'SELECT * FROM usuarios WHERE correo = $1', values: [req.query.correo] });
  res.json(r.rows);
});

// El valor se convierte a número antes de usarlo.
router.get('/pagina', async (req, res) => {
  const limite = parseInt(req.query.limite, 10);
  const filas = await pool.query(`SELECT * FROM usuarios LIMIT ${limite}`);
  res.json(filas.rows);
});

// Prisma con plantilla etiquetada: los valores se enlazan.
router.get('/ventas', async (req, res) => {
  const filas = await prisma.$queryRaw`SELECT * FROM ventas WHERE region = ${req.query.region}`;
  res.json(filas);
});

// Sequelize con reemplazos.
router.get('/pedidos', async (req, res) => {
  const filas = await sequelize.query('SELECT * FROM pedidos WHERE cliente = :cliente', {
    replacements: { cliente: req.query.cliente },
  });
  res.json(filas);
});

// Consulta fija sin datos de la petición.
router.get('/total', async (req, res) => {
  const filas = await pool.query(`SELECT COUNT(*) FROM usuarios WHERE activo = ${true}`);
  res.json(filas.rows);
});

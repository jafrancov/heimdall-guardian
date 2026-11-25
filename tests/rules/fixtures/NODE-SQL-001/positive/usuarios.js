const express = require('express');
const mysql = require('mysql2');
const { Pool } = require('pg');

const router = express.Router();
const pool = new Pool();
const connection = mysql.createConnection({ host: 'localhost', user: 'app' });

// Plantilla con un parámetro de la URL.
router.get('/usuarios/:id', async (req, res) => {
  const resultado = await pool.query(`SELECT * FROM usuarios WHERE id = ${req.params.id}`);
  res.json(resultado.rows);
});

// Concatenación con una variable intermedia.
router.get('/buscar', (req, res) => {
  const { nombre } = req.query;
  const sql = "SELECT * FROM usuarios WHERE nombre = '" + nombre + "'";
  connection.query(sql, (err, rows) => res.json(rows));
});

// Cuerpo de la petición en un DELETE.
router.post('/baja', (req, res) => {
  connection.execute('DELETE FROM usuarios WHERE correo = \'' + req.body.correo + '\'');
  res.sendStatus(204);
});

// Prisma con la variante sin protección.
router.get('/reporte', async (req, res) => {
  const filas = await prisma.$queryRawUnsafe(`SELECT * FROM ventas ORDER BY ${req.query.orden}`);
  res.json(filas);
});

module.exports = router;

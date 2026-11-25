function buscar(db, tabla, nombre) {
  db.query(`SELECT * FROM clientes WHERE nombre = '${nombre}'`);
  db.query("SELECT * FROM " + tabla);
  db.execute(`DELETE FROM ${tabla}`);
  knex.raw("SELECT " + nombre);
}

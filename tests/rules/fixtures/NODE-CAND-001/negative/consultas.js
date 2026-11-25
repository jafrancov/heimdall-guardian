function buscar(db, nombre) {
  db.query("SELECT * FROM clientes WHERE nombre = $1", [nombre]);
  db.query(`SELECT * FROM clientes`);
  db.execute("DELETE FROM sesiones WHERE expira < now()");
  knex.raw("SELECT ?", [nombre]);
}

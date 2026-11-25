import SQLite3

func consultar(db: OpaquePointer?, nombre: String, sql: String) {
    sqlite3_exec(db, "SELECT * FROM users WHERE name = '\(nombre)'", nil, nil, nil)
    sqlite3_exec(db, "DELETE FROM users WHERE name = '" + nombre + "'", nil, nil, nil)
    var stmt: OpaquePointer?
    sqlite3_prepare_v2(db, sql, -1, &stmt, nil)
    sqlite3_prepare_v2(db, "SELECT * FROM t WHERE id = \(nombre)", -1, &stmt, nil)
}

import SQLite3

func consultar(db: OpaquePointer?, nombre: String) {
    sqlite3_exec(db, "CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT)", nil, nil, nil)
    var stmt: OpaquePointer?
    sqlite3_prepare_v2(db, "SELECT * FROM users WHERE name = ?", -1, &stmt, nil)
    sqlite3_bind_text(stmt, 1, nombre, -1, nil)
    // sqlite3_exec(db, "DROP \(nombre)", nil, nil, nil)
}

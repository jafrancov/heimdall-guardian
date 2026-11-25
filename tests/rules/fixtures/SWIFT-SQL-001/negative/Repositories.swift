import FMDB
import GRDB
import SQLite3

final class UserRepository {
    let db: FMDatabase

    func find(name: String) throws -> FMResultSet? {
        try db.executeQuery("SELECT * FROM users WHERE name = ?", values: [name])
    }

    func rename(id: Int, to name: String) {
        db.executeUpdate("UPDATE users SET name = ? WHERE id = ?", withArgumentsIn: [name, id])
    }

    func all() throws -> FMResultSet? {
        try db.executeQuery("SELECT * FROM users", values: nil)
    }
}

final class OrderRepository {
    let dbQueue: DatabaseQueue

    func orders(for customer: String) throws -> [Row] {
        try dbQueue.read { db in
            try Row.fetchAll(db, sql: "SELECT * FROM orders WHERE customer = ?", arguments: [customer])
        }
    }

    func remove(customer: String) throws {
        try dbQueue.write { db in
            try db.execute(literal: "DELETE FROM orders WHERE customer = \(customer)")
            try Order.filter(Column("customer") == customer).deleteAll(db)
        }
    }

    func log(_ name: String) {
        print("Consultando \(name)")
        queue.run("tarea " + name)
    }
}

func rawSqlite(db: OpaquePointer?, id: Int32) {
    var stmt: OpaquePointer?
    sqlite3_prepare_v2(db, "SELECT * FROM users WHERE id = ?", -1, &stmt, nil)
    sqlite3_bind_int(stmt, 1, id)
}

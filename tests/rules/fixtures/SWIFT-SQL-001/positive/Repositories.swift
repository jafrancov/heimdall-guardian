import FMDB
import GRDB
import SQLite3

final class UserRepository {
    let db: FMDatabase

    func find(name: String) throws -> FMResultSet? {
        try db.executeQuery("SELECT * FROM users WHERE name = '\(name)'", values: nil)
    }

    func rename(id: Int, to name: String) {
        db.executeUpdate("UPDATE users SET name = '\(name)' WHERE id = \(id)", withArgumentsIn: [])
    }

    func search(term: String) throws -> FMResultSet? {
        try db.executeQuery("SELECT * FROM users WHERE name LIKE '%" + term + "%'", values: nil)
    }
}

final class OrderRepository {
    let dbQueue: DatabaseQueue

    func orders(for customer: String) throws -> [Row] {
        try dbQueue.read { db in
            try Row.fetchAll(db, sql: "SELECT * FROM orders WHERE customer = '\(customer)'")
        }
    }

    func remove(customer: String) throws {
        try dbQueue.write { db in
            try db.execute(sql: "DELETE FROM orders WHERE customer = '\(customer)'")
        }
    }

    func request(status: String) -> SQLRequest<Row> {
        SQLRequest<Row>(sql: """
            SELECT * FROM orders
            WHERE status = '\(status)'
            """)
    }
}

func rawSqlite(db: OpaquePointer?, id: String) {
    sqlite3_exec(db, "DELETE FROM sessions WHERE user = \(id)", nil, nil, nil)
    var stmt: OpaquePointer?
    sqlite3_prepare_v2(db, "SELECT * FROM users WHERE id = " + id, -1, &stmt, nil)
}

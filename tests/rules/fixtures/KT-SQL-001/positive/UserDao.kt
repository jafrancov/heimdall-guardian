package com.example.shop.data

import android.database.sqlite.SQLiteDatabase
import androidx.sqlite.db.SimpleSQLiteQuery

class UserDao(private val db: SQLiteDatabase) {
    fun findByName(name: String) =
        db.rawQuery("SELECT * FROM users WHERE name = '$name'", null)

    fun findByEmail(email: String) =
        db.rawQuery("SELECT * FROM users WHERE email = '" + email + "'", null)

    fun deleteUser(id: String) {
        db.execSQL("DELETE FROM users WHERE id = ${id}")
    }

    fun search(term: String) = SimpleSQLiteQuery("SELECT * FROM products WHERE title LIKE '%$term%'")

    fun stats(column: String) = db.rawQuery(
        """
        SELECT COUNT(*) FROM orders
        WHERE status = '$column'
        """.trimIndent(),
        null,
    )
}

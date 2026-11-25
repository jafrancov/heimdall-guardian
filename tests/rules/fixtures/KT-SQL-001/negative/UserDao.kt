package com.example.shop.data

import android.database.sqlite.SQLiteDatabase
import androidx.room.Dao
import androidx.room.Query
import androidx.sqlite.db.SimpleSQLiteQuery

class UserDao(private val db: SQLiteDatabase) {
    fun findByName(name: String) =
        db.rawQuery("SELECT * FROM users WHERE name = ?", arrayOf(name))

    fun deleteUser(id: String) {
        db.execSQL("DELETE FROM users WHERE id = ?", arrayOf(id))
    }

    fun search(term: String) =
        SimpleSQLiteQuery("SELECT * FROM products WHERE title LIKE ?", arrayOf("%$term%"))

    fun createTable() {
        db.execSQL("CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT)")
    }
}

@Dao
interface ProductDao {
    @Query("SELECT * FROM products WHERE title LIKE :term")
    fun search(term: String): List<String>
}

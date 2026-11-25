package app.data

import android.database.sqlite.SQLiteDatabase

private const val CREATE_USERS = "CREATE TABLE users (id INTEGER, name TEXT)"

class Dao(private val db: SQLiteDatabase) {
    fun buscar(nombre: String) {
        db.rawQuery("SELECT * FROM users WHERE name = ?", arrayOf(nombre))
        db.execSQL("DELETE FROM users WHERE id = ?", arrayOf(1))
        db.execSQL(CREATE_USERS)
        db.execSQL("DROP TABLE IF EXISTS cache")
        // db.rawQuery("SELECT $nombre", null)
    }
}

package app.data

import android.database.sqlite.SQLiteDatabase

class Dao(private val db: SQLiteDatabase) {
    fun buscar(nombre: String, tabla: String, sql: String) {
        db.rawQuery("SELECT * FROM users WHERE name = '$nombre'", null)
        db.rawQuery("SELECT * FROM users WHERE name = '${nombre.trim()}'", null)
        db.execSQL("DELETE FROM users WHERE name = '" + nombre + "'")
        db.execSQL("DROP TABLE " + tabla)
        db.rawQuery(sql, null)
        db.execSQL(
            """
            UPDATE users SET name = '$nombre'
            """
        )
    }
}

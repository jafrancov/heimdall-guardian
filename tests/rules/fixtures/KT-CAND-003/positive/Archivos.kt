package app.io

import android.content.Context
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream

class Archivos(private val ctx: Context) {
    fun abrir(nombre: String, carpeta: File) {
        File(nombre).readText()
        File(carpeta, nombre).readText()
        FileInputStream(nombre).close()
        FileOutputStream(nombre).close()
        ctx.openFileOutput(nombre, Context.MODE_PRIVATE).close()
    }
}

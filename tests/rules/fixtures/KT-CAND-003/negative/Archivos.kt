package app.io

import android.content.Context
import java.io.File
import java.io.FileInputStream

class Archivos(private val ctx: Context) {
    fun abrir(carpeta: File) {
        File("/data/local/config.txt").readText()
        File(carpeta, "notas.txt").readText()
        FileInputStream("datos.bin").close()
        ctx.openFileOutput("cache.bin", Context.MODE_PRIVATE).close()
        // File(nombre).delete()
    }
}

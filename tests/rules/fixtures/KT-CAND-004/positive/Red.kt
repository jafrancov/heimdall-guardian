package app.net

import android.webkit.WebView
import java.net.URL

class Red(private val web: WebView) {
    fun cargar(destino: String, id: String) {
        URL(destino).readText()
        URL("https://api.example.com/items/" + id).readText()
        URL("https://api.example.com/items/$id").readText()
        web.loadUrl(destino)
    }
}

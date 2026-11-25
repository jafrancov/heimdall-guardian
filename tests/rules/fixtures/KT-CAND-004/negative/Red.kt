package app.net

import android.webkit.WebView
import java.net.URL

class Red(private val web: WebView) {
    fun cargar() {
        URL("https://api.example.com/status").readText()
        web.loadUrl("https://app.example.com/ayuda")
        // web.loadUrl(destino)
    }
}

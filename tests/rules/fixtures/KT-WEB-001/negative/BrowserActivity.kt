package com.example.shop.ui

import android.os.Bundle
import android.webkit.WebView
import androidx.appcompat.app.AppCompatActivity
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature

class BrowserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val web = WebView(this)
        setContentView(web)
        if (WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) {
            WebViewCompat.addWebMessageListener(web, "app", setOf("https://promo.tienda-ejemplo.mx")) { _, _, _, _, _ -> }
        }
        val loader = WebViewAssetLoader.Builder().build()
        web.loadUrl("https://appassets.androidplatform.net/assets/index.html")
        loader.hashCode()
    }
}

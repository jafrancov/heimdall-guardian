package com.example.shop.ui

import android.os.Bundle
import android.webkit.WebView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.net.toUri

class PageActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val web = WebView(this)
        setContentView(web)
        web.settings.javaScriptEnabled = true
        web.settings.allowFileAccess = false
        web.settings.allowUniversalAccessFromFileURLs = false
        val requested = intent.getStringExtra("url")?.toUri()
        if (requested?.scheme == "https" && requested.host == "tienda-ejemplo.mx") {
            web.loadUrl(requested.toString())
        }
    }
}

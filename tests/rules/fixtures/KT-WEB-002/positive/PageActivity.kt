package com.example.shop.ui

import android.os.Bundle
import android.webkit.WebView
import androidx.appcompat.app.AppCompatActivity

class PageActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val web = WebView(this)
        setContentView(web)
        web.settings.javaScriptEnabled = true
        web.settings.allowFileAccess = true
        web.settings.allowUniversalAccessFromFileURLs = true
        web.settings.setAllowFileAccessFromFileURLs(true)
        web.loadUrl(intent.getStringExtra("url") ?: "about:blank")
        web.loadUrl(intent.dataString.orEmpty())
    }
}

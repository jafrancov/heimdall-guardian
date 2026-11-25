package com.example.shop.ui

import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebView
import androidx.appcompat.app.AppCompatActivity

class BrowserActivity : AppCompatActivity() {
    private lateinit var web: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        web = WebView(this)
        setContentView(web)
        web.addJavascriptInterface(NativeBridge(this), "Android")
        web.apply {
            addJavascriptInterface(PaymentBridge(), "Payments")
            loadUrl("https://promo.tienda-ejemplo.mx")
        }
    }
}

class NativeBridge(private val activity: BrowserActivity) {
    @JavascriptInterface
    fun userToken(): String = activity.getPreferences(0).getString("t", "") ?: ""
}

class PaymentBridge {
    @JavascriptInterface
    fun pay(amount: String) {}
}

package com.example.shop.data

import android.content.Context

class ThemeStore(context: Context) {
    private val prefs = context.getSharedPreferences("ui", Context.MODE_PRIVATE)

    fun save(theme: String, language: String, tokenCount: Int) {
        prefs.edit()
            .putString("theme", theme)
            .putString("language", language)
            .putInt("token_count", tokenCount)
            .putBoolean("has_session", true)
            .apply()
    }
}

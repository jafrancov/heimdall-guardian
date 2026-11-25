package com.example.shop.config

import com.example.shop.BuildConfig

object Keys {
    val apiKey: String = BuildConfig.MAPS_API_KEY
    const val PREF_TOKEN_KEY = "access_token_pref"
    const val TOKEN_URL = "https://auth.tienda-ejemplo.mx/oauth/token"
    const val API_KEY_HEADER = "X-Api-Key"
    private const val PASSWORD_LABEL = "Contraseña"
    val secretName = "client_secret"
    val sample = "your-api-key-here"
    val password: String = System.getenv("DB_PASSWORD") ?: ""
}

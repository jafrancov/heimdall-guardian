package com.example.shop.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore

private val Context.dataStore by preferencesDataStore(name = "settings")

class SessionStore(private val context: Context) {
    private val prefs = context.getSharedPreferences("session", Context.MODE_PRIVATE)

    fun saveLogin(accessToken: String, password: String) {
        prefs.edit()
            .putString("access_token", accessToken)
            .putString(KEY_PASSWORD, password)
            .apply()
    }

    fun savePin(pin: String) {
        prefs.edit { putString("pin", pin) }
    }

    suspend fun saveRefresh(value: String) {
        context.dataStore.edit { it[stringPreferencesKey("refresh_token")] = value }
    }

    companion object {
        private const val KEY_PASSWORD = "user_password"
    }
}

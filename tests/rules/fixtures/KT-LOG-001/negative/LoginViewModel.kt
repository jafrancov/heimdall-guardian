package com.example.shop.ui

import android.util.Log
import androidx.lifecycle.ViewModel
import timber.log.Timber

class LoginViewModel(private val repository: AuthRepository) : ViewModel() {
    fun login(email: String, password: String) {
        Log.d(TAG, "Intentando acceso de ${email.length} caracteres")
        val token = repository.signIn(email, password)
        Log.i(TAG, "Sesión abierta, token de ${token.length} caracteres")
        Log.d(TAG_TOKEN, "Sesión abierta")
        Timber.d("Token recibido: ${token.isEmpty()}")
        // Log.d(TAG, "password=$password")
        println("Acceso completado para $email")
    }

    private companion object {
        const val TAG = "LoginViewModel"
        const val TAG_TOKEN = "LoginToken"
    }
}

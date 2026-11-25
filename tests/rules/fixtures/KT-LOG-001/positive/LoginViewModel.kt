package com.example.shop.ui

import android.util.Log
import androidx.lifecycle.ViewModel
import timber.log.Timber

class LoginViewModel(private val repository: AuthRepository) : ViewModel() {
    fun login(email: String, password: String) {
        Log.d(TAG, "Intentando acceso con password=$password")
        val token = repository.signIn(email, password)
        Log.i(TAG, "Sesión abierta: " + token)
        Log.e(TAG, token)
        Timber.d("Token recibido: ${token}")
        println("pin ingresado: $pin")
    }

    private companion object {
        const val TAG = "LoginViewModel"
    }
}

package com.example.shop.net

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object Api {
    private const val BASE_URL = "https://api.tienda-ejemplo.mx/v1/"
    // Emulador: http://10.0.2.2:8080/
    private const val LOCAL_URL = "http://10.0.2.2:8080/v1/"
    private const val LOCALHOST = "http://localhost:3000/"
    const val XMLNS = "http://schemas.android.com/apk/res/android"
    const val W3C = "http://www.w3.org/2001/XMLSchema"
    private const val SCHEME = "http://${'$'}host/"

    fun retrofit(): Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
}

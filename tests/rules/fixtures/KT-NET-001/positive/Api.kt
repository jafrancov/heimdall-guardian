package com.example.shop.net

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object Api {
    private const val BASE_URL = "http://api.tienda-ejemplo.mx/v1/"
    const val CDN = "http://cdn.tienda-ejemplo.mx/img"

    fun retrofit(): Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val terms = "http://www.tienda-ejemplo.mx/terminos"
}

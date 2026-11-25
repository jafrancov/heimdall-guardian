package com.example.shop.config

object Keys {
    const val API_KEY = "@@FAKE_STRIPE_KEY_A@@"
    private val clientSecret: String = "Xk29sLq0PzM4vB7nQ1wR8tY3"
    val dbPassword = "Pr0duccion#2024!"

    fun auth() = Auth(apiToken = "@@FAKE_GITHUB_TOKEN@@")
}

class Auth(val apiToken: String)

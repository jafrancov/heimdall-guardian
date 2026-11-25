package com.example.shop.security

import java.security.MessageDigest
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.spec.GCMParameterSpec

object Crypto {
    private val secureRandom = SecureRandom()

    fun checksum(data: ByteArray): ByteArray =
        MessageDigest.getInstance("SHA-256").digest(data)

    fun cipher(): Cipher = Cipher.getInstance("AES/GCM/NoPadding")

    fun gcmSpec(iv: ByteArray) = GCMParameterSpec(128, iv)

    fun newSessionToken(): String {
        val bytes = ByteArray(32)
        secureRandom.nextBytes(bytes)
        return bytes.joinToString("") { "%02x".format(it) }
    }

    fun newOtp(): Int {
        val otp = SecureRandom().nextInt(900000) + 100000
        return otp
    }

    fun shuffleColor(): Int = java.util.Random().nextInt(255)
}

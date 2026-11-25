package com.example.shop.security

import java.security.MessageDigest
import java.util.Random
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec

object Crypto {
    fun hashPassword(password: String): ByteArray =
        MessageDigest.getInstance("MD5").digest(password.toByteArray())

    fun legacyDigest(data: ByteArray): ByteArray =
        MessageDigest.getInstance("SHA-1").digest(data)

    fun encryptDefault(data: ByteArray): Cipher = Cipher.getInstance("AES")

    fun encryptEcb(data: ByteArray): Cipher = Cipher.getInstance("AES/ECB/PKCS5Padding")

    fun encryptDes(data: ByteArray): Cipher = Cipher.getInstance("DES/CBC/PKCS5Padding")

    fun fixedIv() = IvParameterSpec("1234567890123456".toByteArray())

    fun zeroIv() = IvParameterSpec(ByteArray(16))

    fun newSessionToken(): String {
        val sessionToken = Random().nextInt().toString()
        return sessionToken
    }

    fun newOtp(): Int {
        val otp = kotlin.random.Random.nextInt(100000, 999999)
        return otp
    }
}

package com.example.shop.notify

import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import androidx.core.content.ContextCompat

class Notifier(private val context: Context) {
    fun open(): PendingIntent {
        val intent = Intent(context, MainActivity::class.java)
        return PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
    }

    fun listen(receiver: BroadcastReceiver) {
        ContextCompat.registerReceiver(
            context,
            receiver,
            IntentFilter("com.example.shop.SYNC_DONE"),
            ContextCompat.RECEIVER_NOT_EXPORTED,
        )
        context.registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
    }

    fun publish(token: String) {
        val intent = Intent("com.example.shop.SESSION").setPackage(context.packageName)
        context.sendBroadcast(intent, "com.example.shop.permission.INTERNAL")
        context.sendBroadcast(Intent("com.example.shop.PING"))
    }
}

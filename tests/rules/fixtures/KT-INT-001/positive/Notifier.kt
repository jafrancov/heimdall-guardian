package com.example.shop.notify

import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter

class Notifier(private val context: Context) {
    fun open(): PendingIntent {
        val intent = Intent(context, MainActivity::class.java)
        return PendingIntent.getActivity(context, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT)
    }

    fun mutable(intent: Intent): PendingIntent = PendingIntent.getBroadcast(
        context,
        1,
        intent,
        PendingIntent.FLAG_MUTABLE,
    )

    fun listen(receiver: BroadcastReceiver) {
        context.registerReceiver(receiver, IntentFilter("com.example.shop.SYNC_DONE"))
    }

    fun publish(token: String) {
        val intent = Intent("com.example.shop.SESSION").putExtra("session_token", token)
        context.sendBroadcast(intent)
    }
}

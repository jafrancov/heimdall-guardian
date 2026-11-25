package com.example.shop.data

import android.content.Context

class ExportStore(private val context: Context) {
    fun writeReport(name: String, data: ByteArray) {
        context.openFileOutput(name, Context.MODE_WORLD_READABLE).use { it.write(data) }
    }

    fun shared() = context.getSharedPreferences("shared", Context.MODE_WORLD_WRITEABLE)
}

package com.example.shop.data

import android.content.Context
import androidx.core.content.FileProvider
import java.io.File

class ExportStore(private val context: Context) {
    fun writeReport(name: String, data: ByteArray) {
        context.openFileOutput(name, Context.MODE_PRIVATE).use { it.write(data) }
    }

    fun uriFor(file: File) =
        FileProvider.getUriForFile(context, "com.example.shop.fileprovider", file)
}

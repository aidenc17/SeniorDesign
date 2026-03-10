package com.example.mad.data

enum class MediaType {
    Image,
    Video
}

data class MediaItem(
    val id: String,
    val type: MediaType,
    val url: String
)

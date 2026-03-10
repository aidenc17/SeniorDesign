package com.example.mad.ui.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.media3.exoplayer.ExoPlayer

class VideoPlayerViewModel(application: Application) : AndroidViewModel(application) {
    val player: ExoPlayer = ExoPlayer.Builder(application.applicationContext).build()

    override fun onCleared() {
        player.release()
    }
}

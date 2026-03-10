package com.example.mad.ui.widgets

import android.widget.FrameLayout
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.viewinterop.AndroidView
import androidx.media3.common.MediaItem
import androidx.media3.common.util.UnstableApi
import androidx.media3.datasource.okhttp.OkHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.ui.PlayerView
import com.example.mad.data.HttpClientProvider

@UnstableApi
@Composable
fun VideoPlayer(
    mediaUrl: String,
    modifier: Modifier = Modifier.fillMaxSize(),
    onPlayerChanged: (ExoPlayer?) -> Unit = {}
) {
    val context = LocalContext.current
    val exoPlayer = remember(context) {
        val dataSourceFactory = OkHttpDataSource.Factory(HttpClientProvider.client)
        val mediaSourceFactory = DefaultMediaSourceFactory(context)
            .setDataSourceFactory(dataSourceFactory)

        ExoPlayer.Builder(context)
            .setHandleAudioBecomingNoisy(true)
            .setMediaSourceFactory(mediaSourceFactory)
            .build().apply {
                playWhenReady = true
                repeatMode = ExoPlayer.REPEAT_MODE_OFF
            }
    }
    val mediaItem = remember(mediaUrl) { MediaItem.fromUri(mediaUrl) }

    LaunchedEffect(mediaItem) {
        exoPlayer.seekTo(0)
        exoPlayer.setMediaItem(mediaItem)
        exoPlayer.prepare()
        exoPlayer.playWhenReady = true
    }

    AndroidView(
        factory = { ctx ->
            PlayerView(ctx).apply {
                layoutParams = FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.MATCH_PARENT,
                    FrameLayout.LayoutParams.MATCH_PARENT
                )
                useController = true
                controllerAutoShow = false
                player = exoPlayer
                setShowBuffering(PlayerView.SHOW_BUFFERING_WHEN_PLAYING)
            }
        },
        modifier = modifier,
        update = { view ->
            if (view.player !== exoPlayer) {
                view.player = exoPlayer
            }
        },
        onReset = { view ->
            view.player = null
        },
        onRelease = { view ->
            view.player = null
        }
    )

    DisposableEffect(exoPlayer) {
        onPlayerChanged(exoPlayer)
        onDispose {
            onPlayerChanged(null)
            exoPlayer.playWhenReady = false
            exoPlayer.pause()
            exoPlayer.stop()
            exoPlayer.release()
        }
    }
}

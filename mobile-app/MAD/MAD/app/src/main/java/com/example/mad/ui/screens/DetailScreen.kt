package com.example.mad.ui.screens

import android.app.Activity
import android.content.pm.ActivityInfo
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.media3.exoplayer.ExoPlayer
import com.example.mad.data.MediaType
import com.example.mad.ui.theme.MADTheme
import com.example.mad.ui.widgets.VideoPlayer
import com.example.mad.ui.widgets.ZoomableImage

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DetailScreen(
    mediaUrl: String,
    mediaType: MediaType,
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current
    var currentPlayer by remember { mutableStateOf<ExoPlayer?>(null) }

    if (mediaType == MediaType.Video) {
        BackHandler {
            currentPlayer?.let { player ->
                player.playWhenReady = false
                player.pause()
                player.seekTo(0)
            }
            onNavigateBack()
        }

        DisposableEffect(Unit) {
            val activity = context as? Activity
            val previousOrientation = activity?.requestedOrientation
            if (activity != null) {
                activity.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_LOCKED
            }

            onDispose {
                if (activity != null && previousOrientation != null) {
                    activity.requestedOrientation = previousOrientation
                }
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(text = "Preview") },
                navigationIcon = {
                    IconButton(
                        onClick = {
                            currentPlayer?.let { player ->
                                player.playWhenReady = false
                                player.pause()
                                player.seekTo(0)
                            }
                            onNavigateBack()
                        }
                    ) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when (mediaType) {
                MediaType.Image -> ZoomableImage(mediaUrl = mediaUrl)
                MediaType.Video -> VideoPlayer(
                    mediaUrl = mediaUrl,
                    onPlayerChanged = { currentPlayer = it },
                    modifier = Modifier.fillMaxSize()
                )
            }
        }
    }
}

@Preview
@Composable
private fun DetailScreenImagePreview() {
    MADTheme {
        DetailScreen(
            mediaUrl = "https://picsum.photos/id/42/1920/1080",
            mediaType = MediaType.Image,
            onNavigateBack = {}
        )
    }
}

@Preview
@Composable
private fun DetailScreenVideoPreview() {
    MADTheme {
        DetailScreen(
            mediaUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            mediaType = MediaType.Video,
            onNavigateBack = {}
        )
    }
}

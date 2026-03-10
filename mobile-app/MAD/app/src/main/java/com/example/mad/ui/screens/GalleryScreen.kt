package com.example.mad.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.PlayCircleFilled
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import coil.request.ImageRequest
import com.example.mad.data.MediaItem
import com.example.mad.data.MediaRepository
import com.example.mad.data.MediaType
import com.example.mad.ui.theme.MADTheme
import com.example.mad.ui.viewmodel.MediaUiState
import com.example.mad.ui.viewmodel.MediaViewModel
import com.example.mad.ui.viewmodel.MediaViewModelFactory

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GalleryScreen(
    title: String,
    baseUrl: String,
    repository: MediaRepository,
    showSettings: Boolean,
    onOpenSettings: () -> Unit,
    onOpenDetail: (MediaItem) -> Unit,
    onNavigateBack: () -> Unit
) {
    val mediaViewModel: MediaViewModel = viewModel(
        key = baseUrl,
        factory = MediaViewModelFactory(repository, baseUrl)
    )
    val uiState by mediaViewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(text = title) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                actions = {
                    if (showSettings) {
                        IconButton(onClick = onOpenSettings) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Settings"
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { padding ->
        GalleryScreenBody(
            uiState = uiState,
            onOpenDetail = onOpenDetail,
            modifier = Modifier.padding(padding)
        )
    }
}

@Composable
fun GalleryScreenBody(
    uiState: MediaUiState,
    onOpenDetail: (MediaItem) -> Unit,
    modifier: Modifier = Modifier
) {
    when {
        uiState.isLoading -> {
            Box(
                modifier = modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        }
        uiState.errorMessage != null -> {
            Box(
                modifier = modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text(text = uiState.errorMessage)
            }
        }
        uiState.items.isEmpty() -> {
            Box(
                modifier = modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text(text = "No media found.")
            }
        }
        else -> {
            LazyVerticalGrid(
                columns = GridCells.Adaptive(140.dp),
                modifier = modifier.fillMaxSize(),
                contentPadding = PaddingValues(12.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(uiState.items) { item ->
                    MediaGridItem(
                        item = item,
                        onClick = { onOpenDetail(item) }
                    )
                }
            }
        }
    }
}


@Composable
private fun MediaGridItem(
    item: MediaItem,
    onClick: () -> Unit
) {
    val context = LocalContext.current
    Box(
        modifier = Modifier
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .aspectRatio(1f)
            .clickable { onClick() }
    ) {
        val request = ImageRequest.Builder(context)
            .data(item.url)
            .crossfade(true)
            .build()

        AsyncImage(
            model = request,
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )
        if (item.type == MediaType.Video) {
            Icon(
                imageVector = Icons.Default.PlayCircleFilled,
                contentDescription = "Video",
                tint = Color.White,
                modifier = Modifier
                    .align(Alignment.Center)
                    .size(42.dp)
            )
        }
    }
}

@Preview(showBackground = true)
@Composable
fun GalleryScreenPreview() {
    val sampleItems = listOf(
        MediaItem(id = "1", url = "https://picsum.photos/id/10/250/250", type = MediaType.Image),
        MediaItem(id = "2", url = "https://picsum.photos/id/11/250/250", type = MediaType.Image),
        MediaItem(id = "3", url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", type = MediaType.Video),
        MediaItem(id = "4", url = "https://picsum.photos/id/13/250/250", type = MediaType.Image)
    )
    MADTheme {
        GalleryScreenBody(
            uiState = MediaUiState(items = sampleItems),
            onOpenDetail = {}
        )
    }
}

package com.example.mad.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.example.mad.data.MediaItem
import com.example.mad.data.MediaRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class MediaUiState(
    val isLoading: Boolean = true,
    val items: List<MediaItem> = emptyList(),
    val errorMessage: String? = null
)

class MediaViewModel(
    private val repository: MediaRepository,
    private val baseUrl: String
) : ViewModel() {
    private val _uiState = MutableStateFlow(MediaUiState())
    val uiState: StateFlow<MediaUiState> = _uiState.asStateFlow()

    init {
        load()
    }

    fun refresh() {
        load()
    }

    private fun load() {
        if (baseUrl.isBlank()) {
            _uiState.value = MediaUiState(
                isLoading = false,
                errorMessage = "Set the URL in Settings first."
            )
            return
        }

        _uiState.value = MediaUiState(isLoading = true)
        viewModelScope.launch {
            try {
                val items = repository.fetchMedia(baseUrl)
                _uiState.value = MediaUiState(isLoading = false, items = items)
            } catch (exception: Exception) {
                _uiState.value = MediaUiState(
                    isLoading = false,
                    errorMessage = exception.message ?: "Unable to load media."
                )
            }
        }
    }
}

class MediaViewModelFactory(
    private val repository: MediaRepository,
    private val baseUrl: String
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return MediaViewModel(repository, baseUrl) as T
    }
}

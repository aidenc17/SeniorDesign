package com.example.mad.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.mad.ui.theme.MADTheme
import com.example.mad.ui.viewmodel.SettingsViewModel
import kotlinx.coroutines.launch

@Composable
fun SettingsScreen(
    settingsViewModel: SettingsViewModel ,
    onNavigateBack: () -> Unit
) {
    val settings by settingsViewModel.settings.collectAsState()
    var regularUrl by rememberSaveable(settings.regularUrl) { mutableStateOf(settings.regularUrl) }
    var authenticatedUrl by rememberSaveable(settings.authenticatedUrl) {
        mutableStateOf(settings.authenticatedUrl)
    }
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    val onRegularUrlChange: (String) -> Unit = { regularUrl = it }
    val onAuthenticatedUrlChange: (String) -> Unit = { authenticatedUrl = it }

    SettingsScreenContent(
        regularUrl = regularUrl ,
        authenticatedUrl = authenticatedUrl ,
        onRegularUrlChange = onRegularUrlChange ,
        onAuthenticatedUrlChange = onAuthenticatedUrlChange ,
        onNavigateBack = onNavigateBack ,
        snackbarHostState = snackbarHostState ,
        onSave = {
            settingsViewModel.saveUrls(regularUrl , authenticatedUrl)
            scope.launch {
                snackbarHostState.showSnackbar("Saved")
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SettingsScreenContent(
    regularUrl: String ,
    authenticatedUrl: String ,
    onRegularUrlChange: (String) -> Unit ,
    onAuthenticatedUrlChange: (String) -> Unit ,
    onNavigateBack: () -> Unit ,
    snackbarHostState: SnackbarHostState ,
    onSave: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(text = "Settings") } ,
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack ,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        } ,
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp) ,
            verticalArrangement = Arrangement.Top
        ) {
            Text(
                text = "Media Endpoints" ,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(
                value = regularUrl ,
                onValueChange = onRegularUrlChange ,
                label = { Text("Regular URL") } ,
                placeholder = { Text("http://xxx.xxx.xxx.xxx:8080/") } ,
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(
                value = authenticatedUrl ,
                onValueChange = onAuthenticatedUrlChange ,
                label = { Text("Authenticated URL") } ,
                placeholder = { Text("http://xxx.xxx.xxx.xxx:8081/") } ,
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(24.dp))
            Button(
                onClick = onSave
            ) {
                Text(text = "Save")
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
private fun SettingsScreenPreview() {
    MADTheme {
        val snackbarHostState = remember { SnackbarHostState() }
        SettingsScreenContent(
            regularUrl = "http://123.456.789.000:8080/" ,
            authenticatedUrl = "http://123.456.789.000:8081/" ,
            onRegularUrlChange = {} ,
            onAuthenticatedUrlChange = {} ,
            onNavigateBack = {} ,
            snackbarHostState = snackbarHostState ,
            onSave = {}
        )
    }
}

package com.example.mad.ui.screens

import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import com.example.mad.R
import com.example.mad.data.SettingsData
import com.example.mad.ui.theme.MADTheme
import kotlinx.coroutines.launch

@Composable
fun LandingScreen(
    settings: SettingsData,
    onRegularUser: () -> Unit,
    onAuthenticatedUser: () -> Unit,
    buttonMinWidth: Dp = 220.dp,
    buttonMinHeight: Dp = 52.dp,
    buttonTextSizeSp: Float = 18f
) {
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    val activity = context as? FragmentActivity
    val isRegularConfigured = settings.regularUrl.isNotBlank()
    val isAuthenticatedConfigured = settings.authenticatedUrl.isNotBlank()

    if (activity == null) {
        LandingScreenContent(
            snackbarHostState = snackbarHostState,
            onRegularUser = onRegularUser,
            onAuthenticatedClick = {
                scope.launch {
                    snackbarHostState.showSnackbar("Biometric auth is not available.")
                }
            },
            isRegularConfigured = isRegularConfigured,
            isAuthenticatedConfigured = isAuthenticatedConfigured,
            buttonMinWidth = buttonMinWidth,
            buttonMinHeight = buttonMinHeight,
            buttonTextSizeSp = buttonTextSizeSp
        )
        return
    }

    val executor = remember { ContextCompat.getMainExecutor(context) }
    val biometricPrompt = remember {
        BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    // Once the system confirms biometrics, open the protected gallery.
                    onAuthenticatedUser()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    scope.launch {
                        snackbarHostState.showSnackbar(errString.toString())
                    }
                }
            }
        )
    }

    val promptInfo = remember {
        BiometricPrompt.PromptInfo.Builder()
            .setTitle("Authenticated Access")
            .setSubtitle("Use your fingerprint or face to continue")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .setNegativeButtonText("Cancel")
            .build()
    }

    LandingScreenContent(
        snackbarHostState = snackbarHostState,
        onRegularUser = onRegularUser,
        onAuthenticatedClick = {
            val canAuthenticate = BiometricManager.from(context).canAuthenticate(
                BiometricManager.Authenticators.BIOMETRIC_STRONG
            )
            if (canAuthenticate == BiometricManager.BIOMETRIC_SUCCESS) {
                // This triggers the system biometric sheet on the device.
                biometricPrompt.authenticate(promptInfo)
            } else {
                scope.launch {
                    snackbarHostState.showSnackbar("Biometric auth is not available.")
                }
            }
        },
        isRegularConfigured = isRegularConfigured,
        isAuthenticatedConfigured = isAuthenticatedConfigured,
        buttonMinWidth = buttonMinWidth,
        buttonMinHeight = buttonMinHeight,
        buttonTextSizeSp = buttonTextSizeSp
    )
}

@Composable
private fun LandingScreenContent(
    snackbarHostState: SnackbarHostState,
    onRegularUser: () -> Unit,
    onAuthenticatedClick: () -> Unit,
    isRegularConfigured: Boolean,
    isAuthenticatedConfigured: Boolean,
    buttonMinWidth: Dp,
    buttonMinHeight: Dp,
    buttonTextSizeSp: Float,
    modifier: Modifier = Modifier
) {
    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = Color.Transparent
    ) { padding ->
        Box(
            modifier = modifier.fillMaxSize()
        ) {
            Image(
                painter = painterResource(R.drawable.bg_starfield),
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
                alpha = 0.95f
            )

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(24.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Welcome",
                    style = MaterialTheme.typography.headlineMedium,
                    color = Color.White
                )
                Spacer(modifier = Modifier.height(20.dp))
                Text(
                    text = "Choose a side",
                    style = MaterialTheme.typography.titleMedium,
                    color = Color.White
                )
                Spacer(modifier = Modifier.height(30.dp))
                Button(
                    onClick = onRegularUser,
                    enabled = isRegularConfigured,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF1976D2)),
                    modifier = Modifier.sizeIn(minWidth = buttonMinWidth, minHeight = buttonMinHeight)
                ) {
                    Text(text = "Regular User", color = Color.White, fontSize = buttonTextSizeSp.sp)
                }
                Spacer(modifier = Modifier.height(30.dp))
                Button(
                    onClick = onAuthenticatedClick,
                    enabled = isAuthenticatedConfigured,
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F)),
                    modifier = Modifier.sizeIn(minWidth = buttonMinWidth, minHeight = buttonMinHeight)
                ) {
                    Text(text = "Authenticated User", color = Color.White, fontSize = buttonTextSizeSp.sp)
                }
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
private fun LandingScreenPreview() {
    MADTheme {
        LandingScreen(
            settings = SettingsData(
                regularUrl = "https://example.com/regular",
                authenticatedUrl = "https://example.com/auth"
            ),
            onRegularUser = {},
            onAuthenticatedUser = {}
        )
    }
}

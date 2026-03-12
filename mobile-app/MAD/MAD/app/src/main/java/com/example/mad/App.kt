package com.example.mad

import android.app.Application
import android.net.Uri
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import coil.ImageLoader
import coil.ImageLoaderFactory
import com.example.mad.data.HttpClientProvider
import com.example.mad.data.MediaRepository
import com.example.mad.data.MediaType
import com.example.mad.data.SettingsRepository
import com.example.mad.data.UserMode
import com.example.mad.ui.screens.DetailScreen
import com.example.mad.ui.screens.GalleryScreen
import com.example.mad.ui.screens.LandingScreen
import com.example.mad.ui.screens.SettingsScreen
import com.example.mad.ui.viewmodel.SettingsViewModel
import com.example.mad.ui.viewmodel.SettingsViewModelFactory

class MAD : Application() , ImageLoaderFactory {
    val settingsRepository by lazy { SettingsRepository(this) }
    val mediaRepository by lazy { MediaRepository() }

    override fun newImageLoader(): ImageLoader {
        return ImageLoader.Builder(this)
            .okHttpClient { HttpClientProvider.client }
            .build()
    }
}

sealed class Screen(val route: String) {
    data object Landing : Screen("landing")
    data object Gallery : Screen("gallery/{mode}") {
        fun createRoute(mode: UserMode) = "gallery/${mode.name}"
    }

    data object Detail : Screen("detail?url={url}&type={type}") {
        fun createRoute(url: String , type: MediaType): String {
            return "detail?url=${Uri.encode(url)}&type=${type.name}"
        }
    }

    data object Settings : Screen("settings")
}

@Composable
fun MADApp() {
    val navController = rememberNavController()
    val context = LocalContext.current
    val settingsRepository = (context.applicationContext as MAD).settingsRepository
    val mediaRepository = (context.applicationContext as MAD).mediaRepository
    val settingsViewModel: SettingsViewModel = viewModel(
        factory = SettingsViewModelFactory(settingsRepository)
    )
    val settingsState by settingsViewModel.settings.collectAsState()

    NavHost(
        navController = navController ,
        startDestination = Screen.Landing.route
    ) {
        composable(Screen.Landing.route) {
            LandingScreen(
                settings = settingsState ,
                onRegularUser = {
                    navController.navigate(Screen.Gallery.createRoute(UserMode.Regular))
                } ,
                onAuthenticatedUser = {
                    navController.navigate(Screen.Gallery.createRoute(UserMode.Authenticated))
                }
            )
        }
        composable(
            route = Screen.Gallery.route ,
            arguments = listOf(navArgument("mode") { type = NavType.StringType })
        ) { backStackEntry ->
            val modeName = backStackEntry.arguments?.getString("mode") ?: UserMode.Regular.name
            val mode = runCatching { UserMode.valueOf(modeName) }.getOrDefault(UserMode.Regular)
            val baseUrl = if (mode == UserMode.Authenticated) {
                settingsState.authenticatedUrl
            } else {
                settingsState.regularUrl
            }

            GalleryScreen(
                title = if (mode == UserMode.Authenticated) "Authenticated Users" else "Regular Users" ,
                baseUrl = baseUrl ,
                repository = mediaRepository ,
                showSettings = mode == UserMode.Authenticated ,
                onOpenSettings = {
                    navController.navigate(Screen.Settings.route)
                } ,
                onOpenDetail = { item ->
                    navController.navigate(Screen.Detail.createRoute(item.url , item.type))
                } ,
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        composable(
            route = Screen.Detail.route ,
            arguments = listOf(
                navArgument("url") { type = NavType.StringType } ,
                navArgument("type") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val url = Uri.decode(backStackEntry.arguments?.getString("url").orEmpty())
            val typeName = backStackEntry.arguments?.getString("type") ?: MediaType.Image.name
            val mediaType =
                runCatching { MediaType.valueOf(typeName) }.getOrDefault(MediaType.Image)

            DetailScreen(
                mediaUrl = url ,
                mediaType = mediaType ,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable(Screen.Settings.route) {
            SettingsScreen(
                settingsViewModel = settingsViewModel ,
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}

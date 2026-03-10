# MAD

MAD is an Android application built with Jetpack Compose that lets you browse media content delivered from both public and authenticated endpoints. It combines a modern UI, offline-friendly storage, secure biometric-protected areas, and media playback powered by ExoPlayer to create a responsive multimedia experience.

## Features

- **Media endpoint configuration** – Update the regular and authenticated media base URLs directly from the in-app Settings screen. Changes are persisted and surfaced across the app.
- **Media browsing & playback** – Stream video/audio using the latest `androidx.media3` ExoPlayer components with `coil-video` thumbnails.
- **Secure areas** – Opt-in biometric authentication (fingerprint, face, or device credential) using `androidx.biometric` to gate sensitive flows.
- **Offline-ready state** – Lightweight caching and preferences through Jetpack DataStore for fast relaunches and user-tailored defaults.
- **Navigation-first UX** – Compose Navigation keeps the app single-activity while enabling deep links and clear back-stack behavior.
- **Material 3 design system** – Consistent theming, typography, icons, and motion following modern Android guidelines.

## Tech Stack

| Layer            | Libraries / Tools |
|------------------|-------------------|
| UI               | Jetpack Compose (Material 3, Foundation, Compose BOM), Navigation-Compose |
| State & DI       | AndroidX Lifecycle (ViewModel, Runtime), Kotlin Coroutines |
| Storage          | AndroidX DataStore Preferences |
| Media            | AndroidX Media3 ExoPlayer & UI, Coil (images & video frames) |
| Networking       | OkHttp |
| Platform Support | Activity Compose, Core KTX, Biometric |

## Architecture

The app follows a unidirectional data flow inspired by MVVM:

1. **UI Layer** – Compose screens (e.g., `SettingsScreen`) consume immutable UI state and emit user intents.
2. **ViewModel Layer** – `SettingsViewModel` (and peers) expose Kotlin `StateFlow`s and coordinate persistence or business rules.
3. **Data Layer** – Repositories persist data via DataStore, fetch remote media via OkHttp, and stream playback with Media3.

This approach keeps screens stateless, improves previewability, and simplifies testing.

## Getting Started

### Prerequisites
- Android Studio Giraffe (or newer) with the latest Compose tooling
- JDK 17+
- Android device/emulator running API 24+

### Setup
1. Clone the repo:
   ```bash
   git clone https://github.com/<your-org>/MAD.git
   ```
2. Open the project in Android Studio and let Gradle sync.
3. Create a `local.properties` file (if missing) with your SDK path:
   ```
   sdk.dir=/path/to/android/sdk
   ```
4. Run the **app** configuration on a device/emulator.

## Configuring Media URLs

Navigate to **Settings → Media Endpoints** to define:
- **Regular URL**: Public base endpoint (e.g., `http://192.168.0.10:8080/`).
- **Authenticated URL**: Protected endpoint requiring credentials (e.g., `http://192.168.0.10:8081/`).

Tap **Save** to persist changes; a snackbar confirms success. These values drive playback requests across the app.

## Contributing

1. Create a feature branch from `main`.
2. Implement changes and add tests where relevant.
3. Submit a pull request with a concise summary and screenshots (if UI changes).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

# MAD (Mobile Access Device)

MAD is an Android application built with Jetpack Compose that lets you browse media content delivered from both public and authenticated endpoints. It combines a modern UI, offline-friendly storage, secure biometric-protected areas, and media playback powered by ExoPlayer to create a responsive multimedia experience.

## Features

- **Media endpoint configuration** – Update the regular and authenticated media base URLs directly from the in-app Settings screen. Changes are persisted via DataStore.
- **Media browsing & playback** – Stream video/audio using the latest `androidx.media3` ExoPlayer components with `coil-video` thumbnails.
- **Secure areas** – Biometric authentication (fingerprint, face, or device credential) using `androidx.biometric` to gate sensitive flows.
- **Offline-ready state** – Lightweight caching and preferences through Jetpack DataStore for fast relaunches and user-tailored defaults.
- **Navigation-first UX** – Compose Navigation keeps the app single-activity while enabling clear back-stack behavior.
- **Material 3 design system** – Modern Android UI with consistent theming and Material 3 components.

## Tech Stack

| Layer            | Libraries / Tools |
|------------------|-------------------|
| UI               | Jetpack Compose (Material 3), Navigation-Compose |
| State & DI       | AndroidX Lifecycle (ViewModel), Kotlin Coroutines |
| Storage          | AndroidX DataStore Preferences |
| Media            | AndroidX Media3 ExoPlayer & UI, Coil (images & video frames) |
| Networking       | OkHttp |
| Security         | Biometric API, Network Security Config (Custom CA support) |

## Requirements to Run

To ensure the project runs without issues, verify the following:

### 1. Development Environment
- **Android Studio**: Ladybug (2024.2.1) or newer recommended.
- **JDK**: Version 17 or 21 (Required for Gradle 9.1.0).
- **Gradle**: 9.1.0 (Managed via Gradle Wrapper).

### 2. Device/Emulator Requirements
- **Minimum SDK**: API 29 (Android 10.0).
- **Target SDK**: API 36 (Android 16).
- **Hardware/Feature Support**:
    - **Biometrics**: To access secure features, the device must have biometric hardware (fingerprint/face) or a device PIN/Pattern set up.
    - **Network**: Internet access is required to stream media.

### 3. Server-Side Requirements
- **Endpoints**: The app expects two types of endpoints:
    - **Regular URL**: For public media.
    - **Authenticated URL**: For protected media.
- **Security Headers**: The app sends an `X-App-Key: Yoda I Am!` header with every request.
- **SSL/TLS**: The app uses a custom certificate (`app/src/main/res/raw/api_crt.crt`).

## Getting Started

### Setup
1. **Clone the repo**:
   ```bash
   git clone https://github.com/<your-org>/MAD.git
   ```
2. **Open in Android Studio**: Open the `mobile-app/MAD/MAD` directory directly.
3. **Sync Gradle**: Allow Android Studio to download dependencies and sync the project using JDK 17+.
4. **Run the App**: Select the `app` configuration and run on a device/emulator (API 29+).

### Configuring Media URLs
Upon first launch, navigate to **Settings** to define:
- **Regular URL**: e.g., `https://your-public-api.com/`
- **Authenticated URL**: e.g., `https://your-secure-api.com/`

Tap **Save** to persist these settings. The app will use these base URLs to fetch media items.

## License

This project is licensed under the MIT License.

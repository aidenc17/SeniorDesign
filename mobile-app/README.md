# Photo Gallery Android App

**Simple, easy to customize photo gallery app** that fetches images from nginx endpoints with biometric authentication.

**Documentation:**
- **[CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)** - Detailed customization guide

## Features

**Simple 3-Page Design**
- Main page with two buttons
- Separate Regular and Authorized user pages

**Biometric Authentication**
- Fingerprint/face required for authorized user button

**Configurable URLs**
- Settings screen to change endpoints after authentication.
- Or edit directly in code (clearly marked)

**Photo Features**
- Grid layout
- Fullscreen zoom viewer
- Pull to refresh
- Auto loads images and videos from nginx endpoints

## Requirements

- **Android Studio**
- **Android Phone with biometric feature capability**

## Configuration

### Changing URLs at Runtime (Settings Screen)
1. Open the app
2. Tap the settings icon (top-right)
3. Enter new URLs
4. Tap "Save Settings"

### Changing Default URLs in Code
**File:** `app/src/main/java/com/example/androidapp/ConfigManager.kt` (lines 33-34)

```kotlin
const val DEFAULT_REGULAR_URL = "http://192.168.50.233:8080/"      // Change this
const val DEFAULT_AUTHORIZED_URL = "http://192.168.50.233:8081/"   // Change this
```

**See [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) for more customization options.**

## Run

Open the project in Android Studio and run on an emulator or physical device.

**Note:** For biometric authentication testing, use a physical device or an emulator with biometric enrollment configured.

## Troubleshooting

### Build Errors
- **Gradle sync fails:** Try File > Invalidate Caches > Invalidate and Restart
- **Dependency errors:** Ensure you have internet connection for Gradle to download dependencies
- **Version mismatch:** Check that Gradle version matches Android Gradle Plugin version

### Common Issues
- **Images not loading:** Check that nginx server is running and accessible from device
- **Biometric not working:** Ensure device has fingerprint/face unlock enrolled
- **HTTP connection fails:** Verify network_security_config.xml allows your server IP

## Dependencies (Minimal & Clean)

**Core:**
- Kotlin 2.2.10
- AndroidX Core 1.17.0, AppCompat 1.7.1
- Material Design 1.13.0
- Target SDK 36


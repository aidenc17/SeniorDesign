# Mobile App Development - MAD

## Features

**Simple 3-Page Design**
- Main page with two buttons
- Separate Regular and Authorized user pages

**Biometric Authentication**
- Fingerprint required for authorized user button

**Configurable URLs**
- Settings screen to change endpoints after authentication.

**Photo Features**
- Fullscreen zoom viewer
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

### Prerequisites

- Android Studio Giraffe (or newer) with the latest Compose tooling
- JDK 17+
- Android device/emulator running API 29+ (Android 10.0+)
- Gradle 9.1.0

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


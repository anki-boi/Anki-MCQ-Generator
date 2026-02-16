# android-app

Minimal Android application shell for the Anki MCQ Generator project.

## What's included
- Kotlin-based Android app module (`app`)
- A single `MainActivity`
- Basic app resources and app theme

## Immediate next step (to make it installable)
Generate Gradle wrapper files from Android Studio so the project can build consistently:

1. Open `android-app/` in Android Studio.
2. Let Android Studio sync the project.
3. From the terminal at `android-app/`, run:
   - `gradle wrapper`
4. Commit the generated files:
   - `gradlew`
   - `gradlew.bat`
   - `gradle/wrapper/gradle-wrapper.jar`
   - `gradle/wrapper/gradle-wrapper.properties`

## Install on your Android phone (debug build)
1. On your phone, enable **Developer options** and **USB debugging**.
2. Connect phone via USB and allow the debug prompt on device.
3. From `android-app/`, verify the device is visible:
   - `adb devices`
4. Build and install:
   - `./gradlew installDebug`
5. Launch app from phone launcher (`Anki MCQ`).

## If `installDebug` fails
- Ensure Android SDK is installed in Android Studio.
- Confirm `adb devices` shows your phone as `device` (not `unauthorized`).
- On Linux, verify udev USB permissions if device is not detected.

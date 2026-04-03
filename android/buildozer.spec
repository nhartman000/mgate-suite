[app]
title = Nych
package.name = nych
package.domain = org.mgate
source.dir = ../
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

requirements = python3, kivy, python-dotenv, jsonschema

orientation = portrait
fullscreen = 0
android.api = 34
android.ndk = 25b
android.sdk = 24
android.apptheme = @android:style/Theme.Material.Light.DarkActionBar
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE
android.arch = arm64-v8a
android.release_artifact = apk

icon.filename = %(source.dir)s/android/icon.png
presplash.filename = %(source.dir)s/android/splash.png

[buildozer]
log_level = 2
warn_on_root = 1
android_builddir = .buildozer/android/platform/build-arm64-v8a
bin_dir = bin

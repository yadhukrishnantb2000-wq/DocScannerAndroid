
[app]

title = Document Scanner
package.name = docscanner
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,webp
version = 1.0.0
requirements = python3,kivy,pillow,plyer
orientation = portrait
fullscreen = 0

android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1

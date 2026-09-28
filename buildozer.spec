[app]

# (str) Title of your application
title = Mijn App

# (str) Package name
package.name = mijnapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the base dir)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 0.1

# (list) Application requirements
requirements = python3,kivy

# (bool) Accept SDK license agreement automatically
android.accept_sdk_license = True

# (int) Target Android API
android.api = 33

# (int) Minimum Android API supported
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private = True

# (list) Permissions
android.permissions = INTERNET

# (list) Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (1 = display, 0 = hide)
warn_on_root = 1

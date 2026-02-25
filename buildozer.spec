[app]
# (str) Title of your application
title = Antigravity QR Scanner

# (str) Package name
package.name = qrscanner

# (str) Package domain (needed for android/ios packaging)
package.domain = org.antigravity

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
# We include python3, kivy, kivymd (for UI), pillow and pyzbar (for decoding).
# We also include zbar (the C-library that pyzbar wraps for Android).
requirements = python3, kivy==2.3.0, kivymd==1.1.1, pillow, pyzbar, zbar, sqlite3

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = CAMERA, INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

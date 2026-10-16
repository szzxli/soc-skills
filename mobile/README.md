# soc-skills mobile build

WebView wrapper APK for the soc-skills web app (offline-capable via service worker).

## Build (manual — Gradle daemon fails in this sandbox)

```bash
cd mobile/apkbuild
export PATH=~/workspace/tools/jdk-21.0.12.1+1/bin:$PATH
BT=~/workspace/tools/android-sdk/build-tools/34.0.0
AJAR=~/workspace/tools/android-sdk/platforms/android-34/android.jar

# 1. refresh web assets
cp ../../web/index.html ../../web/manifest.json ../../web/sw.js assets/www/

# 2. link
$BT/aapt2 compile --dir . -o build/compiled.zip
$BT/aapt2 link -o build/base.apk -I $AJAR --manifest AndroidManifest.xml \
  -A assets --min-sdk-version 24 --target-sdk-version 34 build/compiled.zip

# 3. compile + dex
mkdir -p build/classes build/dex
javac -source 8 -target 8 -bootclasspath $AJAR -d build/classes \
  src/com/szzxli/socskills/MainActivity.java
$BT/d8 --lib $AJAR --output build/dex \
  build/classes/com/szzxli/socskills/MainActivity.class

# 4. pack, align, sign
cp build/base.apk build/unsigned.apk
(cd build && zip -j unsigned.apk dex/classes.dex)
$BT/zipalign -f 4 build/unsigned.apk build/aligned.apk
$BT/apksigner sign --ks debug.keystore --ks-pass pass:android \
  --key-pass pass:android --out soc-skills.apk build/aligned.apk
$BT/apksigner verify --print-certs soc-skills.apk
```

## Notes

- Debug-signed. Never shipped to a device before — no signature conflicts.
- Package: `com.szzxli.socskills`. Label: `soc-skills`.
- localStorage works in the WebView (DOM storage enabled) — assessment history
  persists per install.
- Rebuild after any `web/` change: re-copy assets and rerun from step 2.

# Release platforms

## Full Rendering

### Audio
* **Filename:** `$project_full`
* **SampleRate:** 96000
* **Channels:** Stereo
* **Format:** Flac 
* **Flac encoding depth:** 32 bit
* **Data compression:** 8 - Slowest

## SoundCloud

### Audio
* **Filename:** `$project_soundcloud`
* **SampleRate:** 48000
* **Channels:** Stereo
* **Format:** Flac 
* **Flac encoding depth:** 24 bit
* **Data compression:** 8 - Slowest

### Image
Crop image as "Square"
* **Photo kind:** Jpeg
* **JPEG Quality:** Maximum
* **Color profile:** Most compatible
* **Size:** Medium


## CD Baby

### Audio
* **Filename:** `$project_cdbaby`
* **SampleRate:** 44100
* **Channels:** Stereo
* **Resample mode:** Sinc Interpolation: 192pt
* **Format:** Flac 
* **Flac encoding depth:** 16 bit
* **Data compression:** 8 - Slowest

## Image
Tranform image to 3000x3000
```
magick module-music-11.jpeg -resize 3000x3000 module-music-11-cdbaby.jpeg
```

## Bandcamp

### Audio
Check file size against Bandcamp's per-track cap (291MB new account / 600MB after $20 sales / 2GB with Bandcamp Pro).

* **Filename:** `$project_bandcamp`
* **SampleRate:** 48000
* **Channels:** Stereo
* **Format:** Flac
* **Flac encoding depth:** 24 bit   <!-- never 32-bit — Bandcamp rejects it outright -->
* **Data compression:** 8 - Slowest

### Image
Transform image to 3000x3000, RGB color space
```
magick module-music-11.jpeg -resize 3000x3000 -colorspace sRGB module-music-11-bandcamp.jpeg
```

# Marketing Site
Transform image for web. For instance.
```
magick module-music-11.jpeg -resize 1200x1200 -quality 80 module-music-11-web.jpeg
```

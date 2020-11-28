# guetzlidir

Will recursively process image files in source directory, optimizing them with Guetzli and writing to output directory.
Processing is slow, memory and CPU intensive.
EXIF data will be preserved

Optionally supports online processing using [TinyJPG](https://tinyjpg.com/) and [Kraken.io](https://kraken.io)

## Guetzli

[Guetzli](https://github.com/google/guetzli) is a JPEG encoder that aims for excellent compression density at high visual quality. Guetzli-generated images are typically 20-30% smaller than images of equivalent quality generated by libjpeg. Guetzli generates only sequential (nonprogressive) JPEGs due to faster decompression speeds they offer.

## Supported file formats (file extensions):

* JPEG (.jpg .jpeg)
* PNG (.png)

Supports Windows, Linux, MacOS and probably other OSes.

## Installation

```sh
pip install guetzlidir
```

You can download and use it as single Windows binary, see [Releases](https://github.com/varnav/guetzlidir/releases/)

## Usage

### PiPy package

```sh
guetzlidir --minsize 300 --quality 80 /home/username/myphotos /home/username/photos_out
```

### Windows executable

```cmd
./guetzlidir.exe "c:\Users\username\Pictures\My Vacation" "c:\Users\username\Pictures\My Vacation Optimized Pictures"
```

### TinyPNG online processing

[Get API key](https://tinypng.com/developers), then:

```sh
guetzlidir --minsize 300 --tinypng api_key /home/username/myphotos /home/username/photos_out
```

### Kraken.io online processing

Support is removed because no supported version is available in PyPi.
See [this](https://github.com/kraken-io/kraken-python/issues/5).

Windows release 0.3.2 still has it's support: [Download exe](https://github.com/varnav/guetzlidir/releases/download/v0.3.2/guetzlidir.exe).

## Known issues

Paths with spaces in windows are problematic. Looking for a solution.


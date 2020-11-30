import argparse
import io
import os
import pathlib
import shutil
import sys
import time
from typing import Iterable

import pyguetzli
import tinify
from PIL import Image

SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png']
__version__ = '0.5.0'


# Ported from: https://github.com/victordomingos/optimize-images
def search_images(dirpath: str, recursive: bool) -> Iterable[str]:
    if recursive:
        for root, dirs, files in os.walk(dirpath):
            for f in files:
                if not os.path.isfile(os.path.join(root, f)):
                    continue
                extension = os.path.splitext(f)[1][1:]
                if extension.lower() in SUPPORTED_FORMATS:
                    yield os.path.join(root, f)
    else:
        with os.scandir(dirpath) as directory:
            for f in directory:
                if not os.path.isfile(os.path.normpath(f)):
                    continue
                extension = os.path.splitext(f)[1][1:]
                if extension.lower() in SUPPORTED_FORMATS:
                    yield os.path.normpath(f)


def guetzlize_file(inpath, outpath, quality, minsize):
    print('From', inpath, 'to', outpath, 'with quality', quality)
    if inpath == outpath:
        print('Input path cannot be same as output path')
        exit(1)
    if os.path.exists(outpath):
        print("Output file exists")
        return 0

    # We use Pillow to wrap all this because Guetzli may fail to import many JPEG files,
    # and also to preserve EXIF information

    im = Image.open(inpath)
    try:
        exif = im.info['exif']  # Save EXIF data
    except KeyError:
        print("Error reading exif from", inpath)
        exif = False
    insize = os.path.getsize(inpath)
    if insize < (minsize * 1024):
        print(inpath, "minimum size of", minsize, "KB not met")
        return 0
    optimized_jpeg = pyguetzli.process_pil_image(im, quality=quality)
    outsize = sys.getsizeof(optimized_jpeg)

    sizediff = insize - outsize
    if sizediff > 0:
        im = Image.open(io.BytesIO(optimized_jpeg))
        if exif:
            im.save(outpath, 'JPEG', optimize=True, exif=exif)
        else:
            im.save(outpath, 'JPEG', optimize=True)
        percent = round((100 - (outsize / insize * 100)), 2)
        print('Saved', sizediff, 'B', 'or', percent, '%')
    else:
        print("Saved nothing, file skipped")

    return sizediff


def tinypngize_file(inpath, outpath, minsize):
    print('From', inpath, 'to', outpath, 'using online TinyJPG')
    if inpath == outpath:
        print('Input path cannot be same as output path')
        exit(1)
    if os.path.exists(outpath):
        print("Output file exists")
        return 0

    insize = os.path.getsize(inpath)
    if insize < (minsize * 1024):
        print("Minimum size not met")
        return 0

    im = Image.open(inpath)
    try:
        exif = im.info['exif']  # Save EXIF data
    except KeyError:
        print("Error reading exif from", inpath)
        exif = False

    source = tinify.tinify.from_file(inpath)
    source.to_file(outpath)

    im = Image.open(outpath)
    if exif:
        im.save(outpath, 'JPEG', optimize=True, exif=exif)
    else:
        im.save(outpath, 'JPEG', optimize=True)

    outsize = os.path.getsize(outpath)
    sizediff = insize - outsize

    percent = round((100 - (outsize / insize * 100)), 2)
    print('Saved', sizediff, 'B', 'or', percent, '%')

    if sizediff < 0:
        print('Savings are negative, copying original file')
        if os.path.isfile(inpath):
            shutil.copy2(inpath, outpath)

    return sizediff


def main():
    start_time = time.time()
    totalsaved = 0
    totalsavedkb = 0
    c = 0
    parser = argparse.ArgumentParser(description='This tool will recursively optimize jpeg files')
    parser.add_argument('srcpath', metavar='srcpath', type=str, help='Source directory')
    parser.add_argument('dstpath', metavar='dstpath', type=str, help='Destination directory')
    parser.add_argument('-m', '--minsize', help='minimum file size in kilobytes', type=int, default=100)
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quality', metavar='quality', type=int, default=90, help='JPEG quality, default 90')
    group.add_argument('-t', '--tinypng', help='TinyPNG API key', type=str)
    parser.add_argument('-nr', '--no-recursion', action='store_true',
                        help="Don't recurse through subdirectories.")
    args = parser.parse_args()
    # print("The arguments are: ", str(sys.argv))
    print('guetzlidir', __version__)
    if os.name == 'nt':
        # We strip nasty mess if trailing slash and quotes used
        srcpath = os.path.abspath(pathlib.PureWindowsPath(args.srcpath.rstrip("\"")))
        dstpath = os.path.abspath(pathlib.PureWindowsPath(args.dstpath.rstrip("\"")))
    else:
        srcpath = os.path.abspath(pathlib.PurePosixPath(args.srcpath))
        dstpath = os.path.abspath(pathlib.PurePosixPath(args.dstpath))
    if srcpath == dstpath:
        print('Input directory is same as output directory')
        exit(1)
    print('Processing files over', args.minsize, 'KB recursively starting from', srcpath)
    if not os.access(srcpath, os.R_OK):
        print('No such directory or not readable')
        sys.exit(1)
    print('Saving to', dstpath)
    if args.no_recursion:
        print('Processing non-recursively starting from', srcpath)
        recursive = False
    else:
        print('Processing recursively starting from', srcpath)
        recursive = True
    if not os.access(dstpath, os.W_OK):
        print('No such directory or not writable')
        sys.exit(1)
    outdir = os.path.abspath(dstpath)
    for filepath in search_images(str(srcpath), recursive=recursive):
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        outpath = outdir + os.sep + os.path.basename(filepath).lower()
        if not args.tinypng:
            result = guetzlize_file(filepath, outpath, args.quality, args.minsize)
            if result > 0:
                c += 1
                totalsaved = totalsaved + result
        elif args.tinypng:
            tinify.key = args.online
            result = tinypngize_file(filepath, outpath, args.minsize)
            if result > 0:
                c += 1
                totalsaved = totalsaved + result
        totalsavedkb = totalsaved / 1024

    if totalsavedkb > 0:
        print(c, 'files processed', 'in', round((time.time() - start_time), 2), 'saving', round(totalsavedkb, 2), 'KB')


if __name__ == '__main__':
    main()

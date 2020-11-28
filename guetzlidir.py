import argparse
import io
import os
import pathlib
import shutil
import sys
import time

import pyguetzli
import tinify
from PIL import Image

__version__ = '0.4.0'


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
    exif = im.info['exif']  # Save EXIF data
    insize = os.path.getsize(inpath)
    if insize < (minsize * 1024):
        print("Minimum size not met")
        return 0
    optimized_jpeg = pyguetzli.process_pil_image(im, quality=quality)
    outsize = sys.getsizeof(optimized_jpeg)

    sizediff = insize - outsize
    if sizediff > 0:
        im = Image.open(io.BytesIO(optimized_jpeg))
        im.save(outpath, 'JPEG', exif=exif)
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
    exif = im.info['exif']  # Save EXIF data

    source = tinify.tinify.from_file(inpath)
    source.to_file(outpath)

    im = Image.open(outpath)
    im.save(outpath, 'JPEG', exif=exif)

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
    supported = ('.jpg', '.jpeg', '.png')
    parser = argparse.ArgumentParser(description='This tool will recursively optimize jpeg files')
    parser.add_argument('srcpath', metavar='srcpath', type=str, help='Source directory')
    parser.add_argument('dstpath', metavar='dstpath', type=str, help='Destination directory')
    parser.add_argument('-m', '--minsize', help='minimum file size in kilobytes', type=int, default=100)
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quality', metavar='dstpath', type=int, default=90, help='JPEG quality, default 90')
    group.add_argument('-t', '--tinypng', help='TinyPNG API key', type=str)
    args = parser.parse_args()
    # print("The arguments are: ", str(sys.argv))
    print('guetzlidir', __version__)
    if os.name == 'nt':
        # We strip nasty mess if trailing slash and quotes used
        srcpath = pathlib.PureWindowsPath(args.srcpath.rstrip("\""))
        dstpath = pathlib.PureWindowsPath(args.dstpath.rstrip("\""))
    else:
        srcpath = pathlib.PurePosixPath(args.srcpath)
        dstpath = pathlib.PurePosixPath(args.dstpath)
    if srcpath == dstpath:
        print('Input directory is same as output directory')
        exit(1)
    print('Processing files over', args.minsize, 'KB recursively starting from', srcpath)
    if not os.access(srcpath, os.R_OK):
        print('No such directory or not readable')
        sys.exit(1)
    print('Saving to', dstpath)
    if not os.access(dstpath, os.W_OK):
        print('No such directory or not writable')
        sys.exit(1)
    for subdir, dirs, files in os.walk(srcpath):
        for filename in files:
            filepath = subdir + os.sep + filename.lower()
            if filepath.endswith(supported):
                outdir = subdir.replace(str(srcpath), str(dstpath))
                if not os.path.exists(outdir):
                    os.mkdir(outdir)
                outpath = outdir + os.sep + filename.lower()
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

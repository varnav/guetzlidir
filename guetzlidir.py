import time
import os
import sys
import argparse
import pathlib
import pyguetzli

__version__ = '0.1.0'


def optimizejpeg(inpath, outpath, quality, minsize, verbose=False):
    print('From', inpath, 'to', outpath, 'with quality', quality)
    if inpath == outpath:
        print('Input path cannot be same as output path')
        exit(1)
    if os.path.exists(outpath):
        print("Output file exists")
        return 0

    input_jpeg = open(inpath, "rb").read()
    insize = os.path.getsize(inpath)
    if insize < (minsize*1024):
        print("Minimum size not met")
        return 0
    optimized_jpeg = pyguetzli.process_jpeg_bytes(input_jpeg, quality=quality)
    outsize = sys.getsizeof(optimized_jpeg)

    sizediff = insize - outsize
    if sizediff > 0:
        output = open(outpath, "wb")
        output.write(optimized_jpeg)
        percent = round((100-(outsize / insize * 100)), 2)
        print('Saved', sizediff, 'B', 'or', percent, '%')
    else:
        print("Saved nothing, file skipped")

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
    parser.add_argument('-q', '--quality', metavar='dstpath', type=int, default=90, help='JPEG quality, default 90')
    parser.add_argument('-v', '--verbose', help='show every file processed', action='store_true')
    parser.add_argument('-m', '--minsize', help='minimum file size in kilobytes', type=int, default=50)
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    if args.verbose:
        print("The arguments are: ", str(sys.argv))
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
                outpath = outdir + os.sep + filename.lower()
                result = optimizejpeg(filepath, outpath, args.quality, args.minsize, args.verbose)
                if result > 0:
                    c += 1
                    totalsaved = totalsaved + result
                totalsavedkb = totalsaved/1024
    if totalsavedkb > 0:
        print(c, 'files processed', 'in', (time.time() - start_time), 'saving', totalsavedkb, 'KB')


if __name__ == '__main__':
    main()

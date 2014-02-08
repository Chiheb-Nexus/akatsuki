#!/usr/bin/env python3

import sys
import argparse
from struct import pack, unpack
from os.path import basename
from bitfactory import BitFactory
from pixelmanipulator import PixelManipulator
from pixelscraper import PixelScraper

# todo: a way of...
# [X] selecting an image
# [X] selecting a file to embed
# [X] calculating the maximum storage space
# [X] creating a png with alpha channel
# [X] cutting the secret file into bits, literally
# [X] putting one bit at the end of each channel of a pixel
# [X] reading the bits back out
# [X] storing the read bits
# [X] storing file info in a header
# [X] readiung the header
# [X] Argparse!
# [ ] Validate headers... I'm sure you can make really weird things happen with a weird header.


class Akatsuki:
    @staticmethod
    def inject_file(imagepath: str, secretpath: str, outputpath: str):

        secretfilename = basename(secretpath).encode()

        with open(secretpath, "rb") as f:
            secretdata = f.read()

        header = bytearray(b"\0" * 128)
        header[0:4] = pack("<I", len(secretdata))
        header[4:4 + len(secretfilename)] = secretfilename
        header = header[:128]  # cap anything that's too long

        pixelmanipulator = PixelManipulator(imagepath)

        maxfilesize = (pixelmanipulator.get_maximum_size() - 128)
        if maxfilesize < len(secretdata):
            print("The target container is too small for the secret. Maximum file size is", maxfilesize, "bytes")
            sys.exit(1)

        bitfactory = BitFactory(secretdata)

        pixelmanipulator.apply_bits(header, bitfactory)
        pixelmanipulator.save(outputpath)


    @staticmethod
    def extract_file(imagepath: str):
        pixelscraper = PixelScraper(imagepath)
        size, filename = pixelscraper.get_header()
        filename = bytes(filename).decode()
        data = pixelscraper.get_data()
        with open(filename, "wb+") as f:
            f.write(data)


    @staticmethod
    def get_header(imagepath: str) -> (int, str):
        size, filename = PixelScraper(imagepath).get_header()
        filename = bytes(filename).decode()
        return size, filename


    @staticmethod
    def get_maximum_size(imagepath: str) -> int:
        return PixelManipulator(imagepath).get_maximum_size()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Steg some files!")

    parser.add_argument("-i", "--image",  type=str, default="")
    parser.add_argument("-s", "--secret", type=str, default="")
    parser.add_argument("-o", "--output", type=str, default="")

    parser.add_argument("--info",    action="store_const", const=True, default=False)
    parser.add_argument("--extract", action="store_const", const=True, default=False)
    parser.add_argument("--inject",  action="store_const", const=True, default=False)

    args = vars(parser.parse_args())

    if sum(1 if args[name] else 0 for name in ('info', 'extract', 'inject')) != 1:
        print("You must specify either --info, --extract, or --inject")
        sys.exit(1)

    if args["inject"]:
        if not all(args[name] for name in ('image', 'secret', 'output')):
            print("You must specify all of --image, --secret, and --output")
        Akatsuki().inject_file(args["image"], args["secret"], args["output"])

    elif args["extract"] or args["info"]:
        if not args["image"]:
            print("You must specify an image to open with --image")

        capacity = Akatsuki.get_maximum_size(args["image"])
        print("Capacity: ", (capacity-128)//1024, "kb")

        try:
            size, filename = Akatsuki.get_header(args["image"])
            print("File:", filename)
            print("Size:", size//1024, "kb")
        except Exception as e:
            print("The file doesn't contain a valid header")
            sys.exit(1)

        if args["extract"]:
            try:
                Akatsuki().extract_file(args["image"])
            except Exception as e:
                print("Something went wrong:", e)

#!/usr/bin/env python3

import io
import sys
from PIL import Image
from operator import mul
from struct import pack, unpack
from os.path import basename

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
# [ ] Argparse!
# [ ] Validate headers... I'm sure you can make really weird things happen with a weird header.

class BitFactory:
    """
    Accepts anything that supports the file interface, and spits it back out, bit by bit. Literally.
    The order is least significant bit to most, always.
    """

    def __init__(self, data: bytes):
        self.data = data

    def get_bit_pair_generator(self, prefix: bytearray=None):
        """
        Gets two bits from the current byte, from right to left
        """

        if prefix:
            for byte in prefix:
                for i in range(4):  # from zero to 8, two at a time
                    yield byte & 3  # mask is 00000011
                    byte >>= 2      # push everything two steps to the right

        for byte in self.data:
            for i in range(4):      # from zero to 8, two at a time
                yield byte & 3      # mask is 00000011
                byte >>= 2          # push everything two steps to the right


class PixelManipulator:
    """
    """

    def __init__(self, path: str):
        self._image = Image.open(path).convert("RGBA")
        self._running_applier = False


    def get_pixel_generator(self):
        """
        Gets you the _image, one pixel at a time
        """
        for pixel in self._image.getdata():
            yield pixel


    def get_maximum_size(self) -> int:
        """
        Returns how many bytes of data the current _image can hold
        """
        return mul(*self._image.size)


    def get_bit_applying_generator(self, header: bytearray, bitFactory: BitFactory):
        """
        Accepts a header and a bitFactory, applies everything in the bitfactory to the picture
        """

        bitGen = bitFactory.get_bit_pair_generator(prefix=header)
        pixels = list(self._image.getdata())

        running = True
        for index, pixel in enumerate(pixels):
            if not running:
                break

            newPixel = ()
            for i in range(4):
                try:
                    bit = next(bitGen)
                    newPixel += (((pixel[i] >> 2) << 2) + bit, )
                except StopIteration:
                    running = False
                    newPixel += (pixel[i], )

            pixels[index] = newPixel

        return pixels


    def apply_bits(self, header: bytearray, bitFactory: BitFactory):
        """
        """
        im = self._image
        im.putdata(self.get_bit_applying_generator(header, bitFactory))


    def save(self, path: str):
        self._image.save(path)


class PixelScraper:
    """
    Scrapes the pixel data back out of the file.
    """

    def __init__(self, path: str):
        self._pixelManipulator = PixelManipulator(path)


    def get_header(self, length: int=128) -> (int, bytearray):
        pixGen = self._pixelManipulator.get_pixel_generator()

        clearText = bytearray()

        for index, pixel in enumerate(pixGen):
            if index == length:
                break
            charValue = 0
            for i in reversed(range(4)):
                charValue <<= 2
                charValue += pixel[i] & 3
            clearText.append(charValue)

        size = unpack("<I", clearText[0:4])[0]
        filename = clearText[4:].strip(b'\0')

        return size, filename


    def get_data(self):
        size, filename = self.get_header()
        pixGen = self._pixelManipulator.get_pixel_generator()

        # skip the header
        for i in range(128):
            next(pixGen)

        clearText = bytearray()

        for index, pixel in enumerate(pixGen):
            if index == size:
                break
            charValue = 0
            for i in reversed(range(4)):
                charValue <<= 2
                charValue += pixel[i] & 3
            clearText.append(charValue)

        return clearText


class Akatsuki:
    @staticmethod
    def injectFile(originalPath: str, secretPath: str, outputPath: str):

        secretFileName = basename(secretPath).encode()

        with open(secretPath, "rb") as f:
            secretData = f.read()

        header = bytearray(b"\0" * 128)
        header[0:4] = pack("<I", len(secretData))
        header[4:4 + len(secretFileName)] = secretFileName
        header = header[:128] # cap anything that's too long

        pixelManipulator = PixelManipulator(originalPath)

        maxFileSize = (pixelManipulator.get_maximum_size() - 128)
        if maxFileSize < len(secretData):
            print("The target container is too small for the secret. Maximum file size is", maxFileSize, "bytes")
            sys.exit(1)

        bitFactory = BitFactory(secretData)

        pixelManipulator.apply_bits(header, bitFactory)
        pixelManipulator.save(outputPath)

    @staticmethod
    def extractFile(containerPath: str):
        pixelScraper = PixelScraper(containerPath)
        size, filename = pixelScraper.get_header()
        filename = bytes(filename).decode()

        print("Found file named %s, size %d kb" % (filename, size//1024))

        data = pixelScraper.get_data()
        with open(filename, "wb+") as f:
            f.write(data)


if __name__ == '__main__':

    akatsuki = Akatsuki()

    originalPath = "/home/kim/pictures/steg/original.png"
    secretPath = "/home/kim/pictures/steg/secret.jpg"
    outputPath = "/home/kim/pictures/steg/container.png"

    #akatsuki.injectFile(originalPath, secretPath, outputPath)

    akatsuki.extractFile(outputPath)


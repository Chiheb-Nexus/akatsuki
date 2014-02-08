from struct import unpack
from pixelmanipulator import PixelManipulator


class PixelScraper:
    """
    Scrapes the pixel data back out of the file.
    """

    def __init__(self, path: str):
        self._pixelManipulator = PixelManipulator(path)


    def get_header(self, length: int=128) -> (int, bytearray):
        pixgen = self._pixelManipulator.get_pixel_generator()

        cleartext = bytearray()

        for index, pixel in enumerate(pixgen):
            if index == length:
                break
            charvalue = 0
            for i in reversed(range(4)):
                charvalue <<= 2
                charvalue += pixel[i] & 3
            cleartext.append(charvalue)

        size = unpack("<I", cleartext[0:4])[0]
        filename = cleartext[4:].strip(b'\0')

        return size, filename


    def get_data(self):
        size, filename = self.get_header()
        pixgen = self._pixelManipulator.get_pixel_generator()

        # skip the header
        for i in range(128):
            next(pixgen)

        cleartext = bytearray()

        for index, pixel in enumerate(pixgen):
            if index == size:
                break
            charvalue = 0
            for i in reversed(range(4)):
                charvalue <<= 2
                charvalue += pixel[i] & 3
            cleartext.append(charvalue)

        return cleartext

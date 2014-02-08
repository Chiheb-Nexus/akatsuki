from struct import unpack
from pixelmanipulator import PixelManipulator


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

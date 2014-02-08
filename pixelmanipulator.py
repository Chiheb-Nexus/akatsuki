from PIL import Image
from operator import mul
from bitfactory import BitFactory

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

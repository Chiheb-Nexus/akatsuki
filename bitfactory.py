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

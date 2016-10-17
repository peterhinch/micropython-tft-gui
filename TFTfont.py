
class TFTFont(object):
    def __init__(self, font, index, vert, horiz, nchars, firstchar = 32):
        self.firstchar = firstchar  # ord(first_character) Future use: absent from C file.
        self.nchars = nchars        # No. of chars in font
        self.bits_horiz = horiz     # Width in pixels of char if rendered as monospaced
        self.bits_vert = vert       # Height in pixels
        self._index = index
        self._font = font

    def get_ch(self, ch):
        from uctypes import addressof
        relch = ch - self.firstchar
        if relch > self.nchars or relch < 0:
            relch = 0 # instead of value error, typically this is space
            # raise ValueError('Character value {:} is unsupported.'.format(ch))
        offset = relch * 2            # index is 2 bytes/char
        offset =  self._index[offset] + (self._index[offset + 1] << 8)
        delta = (relch + 1) * 2            # index is 2 bytes/char
        delta =  (self._index[delta] + (self._index[delta + 1] << 8)) - offset
        return addressof(self._font) + offset, self.bits_vert, (delta * 8) // self.bits_vert
#
# Get the invariant properties of the font
# 
    def get_properties(self):
        return self.bits_vert, self.bits_horiz, self.nchars, self.firstchar

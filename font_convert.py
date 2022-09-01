"""
Quick Python script to convert .bmp file to font datastructure
used by Workshop 4 by 4D Systems (https://4dsystems.com.au).

Can handle fonts from 9 to 16 columns

I used Photoshop to convert the original image to an indexed color image
and saved it as a .bmp with 1-bit color and flipped row order.
"""

import struct

def convert(filename, font_name, font_chars, font_width, font_height):
    bmp = open(filename, 'rb')
    data = bmp.read()

    (signature, filesize, _, img_offset, hdr_size) = struct.unpack('<2sLLLL', data[:0x12])

    if signature != b'BM' or hdr_size != 40:
        print("Unexpected signature (%2s != 'BM') or header size (%u != 40)" %
              (signature, hdr_size))
        exit()

    (width, height, planes, bits, compression, img_size, hres, vres, palette_size, 
        _) = struct.unpack('<llHHLLLLLL', data[0x12:0x36])

    if bits != 1:
        print("Script only handles bitmaps with 1 bits/pixel (not %u bits)" % bits)
        exit()

    if width & 0x7:
        print("Script only handles 'multiple of 8' widths (fails for %u)" % width)
        exit()

    if height > 0:
        print("Script only handles BMP files in reverse row order")
        exit()
    else:
        height = -height


    print(
"""/*
    24x14 pixel ASCII font from https://xdevs.com/article/lcd-font/
    Copyright (c) 2012-2016, xDevs.com Microcontroller Software Support
    Illya Tsemenko <team@xdevs.com>

    You are very welcome to use the font, there are no restrictions for reuse.
*/

#DATA
    byte %s
    0,             // type 0 = simple
    0x%x,          // number of characters
    32,            // starting offset
    %u,            // font width
    %u,            // font height
""" % (font_name, font_chars, font_width, font_height))

    comma = ","
    # only set top <font_width> bits of value stored in flash
    mask = (0xFFFF << (16 - font_width)) & 0xFFFF
    # for each character in bitmap...
    for i in range(0, font_chars):
        # first row of a given character is based on character width
        print('// 0x%x "%c"' % (i + 32, i + 32))
        offset = img_offset + (i * font_width // 8);
        for b in range(0, font_height):
            if b and ((b & 0x7) == 0):
                print('')
            if i == (font_chars - 1) and b == (font_height - 1):
                comma = ""      # leave comma off of last byte
            
            remainder = (i * font_width) % 8
            value = data[offset] << (8 + remainder)
            value |= data[offset + 1] << remainder
            if remainder:
                value |= data[offset + 2] >> (8 - remainder)
            value &= mask
            
            print("0x%02X,0x%02X%s" % (value >> 8, value & 0xFF, comma), end='')
            offset += (width + 31) // 32 * 4;   # BMP rows are multiple of 32 bits
        print('')
        
    print("\n#END // %u bytes of font data" % (font_height * font_chars * 2))

convert('ascii_2414.bmp', 'FONT_XDEVS_14x24', 
        font_chars=95, font_width=14, font_height=24)

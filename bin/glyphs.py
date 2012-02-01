#!/usr/bin/python
# Filename: glyphs.py
# draw glyphs for scaffold view

import sys
import Image
import ImageFont
import ImageDraw
import math

# nt to px scale factor, font, font width, min glyph width, glyph height, 
SCALE_FACTOR = 50.0

SMALL_FONT = ImageFont.load(sys.path[0] + "/fonts/04B_24__.pil")
fw = 4
MIN_WIDTH = fw * 8 
ih = 7
# bgcolor, fgcolor by pair status
BG = (255,255,255)
FG = { 
    'OneUnmapped': (0,0,165),
    'MultiplyMapped': (165,0,0),
    'SameContig': (0,0,0),
    'Link': (0,165,0),
    'FalsePair': (165,80,0) }

def get_iw(tw=None):
    ''' Get glyph width, if tw not specified, return default.'''
    
    if tw:
        if tw < MIN_WIDTH:
            return tw + MIN_WIDTH
        else:
            return tw
    else:
        return ((fw * 5) + 1)

def single(fgcolor, strand, txt):
    ''' If single end, return fixed width glyph with label 'txt' and arrow 'strand' '''
    
    if len(txt) > 3:
        raise ValueError('Text for glyph must not exceed 3 chars.')

    nf = 5
    iw = get_iw()
    img = Image.new("RGB", (iw, ih), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([(0,0), (iw, ih)], fill=fgcolor)
    if strand == '+':
        d.text((1,1), txt + '>>', font=SMALL_FONT)
    elif strand == '-':
        d.text((1,1), '<<' + txt, font=SMALL_FONT)
    else:
        raise ValueError('Strand must be "+" or "-".')
    return img
   
def paired(fgcolor, template_size=8000, strand='+-'):
    ''' if paired end, return variable length glyph with insert size label and
    two arrows 'strand' '''

    img = None
    ft = '>>'
    rt = '<<'
    nf = 8 # number of chars in label + strands

    # template width in px
    tw = int(math.ceil(template_size / SCALE_FACTOR))
    if tw < 2: tw = 2
    iw = get_iw(tw)
        
    if strand[0] == '-': ft = '<<'
    if strand[1] == '+': rt = '>>'
    
    # change sig. digits on insert size
    if template_size < 10000:
        txt = "%0.2f" % (template_size / 1000.0)
    elif template_size < 100000:
        txt = "%0.1f" % (template_size / 1000.0)
    else:
        txt = "%0.0f" % (template_size / 1000.0)
    
    # if there is space for label and strans internally...
    if tw > MIN_WIDTH:
        img = Image.new("RGB", (iw, ih), BG)
        d = ImageDraw.Draw(img)
        d.rectangle([(0,0), (iw, ih)], fill=fgcolor)
        d.text((1, 1),  ft, font=SMALL_FONT)
        d.text(((iw-(fw*2), 1)),  rt, font=SMALL_FONT)
        if template_size > 15000:
            # print label repeatedly
            for i in range(1, ((iw-(fw*4)) / (int(SCALE_FACTOR)*2))+1):
                d.text(((i*(SCALE_FACTOR*2))-(fw*2)-1,1), txt, font=SMALL_FONT)
        else:
            d.text((int(math.ceil(iw/2.0)) - fw*2 + 2, 1), txt, font=SMALL_FONT)
        
    else: # put label on right of template rect
        print template_size, iw
        img = Image.new("RGB", (iw, ih), BG)
        d = ImageDraw.Draw(img)
        d.rectangle([(0,0), (tw, ih)], fill = fgcolor)
        d.text((tw+2, 1),  '%s%s%s' % (ft,txt,rt), font=SMALL_FONT, fill = fgcolor)
    return img
        
if __name__ == '__main__':
    img = Image.new("RGB", (500, 1000), (200,200,200))
    d = ImageDraw.Draw(img)
    img.paste(single(FG['OneUnmapped'], '+', "???"), (0,0))
    img.paste(single(FG['MultiplyMapped'], '-', "***"), (0,16))
    y = 32
    for i in range(0,200,5):
        img.paste(paired(FG['SameContig'], (i*100), '-+'), (0, y))
        y += 8
    for i in range(0,200,5):
        img.paste(paired(FG['Link'], (i*100), '-+'), (0, y))
        y += 8
    img.save("tmp.png")

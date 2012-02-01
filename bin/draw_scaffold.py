#!/usr/bin/python

import sys
import glyphs
import agp
import status
import Image


def convert_contig_name(cn):
    if cn == 'Repeat':
        return '|||'
    if cn == 'Unmapped':
        return '???'
    else:
        return str(int(cn[6:]))

if __name__ == '__main__':
    pairs = status.load_pair_status(open(sys.argv[1]))
    scaffolds = agp.load(open('scaffold00023.txt'))
    iw = int(scaffolds.length('scaffold00023') / glyphs.SCALE_FACTOR)+1
    ih = 300
    print scaffolds.length('scaffold00023'), iw, int(iw)+1, ih
    contig_offsets = {}
    for s in scaffolds.objects['scaffold00023']:
        if s.component_type != 'N':
            contig_offsets[s.component_id] = s.object_beg
    print contig_offsets
    scaffold_pairs = []
    for t in pairs:
        p = pairs[t]
        if contig_offsets.get(p.left_contig) or contig_offsets.get(p.right_contig):
            scaffold_pairs.append(p)
    img = Image.new("RGB", (iw, 16*len(scaffold_pairs)), (200,200,200))
    y = 0
    for p in scaffold_pairs:
        if contig_offsets.get(p.left_contig) and contig_offsets.get(p.right_contig):
            
            if contig_offsets.get(p.left_contig) == contig_offsets.get(p.right_contig):
                # not FalsePair, usually SameContig
                if p.status != 'FalsePair':
                    ts = p.left_pos + contig_offsets[p.left_contig]
                    te = p.right_pos + contig_offsets[p.right_contig]
                    strand = None
                    if ts < te:
                        strand = p.left_dir + p.right_dir
                    else:
                        strand = p.right_dir + p.left_dir
                        ts, te = te, ts
                    x = int(ts / glyphs.SCALE_FACTOR)
                    img.paste(glyphs.paired(glyphs.FG[p.status], te-ts, strand), (x, y))
                    
                # FalsePair on same contig
                else:
                    ts = p.left_pos + contig_offsets[p.left_contig]
                    x = int(ts / glyphs.SCALE_FACTOR)
                    txt = str(int(p.right_contig[6:]))
                    img.paste(glyphs.single(glyphs.FG[p.status], p.left_dir, 'TXT'), (x, y))

                    ts = p.right_pos + contig_offsets[p.right_contig]
                    x = int(ts / glyphs.SCALE_FACTOR)
                    txt = str(int(p.left_contig[6:]))
                    img.paste(glyphs.single(glyphs.FG[p.status], p.right_dir, 'TXT'), (x, y))
                    
            else: # Both Mapped, on different contigs
                if contig_offsets.get(p.left_contig):
                    ts = p.left_pos + contig_offsets[p.left_contig]
                    x = int(ts / glyphs.SCALE_FACTOR)
                    txt = str(int(p.right_contig[6:]))
                    img.paste(glyphs.single(glyphs.FG[p.status], p.left_dir, txt), (x, y))

                
                if contig_offsets.get(p.right_contig):
                    ts = p.right_pos + contig_offsets[p.right_contig]
                    x = int(ts / glyphs.SCALE_FACTOR)
                    txt = str(int(p.left_contig[6:]))
                    img.paste(glyphs.single(glyphs.FG[p.status], p.right_dir, txt), (x, y))
                
                    
        elif contig_offsets.get(p.left_contig): # left only
            ts = p.left_pos + contig_offsets[p.left_contig]
            x = int(ts / glyphs.SCALE_FACTOR)
            txt = convert_contig_name(p.right_contig)
            img.paste(glyphs.single(glyphs.FG[p.status], 
                                    p.left_dir, 
                                    txt), 
                      (x, y))
                    
                
        elif contig_offsets.get(p.right_contig): # right only
            ts = p.right_pos + contig_offsets[p.right_contig]
            x = int(ts / glyphs.SCALE_FACTOR)
            txt = convert_contig_name(p.left_contig)
            img.paste(glyphs.single(glyphs.FG[p.status], 
                                    p.right_dir, 
                                    txt), 
                      (x, y))
            
        else:
            raise ValueError('Cannot process template: %s' % p.template)
                
        y += 16
    img.save("tmp.png")


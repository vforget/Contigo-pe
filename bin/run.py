#!/usr/bin/python
# Filename: contigo.py
# Author: Vincenzo Forgetta, vincenzo.forgetta@mail.mcgill.ca
# Methods:
#################################################################################

import sys

# update path for ci31
sys.path.append("/data/sequencer/software/python/lib64/python2.6/site-packages/PIL")

# Python 2.5 on ci31
# "/data/sequencer/software/python/lib/lib64/python2.5/site-packages/PIL")
# sys.path.append("/data/sequencer/software/python/lib/lib64/python2.5/site-packages/")
sys.path.append("/home/vforget/lib/python/PIL")

import re
from optparse import OptionParser
import os.path
import shutil

sys.path.append("/home/vforget/Dropbox/Contigo/")
from contigo import *

import datetime
import multiprocessing
import Image
import ImageFont
import ImageDraw

def update_interface(options):
    '''Copies interface from source distribution to output dir
    Parameters: OUTDIR, HTML contig table, HTML scaffold table
    Returns: Nothing.
    '''
    root_path = sys.path[0] + "/../contigo/static"
    try:
        output_dir = options.output_dir
        if os.path.exists(output_dir + "/js"):
            shutil.rmtree(output_dir + "/js")
        shutil.copytree(root_path + "/js", output_dir + "/js")
        print "s1"
        if os.path.exists(output_dir + "/jquery-ui"):
            shutil.rmtree(output_dir + "/jquery-ui")
        
        shutil.copytree(root_path + "/js/jquery-ui", output_dir + "/jquery-ui")

        if os.path.exists(output_dir + "/" + "styles"):
            shutil.rmtree(output_dir + "/" + "styles")
        shutil.copytree(root_path + "/css", output_dir + "/styles")
        print "s2"
        shutil.copy(root_path + "/images/help_30.png", output_dir)
        shutil.copy(root_path + "/images/reload.gif", output_dir)
        shutil.copy(root_path + "/html/disclaimer.html", output_dir)
        of = open(output_dir + "/" + "contigo.html", "w")
        contig_table = open(output_dir + "/" + "contig_table.html").read()
        scaffold_table = open(output_dir + "/" + "scaffold_table.html").read()
        filter_options = open(output_dir + "/" + "filter_options.html").read()
        render.interface(of, options, contig_table, scaffold_table, filter_options)
        of.close()
        af = open(output_dir + "/help.html", 'w')
        print >> af, render.html_header() + render.html_footer()
        af.close()
    except IOError as (errno, strerror):
        print errno
        print strerror
        sys.exit("Cannot access/write destination directory or files.")


def parse_options():
    ''' Parse command line options. 
    Parameters: None.
    Returns: command line options
    '''
    
    default_outdir = "./" + datetime.datetime.now().strftime("%d%m%Y%k%M%S")
    
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-i", "--input_dir", dest="input_dir",
                      default="./", metavar="INPUTDIR",
                      help="Read assembly FILEs from INPUTDIR [default: %default]")
    parser.add_option("-o", "--output_dir", dest="output_dir",
                      default=default_outdir, metavar="OUTDIR",
                      help="Write output to OUTDIR [default: %default]")
    parser.add_option("-a", "--file", dest="assembly", default="454Contigs.ace",
                      help="Read assembly data from FILE [default: %default]",
                      metavar="FILE")
    parser.add_option("-s", "--scaffold", dest="scaffold",
                      default='454Scaffolds.txt', metavar="FILE",
                      help="Read scaffold from FILE [default: %default]")
    parser.add_option("-r", "--read_status", dest="read_status",
                      default='454ReadStatus.txt', metavar="FILE",
                      help="Read read status from FILE [default: %default]")
    parser.add_option("-l", "--pair_status", dest="pair_status",
                      default='454PairStatus.txt', metavar="FILE",
                      help="Read pair status from FILE [default: %default]")
    parser.add_option("-p", "--platform", dest="platform",
                      default='roche', metavar="PLATFORM",
                      choices=('roche', 'illumina', 'generic'),
                      help="Assembly PLATFORM: roche, illumina, generic [default: %default]")
    parser.add_option("-n", "--no-image", dest="noimage", 
                      action="store_true", default=False, metavar="SKIP_IMAGE",
                      help="Set to skip contig images [default: %default]")
    parser.add_option("-t", "--assembly-name", dest="assembly_name",
                      default='Entire', metavar="NAME",
                      help="Assembly NAME [default: %default]")
    parser.add_option("-m", "--min-contig-len", dest="min_contig_len",
                      default=500, metavar="SIZE", type="int",
                      help="Minumum contig SIZE [default: %default]")
    parser.add_option("-b", "--max-contig-num", dest="max_contig_num",
                      default=None, metavar="SIZE", type="int",
                      help="Process MAX contigs [default: %default]")
    parser.add_option("-c", "--contig-name", dest="contig_name",
                      default=None, metavar="NAME", 
                      help="Process contig with NAME [default: %default]")
    parser.add_option("-k", "--num-processors", dest="num_processors",
                      default=1, metavar="NUMBER", type="int",
                      help="NUMBER of processors to use [default: %default]")
    parser.add_option("-d", "--mode", dest="mode",
                      default='full', metavar="MODE", choices=['light', 'full', 'interface'],
                      help="MODE to run program [default: %default]")
    
    return parser.parse_args()

def init(options):
    ''' Validate the user-supplied command-line options and create outdirs
        Returns nothing.  
    '''
    if options.num_processors > multiprocessing.cpu_count():
        exit("Number of processors (%s) exceeds cpu count (%s)." % options.num_processors, multiprocessing.cpu_count);
    
    if not os.path.exists(options.input_dir):
        exit("INPUTDIR does not exist.")
    if not os.path.exists(options.input_dir + "/" + options.assembly):
        exit("Assembly FILE does not exist.")
    if not os.path.exists(options.output_dir):
        try:
            os.mkdir(options.output_dir)
        except OSError:
            exit("Cannot create OUTDIR.")
    if not os.path.exists(options.output_dir + "/dzi"):
        os.mkdir(options.output_dir + "/dzi")
    if not os.path.exists(options.output_dir + "/dzi_2"):
        os.mkdir(options.output_dir + "/dzi_2")
    if not os.path.exists(options.output_dir + "/dzi_3"):
        os.mkdir(options.output_dir + "/dzi_3")
    if not os.path.exists(options.output_dir + "/json"):
        os.mkdir(options.output_dir + "/json")
        
def create_scaffold_table(options):
    ''' Create HTML table for scaffolds.
    Returns HTML table (empty if no scaffolds).'''

    scaffold_table = '<table id="scaffold_table"><tr>'\
        '<td>Scaffold table not available</td></tr></table>'
    sys.stderr.write("Scaffold ... ")
    num_scaffolds = 0
    agp_json = ''
    if options.scaffold and  \
            os.path.exists(options.input_dir + "/" + options.scaffold):
        scaffold_table = agp.scaffold_table_header()
        rows, num_scaffolds = agp.make_scaffold_table(options)
        for row in rows:
            scaffold_table += agp.scaffold_table_row(row)
        scaffold_table += agp.scaffold_table_footer()
        agp_json = agp.make_json(options)
        
    else:
        sys.stderr.write(" FILE: %s does not exist, skipping ... " % options.scaffold)
    
    sys.stderr.write("done.\n")
    return scaffold_table, num_scaffolds, agp_json

def prepare_zoomtig_js(contig_name, contig_length, contig_padded_length, padded_start, padded_end, max_depth, height, ruler_height):
    s = '<script type="text/javascript">'
    s += 'var viewer = null;\n'
    s += 'function init() {\n'
    s += 'if ("dzi/%s.dzi") {\n'
    s += '    CONTIGO.current_contig_name = "%s";\n' % contig_name
    s += '    CONTIGO.current_contig_assembly_length = %s;\n' % (padded_end - padded_start)
    s += '    CONTIGO.current_contig_padded_start = %s;\n' % padded_start
    s += '    CONTIGO.current_contig_padded_end = %s;\n' % padded_end
    s += '    CONTIGO.current_contig_length = %s;\n' % contig_length
    s += '    CONTIGO.current_contig_padded_length = %s;\n' % contig_padded_length
    s += '    CONTIGO.current_contig_max_depth = %s;\n' % max_depth
    s += '    CONTIGO.current_contig_height = %s;\n' % height
    s += '    CONTIGO.current_contig_ruler_height = %s;\n' % ruler_height
    s += '    $(\'#contig_viewed\').html("<b>%s</b> [%s cols, %s bp, %s pads]");\n' % (contig_name,
                                                                                   (padded_end - padded_start),
                                                                                   contig_length,
                                                                                   (contig_padded_length - contig_length))
    s += '    viewer = new Seadragon.Viewer("zoomtig");\n'
    s += '    viewer.openDzi("dzi/%s.dzi");\n' % contig_name
    s += '    viewer.addEventListener("open", showViewport);\n'
    s += '    viewer.addEventListener("animation", showViewport);\n'
    s += '    Seadragon.Utils.addEvent(viewer.elmt, "mousemove", showMouse);\n'
    # s += '    Seadragon.eventManager.clearListeners("click");\n'
    s += '    Seadragon.Utils.addEvent(viewer.elmt, "mousedown", onMouseDown);\n'
    s += '    Seadragon.Utils.addEvent(viewer.elmt, "mouseup", onMouseUp);\n'
    # s += '    Seadragon.Utils.addEvent(viewer.elmt, "click", identifyRead);\n'
    s += '    viewer.addControl(makeFetcherControl(), Seadragon.ControlAnchor.TOP_RIGHT);\n'
    # s += '    viewer.addControl(makeAssemblyControl(), Seadragon.ControlAnchor.TOP_LEFT);\n'
    # s += '    viewer.addControl(makeReadnameControl(), Seadragon.ControlAnchor.TOP_LEFT);\n'
    # s += '    viewer.addControl(makeTemplateControl(), Seadragon.ControlAnchor.TOP_LEFT);\n'
    s += '    viewer.addEventListener("open", onViewerOpen);'
    s += '} else {\n'
    s += '    alert("Zoomtig not available");\n'
    s += '}'
    s += '}'
    s += 'Seadragon.Config.immediateRender = true;\n'
    s += 'Seadragon.Config.zoomPerClick = 1;\n'
    s += 'Seadragon.Utils.addEvent(window, "load", init);\n'
    s += '</script>\n'
    return s
    
def create_image(options, contig, contig_statistic, read_status, otype, pair_status):
    dzi_dir = '/dzi'
    if otype == 'readnames': dzi_dir = '/dzi_2'
    
    if otype == 'templates': dzi_dir = '/dzi_3'
    
    xml, image_params = zoomtig.process_contig(contig,
                                               options.output_dir + dzi_dir,
                                               read_status, otype, pair_status, options.num_processors)
    f = open(options.output_dir + dzi_dir + "/" +
             contig.name + ".dzi", "w")
    print >> f, xml
    f.close()

    html_f = open(options.output_dir + "/" + contig.name + ".html", "w");
    html = open(sys.path[0] + "/../contigo/static/html/" + "/zoomtig_template.html").read()
    html = html.replace('CONTIG_NAME', contig.name)
    js_str = prepare_zoomtig_js(contig_statistic.name, 
                               len(contig.quality), 
                               len(contig.consensus), 
                               image_params['padded_start'], 
                               image_params['padded_end'], 
                               image_params['max_depth'], 
                               image_params['height'], 
                               image_params['ruler_height'])
    html = html.replace('JAVASCRIPT_CODE', js_str)
    print >> html_f, html
    html_f.close()
    link = '<a href=\"%s.html\" target="_blank" title="View Read Assembly for %s">%s</a>' % (contig_statistic.name, 
                                                                                             contig_statistic.name,
                                                                                             contig_statistic.name
                                                                                             )
    
    #link = '<a href=\"contigo.html\" onclick=\"openZoomtig(event,\'dzi/%s.dzi\','\
    #    '\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\');\" title="View Read Assembly for this Contig">'\
    #    '%s</a>' % (contig_statistic.name, contig_statistic.name, 
    #                len(contig.quality), len(contig.consensus), 
    #                image_params['padded_start'], image_params['padded_end'], 
    #                image_params['max_depth'], image_params['height'], 
    #                image_params['ruler_height'], contig_statistic.name)
    return link

def create_image_2(options, contig, contig_statistic, read_status, otype, pair_status, pxbp):
    dzi_dir = '/dzi_3'
    print otype
    xml, image_params = zoomtig.process_contig_2(contig,
                                                 options.output_dir + dzi_dir,
                                                 read_status, otype, pair_status, pxbp)
    f = open(options.output_dir + dzi_dir + "/" +
             contig.name + ".dzi", "w")
    print >> f, xml
    f.close()
    
    link = '<a href=\"contigo.html\" onclick=\"switchTo(event,\'dzi/%s.dzi\','\
        '\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\');\" title="View Read Assembly for this Contig">'\
        '%s</a>' % (contig_statistic.name, contig_statistic.name, 
                    len(contig.quality), len(contig.consensus), 
                    image_params['padded_start'], image_params['padded_end'], 
                    image_params['max_depth'], image_params['height'], 
                    image_params['ruler_height'], contig_statistic.name)
    return link


def contig_json(options, contig):
    of = open(options.output_dir + "/json/" + contig.name + ".json", "w")
    print >> of, json.contig_data(contig)
    of.close()
    
def assembly_json(options, asm, num_scaffolds, scaffold_json):
    of = open(options.output_dir + "/json/assembly.js", "w")
    print >> of, "var CONTIGO = {};"
    print >> of, "CONTIGO.default_segment_width = %s;" % (zoomtig.DEFAULT_SEGMENT_WIDTH,)
    print >> of, "CONTIGO.num_scaffolds = %s;" % (num_scaffolds,)
    print >> of, json.contig_statistics(asm)
    print >> of, scaffold_json
    of.close()


def reads_to_taffydb(options, contig):
    
    sorted_reads = zoomtig.sort_reads(contig.reads)
    tiled_reads, shotgun_asm_height = zoomtig.tile_reads(sorted_reads, contig)
    
    r = re.compile('(["\'\\\\/])', re.VERBOSE)
    asm_width = contig.end - contig.start
    of = []
    for i in range(0, (asm_width / zoomtig.DEFAULT_SEGMENT_WIDTH) + 1):
        f = open(options.output_dir + "/json/" + contig.name + "_" + str(i) + "_reads.json", "w")
        print >> f, '(['
        of.append(f)
    for i, item in enumerate(tiled_reads):
        read, row = item
        ss = (read.padded_start - contig.start) / zoomtig.DEFAULT_SEGMENT_WIDTH
        se = (read.padded_end - contig.start) / zoomtig.DEFAULT_SEGMENT_WIDTH
        s = '{'
        s += 'name:"%s",' % (r.sub("\\\\\g<1>", read.name),)
        s += 'sequence:"%s",' % (read.sequence.replace('*',''),)
        s += 'padded_start:%s,' % (read.padded_start,)
        s += 'padded_length:%s,' % (read.padded_length(),)
        s += 'row:%s' % ((row + 1),)
        s += '}'
        if i < contig.num_reads: s += ','
        
        for j in range(ss, (se+1)):
            print >> of[j], s
    
    for f in of:
        print >> f, '])'
        f.close()
    return (asm_width / zoomtig.DEFAULT_SEGMENT_WIDTH) + 1

DEFAULT_INSERT_SIZE = 8000
DEFAULT_READ_LENGTH = 500
WIDTH_FACTOR = 500
FEAT_HEIGHT = 6
INTER_TEMPLATE_PAD = WIDTH_FACTOR * 2
# SCAFFOLD IMAGE

def calculate_segments(asm_width):
    ''' Calculates how to segment up the contig. '''
    
    i = 0
    segments = []
    DEFAULT_SCAFFOLD_SEGMENT_WIDTH = zoomtig.DEFAULT_SEGMENT_WIDTH * WIDTH_FACTOR
    if DEFAULT_SCAFFOLD_SEGMENT_WIDTH >= asm_width:
        
        segments.append([0, (asm_width - 1), asm_width])
    else:
        
        while i * DEFAULT_SCAFFOLD_SEGMENT_WIDTH < asm_width:

            segment_start = i * DEFAULT_SCAFFOLD_SEGMENT_WIDTH
            segment_end = segment_start + DEFAULT_SCAFFOLD_SEGMENT_WIDTH
            if segment_end >= asm_width:
                segment_end = asm_width
            segment_size = segment_end - segment_start
            segments.append([segment_start, segment_end, segment_size])
            i += 1

    if segments[-1][2] < zoomtig.BASES_PER_TILE: 
        # Merge small right-most segment and second-to-last segment
        s = segments.pop(-1)
        segments[-1][1] += s[2]
        segments[-1][2] += s[2]
    
    if len(segments) > 1 and (len(segments) % 2) != 0:
        # if odd segment count, merge last and second-to-last
        s = segments.pop(-1)
        segments[-1][1] += s[2]
        segments[-1][2] += s[2]
    
    return segments



def tile_templates(templates):
    ''' Given hash of reads, determines row placement so reads do not overlap.
    Returns array of tuples (read_name, row)'''

    
     # space between reads, maybe use to display read name in
    
    current_ends = [0] # stores current end of right-most read in row
    
    template_start, template_end, template_name = templates.pop(0)
    current_ends[0] = template_end # + len(read.name)# current end of right-most read in first row
    tiled_templates = [(template_name, 0, template_start, template_end)] # stores tiles reads
    while templates: # while we still have reads to process
        template_start, template_end, template_name = templates.pop(0)
        is_placed = False
        for (i, row_end) in enumerate(current_ends):
            if template_start > (row_end + INTER_TEMPLATE_PAD): # if read fits on row
                current_ends[i] = template_end # + len(read.name)# update current end
                tiled_templates.append((template_name, i, template_start, template_end)) # append to tiled reads list
                is_placed = True # mark currently processed read as placed
                break
        if not is_placed: # if current read not placed ...
            current_ends.append(template_end) #+ len(read.name)) # add entry to current_ends
            i = len(current_ends) - 1 # how may rows now?
            tiled_templates.append((template_name, i, template_start, template_end)) # add read to tiled reads
            
    return tiled_templates, len(current_ends)


def segment_templates(templates, segments):
    ''' Segment reads into groups by chunk of SEGMENT_SIZE.
    Requied to print large images. '''
    segmented_templates = []
    for i in range(len(segments)): segmented_templates.append([])
    
    for template, row, template_start, template_end in templates:
        in_segments = zoomtig.get_segments(template_start, template_end, segments)
        for i in in_segments: segmented_templates[i].append((template, row, template_start, template_end))

    return segmented_templates

def get_template_coords(template, contigs, status):
    ss, se, st = None, None, None
    if (template.right_contig != status):
        if template.right_dir == '+':
            ss, se, st = [contigs[template.right_contig].object_beg + template.right_pos,
                          contigs[template.right_contig].object_beg + template.right_pos + DEFAULT_INSERT_SIZE, '+']
        else:
            ss, se, st = [contigs[template.right_contig].object_beg + template.right_pos - DEFAULT_INSERT_SIZE,
                          contigs[template.right_contig].object_beg + template.right_pos, '-']
    else:
        
        if template.left_dir == '+':
            ss, se, st = [contigs[template.left_contig].object_beg + template.left_pos,
                          contigs[template.left_contig].object_beg + template.left_pos + DEFAULT_INSERT_SIZE, '+']
        else:
            ss, se, st = [contigs[template.left_contig].object_beg + template.left_pos - DEFAULT_INSERT_SIZE,
                          contigs[template.left_contig].object_beg + template.left_pos, '-']
    return ss, se, st
       

def get_template_scaffold_coords(template, contigs):
    ss, se, st, scl = None, None, None, []
    
    if (template.status == 'BothUnmapped'):
        ss, se, st = None, None, None
        exit("Template status is BothUnmapped but has one end that maps to a contig")
    
    elif (template.status == 'OneUnmapped'):
        ss, se, st = get_template_coords(template, contigs, "Unmapped")
        
    elif (template.status == 'MultiplyMapped'):
        ss, se, st = get_template_coords(template, contigs, "Repeat")
        
    elif (template.status == 'SameContig'):
        scl = [(contigs[template.left_contig].object_beg + template.left_pos),
               (contigs[template.right_contig].object_beg + template.right_pos)]
        scl.sort()
        ss, se, st = scl[0], scl[1], '+'
    
    elif (template.status == 'Link'):
        # same scaffold
        if contigs.get(template.left_contig) and contigs.get(template.right_contig):
            scl = [(contigs[template.left_contig].object_beg + template.left_pos),
                   (contigs[template.right_contig].object_beg + template.right_pos)]
            scl.sort()
            ss, se, st = scl[0], scl[1], '+'
        else:
            if contigs.get(template.left_contig):
                ss, se, st = get_template_coords(template, contigs, template.right_contig)
            else:
                ss, se, st = get_template_coords(template, contigs, template.left_contig)
            
    elif (template.status == 'FalsePair'):
        # WHAT IF STRAND ARE NOT CONSISTENT?
        if contigs.get(template.left_contig) and contigs.get(template.right_contig):
            scl = [(contigs[template.left_contig].object_beg + template.left_pos),
                   (contigs[template.right_contig].object_beg + template.right_pos)]
            scl.sort()
            ss, se, st = scl[0], scl[1], '+'
        
        else:
            print template.template
            if contigs.get(template.left_contig):
                ss, se, st = get_template_coords(template, contigs, template.right_contig)
            else:
                ss, se, st = get_template_coords(template, contigs, template.left_contig)
                
        
    else:
        exit("Template status %s not defined" % (template.status,))
    return [ss, se, template.template, None]

def draw_arrow(draw, x, y):
    # draw a directed arrow: ##-->
    # draw_box
    draw.rectangle()
    # draw line
    draw.line()
    #draw triangle
    draw.polygon()

def draw_segment(img_width, img_height, segment, templates, image_name, pair_status):
    segment_start, segment_end, segment_size = segment
    img = Image.new("RGB", (img_width, img_height), zoomtig.IMG_BG)
    draw = ImageDraw.Draw(img)
    for template, row, template_start, template_end in templates:
        x1 = (template_start - segment_start) / WIDTH_FACTOR
        y1 = (row * FEAT_HEIGHT)
        
        x2 = (template_end - segment_start) / WIDTH_FACTOR
        y2 = (row + 1) * FEAT_HEIGHT
        rgb = (0,0,0)
        status = pair_status[template].status
        if status == 'SameContig': rgb = (165,165,165)
        if status == 'Link': rgb = (165,0,0)
        if status == 'FalsePair': rgb = (0,165,0)
        if status == 'MultiplyMapped': rgb = (0,0,165)
        if status == 'OneUnmapped': rgb = (255,255,255)
        
        
        print status
        draw.rectangle((x1, y1, x2, y2), fill=rgb, outline=(255,0,0))
        
    img.save(image_name + ".png")

def draw_scaffolds(options, pair_status):
    
    if options.scaffold and  \
            os.path.exists(options.input_dir + "/" + options.scaffold):
        scaffolds = agp.load(open(options.input_dir + "/" + options.scaffold))
        # for each scaffold
        for object_id in scaffolds.objects:
            scaffold = scaffolds.objects[object_id]
            contigs = {}
            scaffold_templates = []
            # for each contig/gap (obj) in scaffold
            for obj in scaffold:
                # if not a gap
                if obj.component_type != 'N':
                    contigs[obj.component_id] = obj
            # get templates that have at least one end in a contig in this scaffold
            for tn in pair_status:
                template = pair_status[tn]
                if contigs.get(template.left_contig) or contigs.get(template.right_contig):
                    scaffold_templates.append(get_template_scaffold_coords(template, contigs))
            
            scaffold_templates.sort()
            # print scaffold_templates
            exit(1)
            tiled_templates, asm_height =  tile_templates(scaffold_templates)
            segments = calculate_segments(scaffolds.lengths[object_id])
            print segments
            segmented_templates = segment_templates(tiled_templates, segments)
            img_height = asm_height * FEAT_HEIGHT
            img_width = (scaffolds.lengths[object_id]) / WIDTH_FACTOR
            images = []
            for i, segment in enumerate(segments):
                image_name = options.output_dir + "/%s" % (i)
                print image_name
                images.append(image_name)
                segment_start, segment_end, segment_size = segment
                img_width = segment_size / WIDTH_FACTOR
                print img_width, img_height
                draw_segment(img_width, img_height, segment, segmented_templates[i], image_name, pair_status)
            
    else:
        sys.stderr.write(" FILE: %s does not exist, skipping ... " % options.scaffold)

    sys.stderr.write("done.\n")

# END SCAFFOLD IMAGE

def run_contigo(options):
    scaffold_table, num_scaffolds, scaffold_json = create_scaffold_table(options)
    read_status = status.process_readstatus(options)
    pair_status = status.process_pairstatus(options)
    asm = assembly.Assembly()
    asm.update_pair_statistics(pair_status)
    
    contig_table = render.contig_table_header()
    
    asm.pxbp = zoomtig.SMALL_FONT_WIDTH
    if asm.num_templates > 0:
        asm.pxbp = 500/asm.avg_insert_size
    c = 0
    
    for contig in assembly.load_ace(options.input_dir + "/" +
                                    options.assembly, options.platform):
        
        sys.stderr.write("%s %s %s " % (contig.name, len(contig.consensus), contig.num_reads))
        # if not(contig.name in ('contig00308', 'contig00251', 'contig00295', 'contig00300')): continue
        # if contig.name != 'contig00001': continue
        if options.max_contig_num and options.max_contig_num == c: break
        
        if options.contig_name and (options.contig_name != contig.name):
            sys.stderr.write("\n")
            continue

        if contig.length() < options.min_contig_len:
            sys.stderr.write (" ... skipping, length < %s" % (options.min_contig_len,))
            sys.stderr.write("\n")    
            continue

        c += 1
        contig_statistic = assembly.ContigStatistic(
            contig.name, contig.length(), contig.num_reads,
            contig.base_counts(), contig.depth_histogram(),
            contig.qual_histogram(), contig.low_qual_count(),
            contig.read_length_histogram()
            )
        
        contig_statistic.add_read_stats(*(contig.read_stats()))
        if False:
            sys.stderr.write(" %s\t%s\t%s\t%s\t%0.2f\t%s\t%0.2f\t%s\n" % (contig.name,
                                                                          contig.length(), 
                                                                          len(contig.reads),
                                                                          contig_statistic.avg_depth(),
                                                                          contig_statistic.avg_ins_size(),
                                                                          contig_statistic.med_ins_size(),
                                                                          contig_statistic.avg_paired_depth(),
                                                                          contig_statistic.med_paired_depth()
                                                                          ))
        asm.contig_statistics.append(contig_statistic)
        link = '<a href="#" onclick="alert(\'Zoomtig not available in this version.\'); return false;">%s</a>' % contig.name
        if not options.noimage:
            link = create_image(options, contig, contig_statistic, read_status, 'assembly', pair_status)
            # link_2 = create_image(options, contig, contig_statistic, read_status, 'readnames', pair_status)
            # link_3 = create_image_2(options, contig, contig_statistic, read_status, 'templates', pair_status, asm.pxbp)
        else:
            contig.start, contig.end = zoomtig.adjust_contig_coordinates(contig.reads)

        contig_statistic.num_segments = reads_to_taffydb(options, contig)
        contig_json(options, contig)
        
        contig_table += render.contig_table_row(contig_statistic, link)
        sys.stderr.write("\n")
    contig_table += render.contig_table_footer()
    assembly_json(options, asm, num_scaffolds, scaffold_json)
    
    draw_scaffolds(options, pair_status)
    
    f = open(options.output_dir + "/contig_table.html", "w")
    print >> f, contig_table
    f.close()
    f = open(options.output_dir + "/scaffold_table.html", "w")
    print >> f, scaffold_table
    f.close()
    f = open(options.output_dir + "/filter_options.html", "w")
    if os.path.exists(options.input_dir + "/" + options.scaffold):
        print >> f, agp.make_filter_option_html(options)
    f.close()
    
################
# MAIN PROGRAM #
################
    
def main():
    
    (options, args) = parse_options()
    init(options)
    if options.mode != 'interface':
        run_contigo(options)
    update_interface(options)
    sys.stderr.write("done ... output in %s\n" % (options.output_dir))
    
if __name__ == '__main__':
    main()

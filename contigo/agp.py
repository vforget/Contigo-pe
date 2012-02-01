# Classes and functions to parse and store data from an AGP formatted file.

import re

class Component:
    ''' class for component line '''
    def __init__(self, object_id,  object_beg, object_end, part_number, component_type, component_id, component_beg,  component_end, orientation):
        self.object_id = object_id
        self.object_beg = int(object_beg)
        self.object_end = int(object_end)
        self.part_number = int(part_number)
        self.component_type = component_type
        self.component_id = component_id
        self.component_beg = int(component_beg)
        self.component_end = int(component_end)
        self.orientation = orientation
    
    def __str__(self):
        return "\t".join([str(x) for x in [self.object_id,
                                    self.object_beg,
                                    self.object_end,
                                    self.part_number,
                                    self.component_type,
                                    self.component_id,
                                    self.component_beg,
                                    self.component_end,
                                    self.orientation]])
    def len(self):
        return (self.component_end - self.component_beg + 1)
    
    
class Gap:
    ''' class for gap line '''
    def __init__(self, object_id,  object_beg, object_end, part_number, component_type, gap_length, gap_type, linkage):
        self.object_id = object_id
        self.object_beg = int(object_beg)
        self.object_end = int(object_end)
        self.part_number = int(part_number)
        self.component_type = component_type
        self.gap_length = int(gap_length)
        self.gap_type = gap_type
        self.linkage = linkage
        
    def __str__(self):
        return "\t".join([str(x) for x in [self.object_id,
                                           self.object_beg,
                                           self.object_end,
                                           self.part_number,
                                           self.component_type,
                                           self.gap_length,
                                           self.gap_type,
                                           self.linkage]])
class Scaffold:
    def __init__(self):
        self.objects = {}
        self.lengths = {}

    def __getitem__(self, i):
        self.objects[i]
    
    def __setitem__(self, i, j):
        if not self.objects.get(i): 
            self.objects[i] = []
            self.lengths[i] = 0
        self.objects[i].append(j)
        self.lengths[i] += (j.object_end - j.object_beg + 1)

    def num_contigs(self, name):
        return len([x for x in self.objects[name] if x.component_type != 'N'])
    
    def length(self, name):
        return self.lengths[name]
    
        
        
# def load(fh):
#     ''' Parses AGP format.
#     Returns hash key\'ed on scaffold name. '''

#     scaffolds = {}

#     for line in fh:
#         columns = line.split()
#         component_type = columns[4]
#         object_id = columns[0]
#         if not scaffolds.get(object_id): scaffolds[object_id] = []
#         if component_type != "N": # component
#             scaffolds[object_id].append(Component(*columns))
#         else: # gap
#             scaffolds[object_id].append(Gap(*columns))
#     return scaffolds

def load(fh):
    ''' Parses AGP format.
    Returns hash key\'ed on scaffold name. '''

    scaffolds = Scaffold()
    lengths = {}
    
    for line in fh:
        columns = line.split()
        component_type = columns[4]
        object_id = columns[0]
        item = None
        if component_type != "N": # component
            item = Component(*columns)
        else: # gap
            item = Gap(*columns)
        
        scaffolds[object_id] = item
    
    return scaffolds

def make_scaffold_table_row(sid, item):
    
    rd = None
    r = re.compile('(scaffold|contig)[0]*')
    is_scaffold = False
    if item.component_type == "W":
        link = item.component_id # r.sub('ctg', item.component_id)
        
        rd = [sid,
              # r.sub('scf', item.object_id),
              item.object_id,
              item.object_beg,
              item.object_end,
              (item.object_end - item.object_beg),
              link,
              item.orientation.replace('+', 'U').replace('-', 'C')
              ]
        is_scaffold = True
    elif item.component_type == "N":
        rd = [sid,
              # r.sub('scf', item.object_id),
              item.object_id,
              item.object_beg,
              item.object_end,
              item.gap_length,
              "gap",
              'G'
              ]
    if not rd: exit("Component type \"%s\" not supported" % (item.component_type,))
    return rd, is_scaffold


def scaffold_to_json(scaffold):
    contigs = [item.component_id for item in scaffold if item.component_type != 'N']
    gaps = [item.gap_length for item in scaffold if item.component_type == 'N']
    return ('[%s]' % (",".join('"' + x + '"' for x in contigs))), ('[%s]' % (",".join(str(x) for x in gaps)))
    
def make_filter_option_html(options):

    scaffolds = load(\
        open(options.input_dir + "/" + options.scaffold))
    sid = 0
    rows = []
    num_scaffolds = 0
    html = []
    for length, name in sorted([(value,key) for (key,value) in scaffolds.lengths.items()], reverse=True):
        scaffold = scaffolds.objects[name]
        html.append('<option value="%s">&nbsp;&nbsp;- %s %s %s</option>' % (name, name, 
                                                                           scaffolds.num_contigs(name), 
                                                                           length))
        num_scaffolds += 1
        c = 0
        for item in scaffold:
            if item.component_type != 'N':
                html.append('<option value="%s">&nbsp;&nbsp;&nbsp;&nbsp;%s %s</option>' % (item.component_id, item.component_id, item.len()))
    html = "\n".join(html)
    return html

def make_scaffold_table(options):

    scaffolds = load(\
        open(options.input_dir + "/" + options.scaffold))
    sid = 0
    rows = []
    num_scaffolds = 0
    for name in scaffolds.objects: 
        scaffold = scaffolds.objects[name]
        num_scaffolds += 1
        c = 0
        for item in scaffold:
            if item.component_type != 'N':
                c += 1
        rows.append(['<a href=\"%s.html\" target="_blank" title="View Template Assembly for %s">%s</a>' % (name, name, name), 
                     '<a href="contigo.html" onclick="loadScaffoldSequence(\'%s\'); return false;" title="View Contig Sequences in FASTA format">%s</a>' % (name, scaffolds.lengths[name]),
                     '<a href="contigo.html" onclick="loadScaffoldContigs(\'%s\'); return false;" title="View Contig Sequences in FASTA format">%s</a>' % (name, c)
                     ])
        
    return rows, num_scaffolds,

   
def scaffold_table_header():
    s = '<table id="scaffold_table">'
    s += """<colgroup>
<col style="width: 30px;">
<col style="width: 30px;">
<col style="width: 30px;">
<col style="width: 30px;">
</colgroup>
<tr>
<td title="Scaffold name">Scaffold</td>
<td title="Length of Scaffold">Length</td>
<td title="Number of Contigs in Scaffold">Num. Contigs</td>
</tr>"""
    return s

def scaffold_table_row(row_data):
    s = "<tr><td>"
    s += "</td><td>".join([str(x) for x in row_data])
    s += "</td></tr>"
    return s
    
def scaffold_table_footer():
    s = '</table>'
    return s
    
  
def make_json(options):
    scaffolds = load(\
        open(options.input_dir + "/" + options.scaffold))
    strings = []
    for name in scaffolds.objects: 
        scaffold = scaffolds.objects[name]
        contig_json, gap_json = scaffold_to_json(scaffold)
        strings.append('"%s": { contigs: %s, gaps: %s }' % (name, contig_json, gap_json))
        
    return 'CONTIGO.scaffolds = { %s };' % (','.join(strings))

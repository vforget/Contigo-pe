#!/usr/bin/python
# Filename: render.py

import datetime
import sys

def html_header():
    return """ TEXT """

def html_body():
    return """
Manual
Why the name?
Why Yet-Another-Assembly Viewer?
How's it made?
"""


def html_footer():
    return " TEXT "


def interface(of, options, contig_table, scaffold_table, filter_options):
    html = open(sys.path[0] + "/template.html").read()
    html = html.replace("CONTIG_TABLE_HTML", contig_table)
    html = html.replace("SCAFFOLD_TABLE_HTML", scaffold_table)
    html = html.replace("FILTER1_OPTIONS", filter_options)
    html = html.replace("DATE_CREATED", datetime.datetime.now().strftime("%d %b, %Y"))
    html = html.replace("ASSEMBLY_NAME", options.assembly_name)
    
    print >> of, html
    
def contig_table_header():
    s = '<table id="contig_table">'
    s += '<colgroup><col style="width: 30px;"><col style="width: '\
        '30px;"><col style="width: 30px;"><col style="width: 30px;">'\
        '<col style="width: 30px;"></colgroup><tr><td title="Sort by contig name">Contig</td><td title="Sort by contig length">Length'\
        '</td><td title="Sort by number of reads assembled in contig">No.<br/>Reads</td><td title="Sort by Read Depth">Read<br/>Depth</td><td title="Sort by percentage of bases < Q64">%&lt;Q64</td><td title="Sort by %GC">%GC</td>'\
        '<td title="Sort by Template Depth (if paired)">Templ.<br/>Depth</td><td title="Sort by Avg. Insert Size (if paired)">Avg.<br/>Insert</td>'\
        '</tr>'
    return s
    

def contig_table_row(contig_statistic, link):
    
    s = "<tr>"
    s += "<td>"
    s += '</td><td>'.join([
        link,
        '<a href="contigo.html" onclick="loadFasta(\'%s\'); return false;" title="View Contig Sequence in FASTA format">%s</a>' % (contig_statistic.name, str(contig_statistic.length),),
        '<a href="contigo.html" onclick="loadReads(\'%s\', %s); return false;" title="View Contig Read Sequences in FASTA format">%s</a>' % (contig_statistic.name, contig_statistic.num_segments, contig_statistic.num_reads,),
        ("%0.2f" % contig_statistic.avg_depth()),
        '<a href="contigo.html" onclick="loadQuality(\'%s\'); return false;" title="View Contig Qualities FASTA format">%0.2f</a>' % (contig_statistic.name, contig_statistic.perc_lowqual(),),
        ("%0.2f" % contig_statistic.perc_gc())])
    s += "</td>"
    s += "<td>%0.2f</td><td>%0.2f</td>" % (contig_statistic.avg_paired_depth(), \
                                           contig_statistic.avg_ins_size()/1000
                                           )
    s += "</tr>"
    return s

def contig_table_footer():
    return "</table>"




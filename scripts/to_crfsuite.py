#!/usr/bin/env python
"""
Code originally from CRFsuite, modified by Joseph Turian to include representations.

You can enter combinations of brown and/or embeddings representations
to add to the feature set.
"""

import sys, string

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-b", "--brown", dest="brown", action="append", help="brown clusters to use")
parser.add_option("-e", "--embeddings", dest="embeddings", action="append", help="embeddings to use")
parser.add_option("-p", "--prefixes", dest="prefixes", default="4,6,10,20", help="brown prefixes")

(options, args) = parser.parse_args()
assert len(args) == 0

prefixes = [int(s) for s in string.split(options.prefixes, sep=",")]

if options.brown is None: options.brown = []

from common.file import myopen
import string
word_to_cluster = []
for i, brownfile in enumerate(options.brown):
    print >> sys.stderr, "Reading Brown file: %s" % brownfile
    word_to_cluster.append({})
    assert len(word_to_cluster) == i+1
    for l in myopen(brownfile):
        cluster, word, cnt = string.split(l)
        word_to_cluster[i][word] = cluster

def output_features(fo, seq):
    for i in range(2, len(seq)-2):
        fs = []
        
        fs.append('U00=%s' % seq[i-2][0])
        fs.append('U01=%s' % seq[i-1][0])
        fs.append('U02=%s' % seq[i][0])
        fs.append('U03=%s' % seq[i+1][0])
        fs.append('U04=%s' % seq[i+2][0])
        fs.append('U05=%s/%s' % (seq[i-1][0], seq[i][0]))
        fs.append('U06=%s/%s' % (seq[i][0], seq[i+1][0]))

        for cluster in word_to_cluster:
            for name, pos in zip(["U00", "U01", "U02", "U03", "U04"], [i-2,i-1,i,i+1,i+2]):
                if seq[pos][0] not in cluster: continue
                for p in prefixes:
                    fs.append("%sbp%d=%s" % (name, p, cluster[seq[pos][0]][:p]))


        fs.append('U10=%s' % seq[i-2][1])
        fs.append('U11=%s' % seq[i-1][1])
        fs.append('U12=%s' % seq[i][1])
        fs.append('U13=%s' % seq[i+1][1])
        fs.append('U14=%s' % seq[i+2][1])
        fs.append('U15=%s/%s' % (seq[i-2][1], seq[i-1][1]))
        fs.append('U16=%s/%s' % (seq[i-1][1], seq[i][1]))
        fs.append('U17=%s/%s' % (seq[i][1], seq[i+1][1]))
        fs.append('U18=%s/%s' % (seq[i+1][1], seq[i+2][1]))
        
        fs.append('U20=%s/%s/%s' % (seq[i-2][1], seq[i-1][1], seq[i][1]))
        fs.append('U21=%s/%s/%s' % (seq[i-1][1], seq[i][1], seq[i+1][1]))
        fs.append('U22=%s/%s/%s' % (seq[i][1], seq[i+1][1], seq[i+2][1]))

        fo.write('%s\t%s\n' % (seq[i][2], '\t'.join(fs)))
    fo.write('\n')

def encode(x):
    x = x.replace('\\', '\\\\')
    x = x.replace(':', '\\:')
    return x
    
fi = sys.stdin
fo = sys.stdout

d = ('', '', '')

seq = [d, d]
for line in fi:
    line = line.strip('\n')
    if not line:
        seq.append(d)
        seq.append(d)
        output_features(fo, seq)
        seq = [d, d]
    else:
        fields = line.strip('\n').split(' ')
        seq.append((encode(fields[0]), encode(fields[1]), encode(fields[2])))
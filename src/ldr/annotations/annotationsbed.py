#!/usr/bin/env python

import gzip
import tempfile

class AnnotationsBed:

    def __init__(self, annotations):
        self.annotations = annotations
    
    def __enter__(self):
        self.tempfile = tempfile.NamedTemporaryFile('wt')
        with (gzip.open if self.annotations.endswith(".gz") else open)(self.annotations, 'rt') as f:
            f.readline()
            for line in f:
                l = line.strip().split('\t')
                self.tempfile.write("chr%s\t%d\t%d\t%s\n" % (l[0], int(l[1]), int(l[1]) + 1, l[2]))
        self.tempfile.flush()
        return self.tempfile
    
    def __exit__(self, *args):
        self.tempfile.close()

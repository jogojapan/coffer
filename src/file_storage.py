# -*- coding: utf-8 -*-

'''
Created on 2011/04/18

@author: gollerjo
'''

import os.path
from os import listdir
import re
import tarfile
import subprocess

FILE_PRE      = u'block_'
FILE_EXT      = u'.tar'
COMPR_EXT     = u'.bz2'
FILE_PATTERN  = re.compile(u'^' + re.escape(FILE_PRE) + u'(\d+)' + \
                          re.escape(FILE_EXT) + u'(?:' + \
                          re.escape(COMPR_EXT) + u')?')
COMPR_PATTERN = re.compile(re.escape(COMPR_EXT) + u'$')

# Maximum size in bytes of a block. When reached, a new block
# will be started.
DEFAULT_MAX_BLOCK_SIZE = 10,485,760

class Bucket:
    '''
    Holds all information related to a bucket, i.e. a directory
    of the file store.
    '''
    
    def __init__(self,
                 external_processes,
                 path,
                 max_block_size = DEFAULT_MAX_BLOCK_SIZE,
                 bzip2_path     = '/usr/bin/bzip2'):
        self._external_processes = external_processes
        self._bzip2_path         = bzip2_path
        if not os.path.isdir(path):
            raise "Invalid bucket path '%s'" % path
        self._current_fileno = 0
        self._path           = path
        self._current_size   = 0
        self._max_block_size = max_block_size
        # Determine the largest file number used in the bucket.
        exists = False
        for filename in listdir(path):
            m = FILE_PATTERN.match(filename)
            if m:
                current_fileno = int(m.group(1))
                if current_fileno > self._current_fileno:
                    if COMPR_PATTERN.search(filename):
                        self._current_fileno = current_fileno + 1
                        exists = False
                    else:
                        self._current_fileno = current_fileno
                        exists = True
        if exists:
            # If the current output file exists, we need to determine its size
            abspath = self.generate_filename(self._current_fileno,False)
            if os.stat(abspath).st_size >= self._max_block_size:
                self.compress(abspath)
                self._current_fileno += 1
                exists = False

    def compress(self,abspath):
        process = subprocess.Popen([self._bzip2_path,abspath])
        self._external_processes.append(process)

    def generate_filename(self,fileno,is_compressed = False):
        '''
        Ancillary function that generates absolute paths and filenames
        for individual blocks.
        '''
        filename = os.path.join(self._path,
                                u'%s%d%s' % (FILE_PRE,fileno,FILE_EXT))
        if is_compressed:
            filename += COMPR_EXT
        return filename

    def store(self,unicode_text):
        '''
        Store a piece of text in the current block. Create a new block if necessary.
        '''
        filename = self.generate_filename(self._current_fileno,False)
        if os.path.exists(filename):
            channel = tarfile.open(name=filename,mode='a')
        else:
            channel = tarfile.open(name=filename,mode='w')


class FileStorage(object):
    '''
    Implements a store for text files. The store is organized using
    one layer of buckets, and one or more .tar.bz2 files in each bucket.
    When a .tar.bz2 reaches a certain (configurable) size limit,
    another one is added.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
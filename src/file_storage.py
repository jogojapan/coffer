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
import time
from os_specific.userinfo import user_info
from StringIO import StringIO

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

def escape_path(path):
    return path.replace('/','_')

class FileStorageException(Exception):
    def __init__(self,message):
        self._message = message
    def __repr__(self):
        return self._message

class Bucket:
    '''
    Holds all information related to a bucket, i.e. a directory
    of the file store. A bucket holds all files belonging to one
    particular source feed.
    '''
    
    def __init__(self,
                 external_processes,
                 path,
                 max_block_size = DEFAULT_MAX_BLOCK_SIZE,
                 bzip2_path     = '/usr/bin/bzip2'):
        self._external_processes = external_processes
        self._bzip2_path         = bzip2_path
        if not os.path.exists(path):
            os.mkdir(path)
        elif not os.path.isdir(path):
            raise FileStorageException("Invalid bucket path '%s' (not a directory)" % path)
        self._current_fileno = 0
        self._current_size   = 0
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
            self._current_size = os.stat(abspath).st_size
            if self._current_size >= self._max_block_size:
                self.compress(abspath)
                self._current_fileno += 1
                exists = False
                self._current_size = 0
        
        # This maintains a mapping from block ids to sets of filenames,
        # i.e. a directory of all files stored in the tar blocks. This
        # will be filled with data dynamically, on demand.
        self._text_id_directory = {}

    def compress(self,abspath):
        '''
        Spawn an external process that compresses a block.
        '''
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

    def store_all(self,text_objs):
        '''
        Store a list of text objects (each an id and a unicode text) in the
        current block. Create a new block if necessary.
        '''
        ui = user_info()
        filename = self.generate_filename(self._current_fileno,False)
        if os.path.exists(filename) and os.stat(filename).st_size != 0:
            channel = tarfile.open(name=filename,mode='a')
        else:
            channel = tarfile.open(name=filename,mode='w')
        for (text_id,unicode_text) in text_objs:
            encoded_text = unicode_text.encode('utf-8')
            tarinfo = tarfile.TarInfo(escape_path(text_id))
            tarinfo.size = len(encoded_text)
            tarinfo.mtime = time.time()
            (tarinfo.uid,tarinfo.gid) = ui
            channel.addfile(tarinfo,StringIO(encoded_text))
            if self._current_fileno in self._text_id_directory:
                self._text_id_directory[self._current_fileno].add(text_id)
            self._current_size += len(encoded_text)
            if self._current_size >= self._max_block_size:
                channel.close()
                self.compress(filename)
                self._current_fileno += 1
                filename = self.generate_filename(self._current_fileno,False)
                channel = tarfile.open(name=filename,mode='w')
        channel.close()

    def retrieve(self,text_id):
        '''
        Retrieve the file designated by text_id. The function searches all
        tar blocks, but shortcuts the search through the use of the
        _text_id_directory. The file list of any tar block that has been
        searched earlier is stored in _text_id_directory so there is no need
        to open the tar file in this case. Tar blocks that have not been
        searched earlier will be opened and their members list be stored
        in _text_id_directory.
        @param text_id: The non-escaped version of the id of the RSS item we
              are looking for.
        @return: A file object that gives access to the contents for text_id,
              or None if text_id was not found in any tar block.
        '''
        for fileno in range(self._current_fileno+1):
            channel = None
            is_in_fileno = False
            # Check whether the text_id is in the block designated by fileno:
            if fileno in self._text_id_directory:
                is_in_fileno = (text_id in self._text_id_directory[fileno])
            else:
                filename = self.generate_filename(fileno,(fileno < self._current_fileno))
                if os.path.exists(filename):
                    mode = 'r'
                    if fileno < self._current_fileno:
                        mode = 'r|bz2'
                    channel = tarfile.open(name=filename,mode=mode)
                    memberset = set([x.name for x in channel.getmembers()])
                    self._text_id_directory[fileno] = memberset
                    if text_id in memberset:
                        is_in_fileno = True
                    else:
                        channel.close()
                        channel = None
                        continue
            if is_in_fileno:
                if channel is None:
                    mode = 'r'
                    if fileno < self._current_fileno:
                        mode = 'r|bz2'
                    channel = tarfile.open(name=filename,mode=mode)
                return channel.extractfile(escape_path(filename))
                channel.close()
        return None

    def items(self):
        for fileno in range(self._current_fileno+1):
            channel = None
            # Check whether the text_id is in the block designated by fileno:
            if fileno in self._text_id_directory:
                for text_id in self._text_id_directory[fileno]:
                    yield text_id
            else:
                filename = self.generate_filename(fileno,(fileno < self._current_fileno))
                if os.path.exists(filename):
                    mode = 'r'
                    if fileno < self._current_fileno:
                        mode = 'r|bz2'
                    channel = tarfile.open(name=filename,mode=mode)
                    memberset = set([x.name for x in channel.getmembers()])
                    channel.close()
                    self._text_id_directory[fileno] = memberset
                    for text_id in memberset:
                        yield text_id


class FileStorage(object):
    '''
    Implements a store for text files. The store is organized using
    one layer of buckets, and one or more .tar.bz2 files in each bucket.
    When a .tar.bz2 reaches a certain (configurable) size limit,
    another one is added.
    '''

    def __init__(self,
                 external_processes,
                 path,
                 max_block_size = DEFAULT_MAX_BLOCK_SIZE,
                 bzip2_path     = '/usr/bin/bzip2'):
        self._external_processes = external_processes
        self._path               = path
        self._max_block_size     = max_block_size
        self._bzip2_path         = bzip2_path
        
        # Create a directory of buckets
        self._directory = {}
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            # If the main path refers to an existing file directory,
            # all its subdirectories are configured as existing buckets.
            if not os.path.isdir(path):
                raise FileStorageException("'%s' is a file but should be a directory." % path)
            for entry in os.listdir(path):
                abspath = os.path.join(path,entry)
                if os.path.isdir(abspath):
                    self._directory[entry] = Bucket(external_processes,
                                                    abspath,
                                                    max_block_size,
                                                    bzip2_path)

    def store_all(self,text_objs_dict):
        '''
        @param text_objs_dict: A hash of source-feed -> [(text_id,unicode_text),..]
            mappings.
            The source-feed will be used as a subdirectory name that should be
            specific to the feed the text comes from. The text_id must
            correspond to the unique ID of the text (usually comes as 'id'
            meta field from the RSS/Atom item. The unicode_text is the
            text downloaded from the 'link' the comes along with the RSS/Atom
            item. It is generally formatted in HTML.
        '''
        for source_feed,text_objs in text_objs_dict.iteritems():
            if source_feed not in self._directory:
                self._directory[source_feed] = Bucket(self._external_processes,
                                                      os.path.join(self._path,source_feed),
                                                      self._max_block_size,
                                                      self._bzip2_path)
            self._directory[source_feed].store_all(text_objs)

    def retrieve(self,source_feed,text_id):
        '''
        Return the contents of a particular item stored for a particular
        RSS source feed.
        @param source_feed: The id of the source RSS feed.
        @param text_id: The non-escaped version of the id of the RSS item we
              are looking for.
        @return: A file object that gives access to the contents for text_id,
              or None if text_id was could not be found.
        '''
        if source_feed in self._directory:
                return self._directory[source_feed].retrieve(text_id)

    def items(self,source_feed):
        '''
        Retrieve an iterator for the list of items for the given
        source feed id.
        '''
        if source_feed in self._directory:
            return self._directory[source_feed].items()
        else:
            return None

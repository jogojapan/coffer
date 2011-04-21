import codecs

encoding_name_map = {'euc-jp':'euc_jp'}

def get_decoder(encoding,default = 'utf-8'):
    '''
    Returns a decoder for the given encoding.
    @param encoding: A string that specified an encoding. The
        string must correspond to one of the encoding names or aliases
        registered in the Python codecs library, or it must match one
        of the keys of the encoding_name_map dictionary defined
        in this langid module.
    @param default: The encoding that will be assumed if the
        one specified in 'encoding' does not exist. Make sure you define
        a default that actually exists. Otherwise a LookupError
        exception will be raised.
    '''
    if encoding in encoding_name_map:
        encoding = encoding_name_map[encoding]
    try:
        decoder = codecs.getdecoder(encoding)
    except LookupError:
        return codecs.getdecoder(default)
    return decoder

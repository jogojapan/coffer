'''
Created on 2011/04/19

@author: gollerjo
'''

def get_from_config_parser(config_parser,
                           section,
                           key,
                           default):
    if config_parser.has_option(section,key):
        return config_parser.get(section,key)
    else:
        return default

def get_boolean_from_config_parser(config_parser,
                                   section,
                                   key,
                                   default):
    if config_parser.has_option(section,key):
        return config_parser.getboolean(section,key)
    else:
        return default

def get_int_from_config_parser(config_parser,
                                   section,
                                   key,
                                   default):
    if config_parser.has_option(section,key):
        return config_parser.getint(section,key)
    else:
        return default

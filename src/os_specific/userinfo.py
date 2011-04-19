# -*- coding: utf-8 -*-

'''
Created on 2011/04/19

@author: gollerjo
'''

import os

def user_info():
    '''
    Returns the user id and group id of the user.
    Only implemented for Unix so far.
    '''
    return (os.getuid(),os.getgid())

# -*- coding: utf-8 -*-

import os

def user_info():
    '''
    Returns the user id and group id of the user.
    Only implemented for Unix so far.
    '''
    return (os.getuid(),os.getgid())

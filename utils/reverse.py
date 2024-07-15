# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 21:45:33 2024

@author: Eduin Hernandez
"""

def revert_dict(dt):
    return {value: key for key, value in dt.items()}
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  2 16:15:39 2015

@author: joag
"""

import os

print os.path.realpath(__file__)

import abalone.gaussian_kernel_cnmf.gaussian_cnmf as gaussian_cnmf

gaussian_cnmf.gaussian_cnmf()

import ar.gaussian_kernel_cnmf.gaussian_cnmf as gaussian_cnmf

gaussian_cnmf.gaussian_cnmf()

import att.gaussian_kernel_cnmf.gaussian_cnmf as gaussian_cnmf

gaussian_cnmf.gaussian_cnmf()

import balance_scale.gaussian_kernel_cnmf.gaussian_cnmf as gaussian_cnmf

gaussian_cnmf.gaussian_cnmf()

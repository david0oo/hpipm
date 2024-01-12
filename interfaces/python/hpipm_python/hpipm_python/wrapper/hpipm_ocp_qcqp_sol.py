###################################################################################################
#                                                                                                 #
# This file is part of HPIPM.                                                                     #
#                                                                                                 #
# HPIPM -- High-Performance Interior Point Method.                                                #
# Copyright (C) 2019 by Gianluca Frison.                                                          #
# Developed at IMTEK (University of Freiburg) under the supervision of Moritz Diehl.              #
# All rights reserved.                                                                            #
#                                                                                                 #
# The 2-Clause BSD License                                                                        #
#                                                                                                 #
# Redistribution and use in source and binary forms, with or without                              #
# modification, are permitted provided that the following conditions are met:                     #
#                                                                                                 #
# 1. Redistributions of source code must retain the above copyright notice, this                  #
#    list of conditions and the following disclaimer.                                             #
# 2. Redistributions in binary form must reproduce the above copyright notice,                    #
#    this list of conditions and the following disclaimer in the documentation                    #
#    and/or other materials provided with the distribution.                                       #
#                                                                                                 #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND                 #
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED                   #
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE                          #
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR                 #
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES                  #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;                    #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND                     #
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT                      #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS                   #
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                    #
#                                                                                                 #
# Author: Gianluca Frison, gianluca.frison (at) imtek.uni-freiburg.de                             #
#                                                                                                 #
###################################################################################################

from ctypes import *
import numpy as np
from .hpipm_ocp_qp_dim import hpipm_ocp_qp_dim
from typing import Union, Optional



class hpipm_ocp_qcqp_sol:


	def __init__(self, dim: hpipm_ocp_qp_dim):

		# save dim internally
		self.dim = dim

		# load hpipm shared library
		__hpipm   = CDLL('libhpipm.so')
		self.__hpipm = __hpipm

		# C qp struct
		qp_sol_struct_size = __hpipm.d_ocp_qcqp_sol_strsize()
		qp_sol_struct = cast(create_string_buffer(qp_sol_struct_size), c_void_p)
		self.qp_sol_struct = qp_sol_struct

		# C qp internal memory
		qp_sol_mem_size = __hpipm.d_ocp_qcqp_sol_memsize(dim.dim_struct)
		qp_sol_mem = cast(create_string_buffer(qp_sol_mem_size), c_void_p)
		self.qp_sol_mem = qp_sol_mem

		# create C qp
		__hpipm.d_ocp_qcqp_sol_create(dim.dim_struct, qp_sol_struct, qp_sol_mem)

		# getter functions for controls, states
		self.__getters = {
			'u': {
				'n_var': __hpipm.d_ocp_qcqp_dim_get_nu,
				'var': __hpipm.d_ocp_qcqp_sol_get_u
			},
			'x': {
				'n_var': __hpipm.d_ocp_qcqp_dim_get_nx,
				'var': __hpipm.d_ocp_qcqp_sol_get_x
			},
		}


	def get(self, field: str, idx_start: int, idx_end: Optional[int] = None)-> Union[np.ndarray, list[np.ndarray]]:
		'''
		Getter for value of `field` at stage `idx_start` or at stages `idx_start` to `idx_end`.
		Returns a single np.ndarray if only `idx_start` is given.
		Returns a list of np.ndarray if also `idx_end` is given.
		'''
		if field not in self.__getters:
			raise NameError('hpipm_ocp_qcqp_sol.get: wrong field. Available fields are:', *self.__getters.keys())
		else:
			return self.__get(self.__getters[field], idx_start, idx_end)


	def __get(self, getter, idx_start: int, idx_end: Optional[int]=None) -> Union[np.ndarray, list[np.ndarray]]:
		n_var = np.zeros((1,), dtype=int)

		if idx_end is None:
			idx_end_ = idx_start
		else:
			idx_end_ = idx_end

		var = []
		for i in range(idx_start, idx_end_ + 1):
			tmp_ptr = cast(n_var.ctypes.data, POINTER(c_int))
			getter['n_var'](self.dim.dim_struct, i, tmp_ptr)

			var.append(np.zeros((n_var[0], 1)))
			tmp_ptr = cast(var[-1].ctypes.data, POINTER(c_double))
			getter['var'](i, self.qp_sol_struct, tmp_ptr)

		return var if idx_end is not None else var[0]


	def print_C_struct(self):
		self.__hpipm.d_ocp_qcqp_sol_print(self.dim.dim_struct, self.qp_sol_struct)
		return

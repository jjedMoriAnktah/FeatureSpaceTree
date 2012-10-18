#!/usr/local/bin/python
# coding: utf-8

# Copyright (C) 2011-2012 FeatureSpaceTree Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ==============================================================================
# FeatureSpaceTree:
#
# Author: Adrian Pastor Lopez-Monroy <pastor@ccc.inaoep.mx>
# URL: <https://github.com/beiceman/FeatureSpaceTree>
#
# Language Technologies Lab,
# Department of Computer Science,
# Instituto Nacional de Astrofísica, Óptica y Electrónica
#
# For license information, see:
#  * The header of this file
#  * The LICENSE.TXT included in the project dir
# ==============================================================================

#===============================================================================
# Modes are Templates to choose how the terms will be calculated. The ModeCorpus
# receive the object corpus in kwargs["corpus"] and a list of files(can be a
# list of one)in kwargs[sources]; it iterates and get the respective tokens.
# The ModeString calculates the tokens in kwargs["string"].
#===============================================================================

from mode_options import EnumModes
from modes import *
from modes_extra import *
     

class FactoryMode(object):

    @staticmethod
    def create(option):

        if option == EnumModes.MODE_CORPUS:
            return ModeCorpus()
        
        elif option == EnumModes.MODE_STRING:
            return ModeString()
        
        elif option == EnumModes.MODE_GLOBALW:
            return ModeWeightGlobalCollocation()
        
        elif option == EnumModes.MODE_GLOBALA:
            return ModeWeightAuthorCollocation()
        
        elif option == EnumModes.MODE_CORPUS_POS:
            return ModeCorpusPOS()
        
        elif option == EnumModes.MODE_CORPUS_POS_GLOBAL_A:
            return ModeWeightAuthorCollocationPOS()
        
        elif option == EnumModes.MODE_CORPUS_AUTHOR_POS:
            return ModeWeightAuthorPOS()
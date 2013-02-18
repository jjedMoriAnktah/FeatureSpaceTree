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

from postfilter import *
from postfilter_extra import *

class Util(object):

    @staticmethod
    def decorate_by_token_normalizer(by_token_normalizer,
                                     by_token_normalizers):
        for kwargs_by_token_normalizer in by_token_normalizers:

            decorated_by_token_normalizer = FactorySimpleDecoratorByTokenNormalizer.create(kwargs_by_token_normalizer['type_by_token_normalizer'],
                                                                                           kwargs_by_token_normalizer,
                                                                                           by_token_normalizer)

            by_token_normalizer = decorated_by_token_normalizer

        return by_token_normalizer

class EnumDecoratorByTokenNormalizer(object):

    (STEMMER,
     TOKEN_X_COLAPSE,
     INVERSE_SPECIFIC_FILTER,
     CHAR_REPEATER,
     INVERSE_CONTAINS_SPECIFIC_FILTER,
     NEIGHBORING_BIGRAMS,
     ORIENTATION_NEIGHBORING_BIGRAMS,
     NEIGHBORING_NO_ORDER_BIGRAMS,
     NEIGHBORING_NO_ORDER_TRIGRAMS, 
     NEIGHBORING_NO_ORDER_TETRAGRAMS) = range(10)
     

class FactorySimpleDecoratorByTokenNormalizer(object):

    @staticmethod
    def create(option, kwargs, by_token_normalizer):
        # DEBUG: print "#######" + str(option)
        option = eval(option)
        if option == EnumDecoratorByTokenNormalizer.STEMMER:
            return StemmerDecoratorByTokenNormalizer(by_token_normalizer)
        
        if option == EnumDecoratorByTokenNormalizer.TOKEN_X_COLAPSE:
            return TokenXColapseDecoratorByTokenNormalizer(by_token_normalizer, kwargs['token'], kwargs['until'])
        
        if option == EnumDecoratorByTokenNormalizer.INVERSE_SPECIFIC_FILTER:
            return InverseSpecificFilterDecoratorByTokenNormalizer(by_token_normalizer, kwargs['tokens'])
        
        if option == EnumDecoratorByTokenNormalizer.CHAR_REPEATER:
            return CharRepeaterDecoratorByTokenNormalizer(by_token_normalizer, kwargs['bias'])
        
        if option == EnumDecoratorByTokenNormalizer.INVERSE_CONTAINS_SPECIFIC_FILTER:
            return InverseContainsSpecificFilterDecoratorByTokenNormalizer(by_token_normalizer, kwargs['tokens'])
        
        if option == EnumDecoratorByTokenNormalizer.NEIGHBORING_BIGRAMS:
            return NeighboringBigramsFilterDecoratorByTokenNormalizer(by_token_normalizer)
        
        if option == EnumDecoratorByTokenNormalizer.ORIENTATION_NEIGHBORING_BIGRAMS:
            return OrientationNeighboringBigramsFilterDecoratorByTokenNormalizer(by_token_normalizer)
        
        if option == EnumDecoratorByTokenNormalizer.NEIGHBORING_NO_ORDER_BIGRAMS:
            return NeighboringNoOrderBigramsFilterDecoratorByTokenNormalizer(by_token_normalizer)
        
        if option == EnumDecoratorByTokenNormalizer.NEIGHBORING_NO_ORDER_TRIGRAMS:
            return NeighboringNoOrderTrigramsFilterDecoratorByTokenNormalizer(by_token_normalizer)
        
        if option == EnumDecoratorByTokenNormalizer.NEIGHBORING_NO_ORDER_TETRAGRAMS:
            return NeighboringNoOrderTetragramsFilterDecoratorByTokenNormalizer(by_token_normalizer)
        
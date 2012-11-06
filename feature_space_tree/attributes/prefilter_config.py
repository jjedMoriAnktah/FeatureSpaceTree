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

# ==============================================================================
# The following classes helps to normalize the text when each term is being
# extracted. The "ByTokenNormalizer" like classes are normalizer applied after
# each term is extracted, this is when we have the tokens in a list. For example,
# when all the words are extracted using TermRegExp calc_terms method, in this
# way, each token receives the normalization.

# The RawStringNormalizer
# ==============================================================================
from prefilter import *
from prefilter_extra import *

class Util(object):

    @staticmethod
    def decorate_raw_string(raw_string_normalizer,
                            raw_string_normalizers):

        for kwargs_raw_string_normalizer in raw_string_normalizers:

            decorated_raw_string_normalizer = FactorySimpleDecoratorRawStringNormalizer.create(kwargs_raw_string_normalizer['type_raw_string_normalizer'],
                                                                                               kwargs_raw_string_normalizer,
                                                                                               raw_string_normalizer)

            raw_string_normalizer = decorated_raw_string_normalizer

        return raw_string_normalizer


class EnumDecoratorRawStringNormalizer(object):

    (TO_LOWER,
     TO_UPPER,
     JUST_REGEXP,
     IGNORE_STRINGS,
     REPLACE_REGEXP) = range(5)
     

class FactorySimpleDecoratorRawStringNormalizer(object):

    @staticmethod
    def create(option, kwargs, raw_string_normalizer):
        # DEBUG: print "????????" + str(option)
        option = eval(option)
        
        if option == EnumDecoratorRawStringNormalizer.TO_LOWER:
            return ToLowerDecoratorRawStringNormalizer(raw_string_normalizer)
        
        elif option == EnumDecoratorRawStringNormalizer.TO_UPPER:
            return ToUpperDecoratorRawStringNormalizer(raw_string_normalizer)
        
        elif option == EnumDecoratorRawStringNormalizer.JUST_REGEXP:
            return JustRegExpDecoratorRawStringNormalizer(raw_string_normalizer,
                                                          kwargs['regexp'])
            
        elif option == EnumDecoratorRawStringNormalizer.IGNORE_STRINGS:
            return IgnoreStringsDecoratorRawStringNormalizer(raw_string_normalizer,
                                                          kwargs['path_ignored_strings'],
                                                          (False, True)['to_lower' in kwargs])
        
        elif option == EnumDecoratorRawStringNormalizer.REPLACE_REGEXP:
            regexp = attr_util.Util.get_the_regexp(kwargs)
            return ReplaceRegExpDecoratorRawStringNormalizer(raw_string_normalizer,
                                                             regexp,
                                                             kwargs['replacement'])
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
# FeatureSpaceTree: Filters module
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

# ------------------------------------------------------------------------------
# The REALLY important classes here are all that contains the name vocabulary. This
# is since they are used when the PROPROCESSING_OPTION is set to SIMPLE, this
# means that we will process the terms as SETs and as Dictionaries (nltk FDIST).
# The option FULL we would have FILTER the tokens just as they are retrieved
# so, the preprocessing is slower. 
# ------------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod
from filters_terms import *

class EnumFiltersVocabulary(object):

    (FIXED_TOP,
     PERCENTAGE_TOP,
     BIAS_FREQ,
     FIXED_RAND,
     PERCENTAGE_RAND,
     TRANSPARENT) = range(6)


class FactoryFilterVocabulary(object):

    __metaclass__ = ABCMeta

    def build(self, option, kwargs, vocabulary_object):
        option = eval(option)
        return self.create(option, kwargs, vocabulary_object)

    @abstractmethod
    def create(self, option, kwargs, vocabulary_object):
        pass


class FactorySimpleFilterVocabulary(FactoryFilterVocabulary):

    def create(self, option, kwargs, vocabulary_object):
        if option == EnumFiltersVocabulary.FIXED_TOP:
            return FixedTopVocabulary(vocabulary_object, kwargs["fixed_top"])

        if option == EnumFiltersVocabulary.PERCENTAGE_TOP:
            return PercentageTopVocabulary(vocabulary_object, kwargs["percentage_top"])

        if option == EnumFiltersVocabulary.BIAS_FREQ:
            return BiasFreqVocabulary(vocabulary_object, kwargs["bias_freq"])

        if option == EnumFiltersVocabulary.FIXED_RAND:
            return FixedRandomVocabulary(vocabulary_object, kwargs["n_terms"], kwargs["caos"])

        if option == EnumFiltersVocabulary.PERCENTAGE_RAND:
            return PercentageRandomVocabulary(vocabulary_object, kwargs["percentage"], kwargs["caos"])

        if option == EnumFiltersVocabulary.TRANSPARENT:
            return FilterVocabulary(vocabulary_object)
        
        
class EnumFiltersTermsList(object):

    (FIXED_TOP,
     PERCENTAGE_TOP,
     BIAS_FREQ,
     FIXED_RAND,
     PERCENTAGE_RAND,
     ORDER,
     TRANSPARENT) = range(7)


class FactorySimpleFilterTermsList(object):

    @staticmethod
    def create(option, kwargs, terms_list):

        option = eval (option)
        if option == EnumFiltersTermsList.FIXED_TOP:
            return FixedTopTermsList(terms_list, kwargs["fixed_top"])

        if option == EnumFiltersTermsList.PERCENTAGE_TOP:
            return PercentageTopTermsList(terms_list, kwargs["percentage_top"])

        if option == EnumFiltersTermsList.BIAS_FREQ:
            return BiasFreqTermsList(terms_list, kwargs["bias_freq"])

        if option == EnumFiltersTermsList.FIXED_RAND:
            return FixedRandomTermsList(terms_list, kwargs["n_terms"], kwargs["caos"])

        if option == EnumFiltersTermsList.PERCENTAGE_RAND:
            return PercentageRandomTermsList(terms_list, kwargs["percentage"], kwargs["caos"])

        if option == EnumFiltersTermsList.ORDER:
            return OrderTermsList(terms_list)

        if option == EnumFiltersTermsList.TRANSPARENT:
            return TransparentTermsList(terms_list)
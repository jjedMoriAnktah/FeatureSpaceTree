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
# FeatureSpaceTree: Postfilter module
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


# ==============================================================================
# The following classes helps to normalize the text when each term is being
# extracted. The "ByTokenNormalizer" like classes are normalizer applied after
# each term is extracted, this is when we have the tokens in a list. For example,
# when all the words are extracted using TermRegExp calc_terms method, in this
# way, each token receives the normalization.

# The RawStringNormalizer
# ==============================================================================



from postfilter import *

class EnumDecoratorByTokenNormalizer(object):

    (STEMMER,
     TOKEN_X_COLAPSE,
     INVERSE_SPECIFIC_FILTER,
     CHAR_REPEATER,
     INVERSE_CONTAINS_SPECIFIC_FILTER) = range(5)
     

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
        
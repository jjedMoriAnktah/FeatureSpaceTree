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
#from attr_util import Util

import attr_util
from abc import ABCMeta, abstractmethod
        
class ByTokenNormalizer(object):

    __metaclass__ = ABCMeta

    def __init__(self, list_of_tokens):
        self._list_of_tokens = list_of_tokens

    @abstractmethod
    def get_list_of_tokens(self):
        return self._list_of_tokens


class EmptyByTokenNormalizer(ByTokenNormalizer):

    def __init__(self, list_of_tokens):
        super(EmptyByTokenNormalizer, self).__init__(list_of_tokens)

    def get_list_of_tokens(self):
        return self._list_of_tokens


class DecoratorByTokenNormalizer(ByTokenNormalizer):

    def __init__(self, by_token_normalizer):
        self._by_token_normalizer = by_token_normalizer

    @abstractmethod
    def get_list_of_tokens(self):
        return self._by_token_normalizer.get_list_of_tokens()


class StemmerDecoratorByTokenNormalizer(DecoratorByTokenNormalizer):

    def __init__(self, by_token_normalizer):
        super(StemmerDecoratorByTokenNormalizer, self).__init__(by_token_normalizer)

    def get_list_of_tokens(self):
        old_list_of_tokens = self._by_token_normalizer.get_list_of_tokens()

        new_list_of_tokens = attr_util.Util.applyStem(old_list_of_tokens)

        return new_list_of_tokens


class TokenXColapseDecoratorByTokenNormalizer(DecoratorByTokenNormalizer):

    def __init__(self, by_token_normalizer, token, until):
        super(TokenXColapseDecoratorByTokenNormalizer, self).__init__(by_token_normalizer)
        self.until = until
        self.token = token

    def get_list_of_tokens(self):
        old_list_of_tokens = self._by_token_normalizer.get_list_of_tokens()

        for i in range(self.until):
            if ((i+1) <= len(old_list_of_tokens) and
                self.token == old_list_of_tokens[-(i+1)]):
                # print i
                # print old_list_of_tokens
                for j in range(i + 1):
                    old_list_of_tokens.pop()

                old_list_of_tokens.append(self.token + str(i))
                # print "NEW: " + str(old_list_of_tokens)
                #break

        new_list_of_tokens = old_list_of_tokens

        return new_list_of_tokens


class InverseSpecificFilterDecoratorByTokenNormalizer(DecoratorByTokenNormalizer):

    def __init__(self, by_token_normalizer, list_of_tokens):
        super(InverseSpecificFilterDecoratorByTokenNormalizer, self).__init__(by_token_normalizer)
        self.list_of_tokens = list_of_tokens

    def get_list_of_tokens(self):
        old_list_of_tokens = self._by_token_normalizer.get_list_of_tokens()

        new_list_of_tokens = [e for e in  old_list_of_tokens
                              if e in self.list_of_tokens]

        return new_list_of_tokens


class InverseContainsSpecificFilterDecoratorByTokenNormalizer(DecoratorByTokenNormalizer):

    def __init__(self, by_token_normalizer, list_of_tokens):
        super(InverseContainsSpecificFilterDecoratorByTokenNormalizer, self).__init__(by_token_normalizer)
        self.list_of_tokens = list_of_tokens

    def get_list_of_tokens(self):
        old_list_of_tokens = self._by_token_normalizer.get_list_of_tokens()

        new_list_of_tokens = []
        for e in  old_list_of_tokens:
            for t in self.list_of_tokens:
                if t in e:
                    new_list_of_tokens += [e]
                    break

        return new_list_of_tokens


class CharRepeaterDecoratorByTokenNormalizer(DecoratorByTokenNormalizer):

    def __init__(self, by_token_normalizer, bias):
        super(CharRepeaterDecoratorByTokenNormalizer, self).__init__(by_token_normalizer)
        self.bias = bias

    def get_list_of_tokens(self):
        old_list_of_tokens = self._by_token_normalizer.get_list_of_tokens()

        new_list_of_tokens = attr_util.Util.applyRepeater(old_list_of_tokens, self.bias)

        return new_list_of_tokens
    
    
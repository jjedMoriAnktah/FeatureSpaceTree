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

import random
import copy

import nltk
from abc import ABCMeta, abstractmethod

# ------------------------------------------------------------------------------
# The REALLY important classes here are all that contains the name vocabulary. This
# is since they are used when the PROPROCESSING_OPTION is set to SIMPLE, this
# means that we will process the terms as SETs and as Dictionaries (nltk FDIST).
# The option FULL we would have FILTER the tokens just as they are retrieved
# so, the preprocessing is slower. 
# ------------------------------------------------------------------------------


class Vocabulary(object):

    def __init__(self, fdist):
        self.__fdist = fdist

    def get_fdist(self):
        return self.__fdist

    def set_fdist(self, value):
        self.__fdist = value

    @abstractmethod
    def get_vocabulary_selected(self):
        pass

    @abstractmethod
    def get_fdist_selected(self):
        pass


class VocabularyRaw(Vocabulary):

    def __init__(self, fdist):
        super(VocabularyRaw, self).__init__(fdist)

    def get_fdist_selected(self):
        return self.get_fdist()


class FilterVocabulary(Vocabulary):

    def __init__(self, vocabulary_object):
        self.__vocabulary_object = vocabulary_object

    def get_fdist(self):
        return self.__vocabulary_object.get_fdist()

    def set_fdist(self, value):
        self.__vocabulary_object.set_fdist(value)

    def get_fdist_selected(self):
        return self.__vocabulary_object.get_fdist_selected()


class FixedTopVocabulary(FilterVocabulary):

    def __init__(self, vocabulary_object, n_terms):
        super(FixedTopVocabulary, self).__init__(vocabulary_object)
        self.n_terms = n_terms

    def get_fdist_selected(self):
        old_fdist_selected = \
        super(FixedTopVocabulary, self).get_fdist_selected()
        new_vocabulary_selected = old_fdist_selected.keys()[:self.n_terms]

        new_fdist_selected = nltk.FreqDist()
        for token in new_vocabulary_selected:
            new_fdist_selected[token] = old_fdist_selected[token]

        return new_fdist_selected


class PercentageTopVocabulary(FilterVocabulary):

    def __init__(self, vocabulary_object, percentage):
        super(PercentageTopVocabulary, self).__init__(vocabulary_object)
        self.percentage = percentage

    def get_fdist_selected(self):
        old_fdist_selected = \
        super(PercentageTopVocabulary, self).get_fdist_selected()
        new_vocabulary_selected = \
        old_fdist_selected.keys()[:int(len(old_fdist_selected) * self.percentage)]

        new_fdist_selected = nltk.FreqDist()
        for token in new_vocabulary_selected:
            new_fdist_selected[token] = old_fdist_selected[token]

        return new_fdist_selected


class BiasFreqVocabulary(FilterVocabulary):

    def __init__(self, vocabulary_object, bias_freq):
        super(BiasFreqVocabulary, self).__init__(vocabulary_object)
        self.bias_freq = bias_freq

    def get_fdist_selected(self):
        old_fdist_selected = \
        super(BiasFreqVocabulary, self).get_fdist_selected()
        new_vocabulary_selected = \
        [token
         for token in old_fdist_selected
         if old_fdist_selected[token] >= self.bias_freq]

        new_fdist_selected = nltk.FreqDist()
        for token in new_vocabulary_selected:
            new_fdist_selected[token] = old_fdist_selected[token]

        return new_fdist_selected


class FixedRandomVocabulary(FilterVocabulary):

    def __init__(self, vocabulary_object, n_terms, caos):
        super(FixedRandomVocabulary, self).__init__(vocabulary_object)
        self.n_terms = n_terms
        self.caos = caos

    def get_fdist_selected(self):
        old_fdist_selected = \
        super(BiasFreqVocabulary, self).get_fdist_selected()
        new_vocabulary_selected = old_fdist_selected.keys()

        #=======================================================================
        portion = int(len(new_vocabulary_selected)/self.caos)
        a = 0
        b = portion
        temp_new_vocabulary_selected = []
        for i in range(self.caos):
            part_x = new_vocabulary_selected[a:b]
            random.shuffle(part_x)
            temp_new_vocabulary_selected += part_x[:int(self.n_terms/self.caos)]
            a += portion
            b += portion
            i+=0
        new_vocabulary_selected = temp_new_vocabulary_selected
        #=======================================================================

        new_fdist_selected = nltk.FreqDist()
        for token in new_vocabulary_selected:
            new_fdist_selected[token] = old_fdist_selected[token]

        return new_fdist_selected


class PercentageRandomVocabulary(FilterVocabulary):

    def __init__(self, vocabulary_object, percentage, caos):
        super(PercentageRandomVocabulary, self).__init__(vocabulary_object)
        self.percentage = percentage
        self.caos = caos

    def get_fdist_selected(self):
        old_fdist_selected = \
        super(BiasFreqVocabulary, self).get_fdist_selected()
        new_vocabulary_selected = old_fdist_selected.keys()
        self.n_terms = len(new_vocabulary_selected) * self.percentage

        #=======================================================================
        portion = int(len(new_vocabulary_selected)/self.caos)
        a = 0
        b = portion
        temp_new_vocabulary_selected = []
        for i in range(self.caos):
            part_x = new_vocabulary_selected[a:b]
            random.shuffle(part_x)
            temp_new_vocabulary_selected += part_x[:int(self.n_terms/self.caos)]
            a += portion
            b += portion
            i+=0
        new_vocabulary_selected = temp_new_vocabulary_selected

        random.shuffle(new_vocabulary_selected)
        new_vocabulary_selected = new_vocabulary_selected[:portion]
        #=======================================================================

        new_fdist_selected = nltk.FreqDist()
        for token in new_vocabulary_selected:
            new_fdist_selected[token] = old_fdist_selected[token]

        return new_fdist_selected
    
    
# ==============================================================================    



class TermsList(object):

    __metaclass__ = ABCMeta

    def __init__(self, tokens):
        self.set_tokens(tokens)

    @abstractmethod
    def get_terms_selected(self):
        pass

    def get_tokens(self):
        return self.__tokens

    def set_tokens(self, value):
        self.__tokens = value
        self._fdist = nltk.FreqDist(nltk.Text(value))

    def get_fdist(self):
        return self._fdist


class TermsListRaw(TermsList):

    def __init__(self, tokens):
        super(TermsListRaw, self).__init__(tokens)

    def get_terms_selected(self):
        return self._fdist.keys()


class FilterTermsList(TermsList):

    def __init__(self, terms_list):
        self._terms_list = terms_list

    def get_tokens(self):
        return self._terms_list.get_tokens()

    def set_tokens(self, value):
        self._terms_list.set_tokens(value)

    def get_fdist(self):
        return self._terms_list.get_fdist()

    def get_filtered_tokens(self):
        terms_selected = self.get_terms_selected()
        return [token
                for token in self._terms_list.get_tokens()
                if token in terms_selected]

    def get_filtered_fdist(self):
        terms_selected = self.get_terms_selected()
        temp_fdist = copy.deepcopy(self._terms_list.get_fdist())
        filtered_tokens = set(self._terms_list.get_tokens()) - set(terms_selected)

        for filtered_token in filtered_tokens:
            del temp_fdist[filtered_token]

        return temp_fdist


class FixedTopTermsList(FilterTermsList):

    def __init__(self, terms_list, n_terms):
        super(FixedTopTermsList, self).__init__(terms_list)
        self.n_terms = n_terms

    def get_terms_selected(self):
        terms_selected = self._terms_list.get_terms_selected()
        return terms_selected[:self.n_terms]


class PercentageTopTermsList(FilterTermsList):

    def __init__(self, terms_list, percentage):
        super(PercentageTopTermsList, self).__init__(terms_list)
        self.percentage = percentage

    def get_terms_selected(self):
        terms_selected = self._terms_list.get_terms_selected()
        length_terms_list = len(terms_selected)
        total_terms = int(length_terms_list * self.percentage)
        return terms_selected[:total_terms]


class BiasFreqTermsList(FilterTermsList):

    def __init__(self, terms_list, bias_freq):
        super(BiasFreqTermsList, self).__init__(terms_list)
        self.bias_freq = bias_freq

    def get_terms_selected(self):
        terms_selected = self._terms_list.get_terms_selected()
        terms_selected = [term
                          for term in terms_selected
                          if self.get_fdist()[term] >= self.bias_freq]

        return terms_selected


class FixedRandomTermsList(FilterTermsList):

    def __init__(self, terms_list, n_terms, caos):
        super(FixedRandomTermsList, self).__init__(terms_list)
        self.n_terms = n_terms
        self.caos = caos

    def get_terms_selected(self):
        terms_selected = self._terms_list.get_terms_selected()

        portion = int(len(terms_selected)/self.caos)

        a = 0
        b = portion
        temp_terms_selected = []
        for i in range(self.caos):
            part_x = terms_selected[a:b]
            random.shuffle(part_x)
            temp_terms_selected += part_x[:int(self.n_terms/self.caos)]
            a += portion
            b += portion
            i+=0

        terms_selected = temp_terms_selected

        return terms_selected


class PercentageRandomTermsList(FilterTermsList):

    def __init__(self, terms_list, percentage, caos):
        super(PercentageRandomTermsList, self).__init__(terms_list)
        self.percentage = percentage
        self.caos = caos

    def get_terms_selected(self):
        terms_selected = self._terms_list.get_terms_selected()
        self.n_terms = len(terms_selected) * self.percentage

        portion = int(len(terms_selected)/self.caos)

        a = 0
        b = portion
        temp_terms_selected = []
        for i in range(self.caos):
            part_x = terms_selected[a:b]
            random.shuffle(part_x)
            temp_terms_selected += part_x[:int(self.n_terms/self.caos)]
            a += portion
            b += portion
            i+=0

        terms_selected = temp_terms_selected

        random.shuffle(terms_selected)
        return terms_selected[:portion]


class OrderTermsList(FilterTermsList):

    def __init__(self, terms_list):
        super(OrderTermsList, self).__init__(terms_list)

    def get_terms_selected(self):
        terms_selected = self._terms_list.get_terms_selected()
        terms_selected = [term
                          for term in self.get_fdist().keys()
                          if term in terms_selected]

        return terms_selected


class TransparentTermsList(FilterTermsList):

    def __init__(self, terms_list):
        super(TransparentTermsList, self).__init__(terms_list)

    def get_terms_selected(self):
        terms_selected = self._terms_list.get_terms_selected()
        return terms_selected
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
# FeatureSpaceTree: Virtuals module
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


import nltk
from abc import ABCMeta, abstractmethod

from ..attributes.attr_config import FactoryTermLex
from ..attributes.filters_terms_config import FactorySimpleFilterVocabulary, FactorySimpleFilterTermsList
from ..attributes.filters_terms import TermsListRaw, VocabularyRaw

# ------------------------------------------------------------------------------
# The REALLY important classes here are all that contains the name vocabulary. This
# is since they are used when the PROPROCESSING_OPTION is set to SIMPLE, this
# means that we will process the terms as SETs and as Dictionaries (nltk FDIST).
# The option FULL we would have FILTER the tokens just as they are retrieved
# so, the preprocessing is slower. 
# ------------------------------------------------------------------------------

# ##############################################################################
#
#                 +--------------------+
#                 |   VirtualElement   |
#                 |--------------------|
#                 | id_term            |
#                 | kwargs_term        |
#                 | fdist              |
#                 | vocabulary         |
#                 |--------------------|
#                 | __init__           |
#                 +--------------------+
#                      .          .
#                     /_\        /_\
#                      |          |
#                      |          |
#           |...........          ........
#           |                            |
#  +--------------------+       +--------------------+
#  | VirtualVocabulary  |       |    VirtualTerm     |
#  |--------------------|       |--------------------|
#  | string_description |       | string_description |  ---->  [ nltk.FreqDist ]
#  | fdist              |       | tokens             |
#  | vocabulary         |       | fdist              |
#  |--------------------|       | vocabulary         |
#  | __init__           |       |--------------------|
#  +--------------------+       | __init__           |
#                               +--------------------+
#
#
#
#
#                        +------------------------+
#                        | FactoryTermsProcessing |
#                        |------------------------|
#                        | __metaclass__          |
#                        |------------------------|
#                        | build                  |
#                        | create                 |
#                        +------------------------+
#                                   .
#                                  /_\
#                                   |
#                                   |
#                    +------------------------------+
#                    | FactorySimpleTermsProcessing |
#                    |------------------------------|
#                    | create                       |
#                    +------------------------------+
#                                   .
#                                  /|\
#                                   |
#                                   |
#                   +---------------'-----------------+
#                   |    AbstractFactoryProcessing    |
#                   |---------------------------------|
#                   | build_virtual_processor         |
#                   | build_virtual_re_processor      |
#                   | build_virtual_global_processor  |
#                   | create_virtual_processor        |
#                   | create_virtual_re_processor     |
#                   | create_virtual_global_processor |
#                   +---------------------------------+
#                          .                     .
#                         /_\                   /_\
#                          |                     |
#                  .........                     .............
#                  |                                         |
#                  |                                         |
#                  '                                         |
#  +---------------------------------+       +---------------------------------+
#  |     SimpleFactoryProcessing     |       |      FullFactoryProcessing      |
#  |---------------------------------|       |---------------------------------|
#  | create_virtual_processor        |       | create_virtual_processor        |
#  | create_virtual_re_processor     |       | create_virtual_re_processor     |
#  | create_virtual_global_processor |       | create_virtual_global_processor |
#  +---------------------------------+       +---------------------------------+
#
#
#
#
#
#
#
#
#                         +-------------------+
#                         |  VirtualProcessor |
#                         |-------------------|
#                         | _factory_term_lex |  ---->  [ FactoryTermLex ]
#                         | virtual_elements  |
#                         | fdist             |
#                         | vocabulary        |
#                         |-------------------|
#                         | __init__          |
#                         +-------------------+
#                          .                .
#                         /_\              /_\
#                __________|                |_______
#               |                                  |
#  +----------------------------+       +-----------------------+
#  | VocabularyVirtualProcessor |       | TermsVirtualProcessor |
#  |----------------------------|       |-----------------------|
#  | virtual_elements           |       | virtual_elements      |
#  | fdist                      |       | tokens                |
#  | vocabulary                 |       | fdist                 |
#  |----------------------------|       | vocabulary            |
#  | __init__                   |       |-----------------------|
#  +----------------------------+       | __init__              |
#                                       +-----------------------+
#
#
#
#
#
#
#
#
#                                +-----------------------+
#                                |   VirtualReProcessor  |
#                                |-----------------------|
#                                | kwargs_terms_refilter |
#                                | new_virtual_elements  |
#                                | fdist                 |
#                                | vocabulary            |
#                                |-----------------------|
#                                | __init__              |
#                                +-----------------------+
#                                        .        .
#                                       /_\      /_\
#                ________________________|        |___________________
#                |                                                   |
# +-------------------------------+                 +------------------------------------+
# | FilterTermsVirtualReProcessor |                 | FilterVocabularyVirtualReProcessor |
# |-------------------------------|                 |------------------------------------|
# | new_virtual_elements          |                 | new_virtual_elements               |
# | tokens                        |                 | fdist                              |
# | fdist                         |                 | vocabulary                         |
# | vocabulary                    |                 |------------------------------------|
# |-------------------------------|                 | __init__                           |
# | __init__                      |                 +------------------------------------+
# +-------------------------------+
#
#
#
#
#
#
#                             +-----------------------------+
#                             |    VirtualGlobalProcessor   |
#                             |-----------------------------|
#                             | virtual_elements            |
#                             | global_kwargs_filters_terms |
#                             | fdist                       |
#                             | vocabulary                  |
#                             |-----------------------------|
#                             | __init__                    |
#                             +-----------------------------+
#                                      .             .
#                                     /_\           /_\
#                   ___________________|             ............
#                  |                                            |
# +-----------------------------------+      +----------------------------------------+
# | FilterTermsVirtualGlobalProcessor |      | FilterVocabularyVirtualGlobalProcessor |
# |-----------------------------------|      |----------------------------------------|
# | all_tokens                        |      | all_fdist                              |
# | all_fdist                         |      | all_vocabulary                         |
# | all_vocabulary                    |      | fdist                                  |
# | tokens                            |      | vocabulary                             |
# | fdist                             |      |----------------------------------------|
# | vocabulary                        |      | __init__                               |
# |-----------------------------------|      +----------------------------------------+
# | __init__                          |
# +-----------------------------------+
#
#
#
#
################################################################################

class Util(object):

    @staticmethod
    def decorate_terms_list(terms_list, kwargs_filters_terms):

        for kwargs_filter in kwargs_filters_terms:
            print kwargs_filter
            filter_terms_list = \
            FactorySimpleFilterTermsList.create(kwargs_filter["type_filter_terms"],
                                                kwargs_filter,
                                                terms_list)
            terms_list = filter_terms_list

        terms_list = \
        FactorySimpleFilterTermsList.create('EnumFiltersTermsList.ORDER',
                                            [],
                                            terms_list)
        return terms_list

    @staticmethod
    def decorate_vocabulary_object(vocabulary_object, kwargs_refilters_terms):

        factory_simple_filter_vocabulary = FactorySimpleFilterVocabulary()
        for kwargs_refilter_term in kwargs_refilters_terms:
            print kwargs_refilter_term
            filter_vocabulary_object = \
            factory_simple_filter_vocabulary.build(kwargs_refilter_term["type_filter_terms"],
                                                   kwargs_refilter_term,
                                                   vocabulary_object)
            vocabulary_object = filter_vocabulary_object

        vocabulary_object = \
        factory_simple_filter_vocabulary.build('EnumFiltersVocabulary.TRANSPARENT',
                                               None,
                                               vocabulary_object)
        return vocabulary_object

class VirtualProcessor(object):

    def __init__(self):
        self._factory_term_lex = FactoryTermLex()
        self.virtual_elements = None
        self.fdist = None
        self.vocabulary = None

class TermsVirtualProcessor(VirtualProcessor):

    def __init__(self, kwargs_terms):
        super(TermsVirtualProcessor, self).__init__()

        # ======================================================================
        # Produce the individual filtered VirtualTerms, storing them into a list
        # ======================================================================
        self.virtual_elements = []

        for kwargs_term in kwargs_terms:

            term = \
            self._factory_term_lex.build_tokens(kwargs_term['type_term'],
                                                 kwargs_term)

            term_list = TermsListRaw(term.tokens)

            filtered_terms_list = \
            Util.decorate_terms_list(term_list,
                                     kwargs_term['filters_terms'])

            tokens = filtered_terms_list.get_filtered_tokens()

            self.virtual_elements += [VirtualTerm(kwargs_term, tokens)]
        # ======================================================================

        # ======================================================================
        # This block computes the tokens
        # ======================================================================
        self.tokens = []
        for virtual_term in self.virtual_elements:
            self.tokens += virtual_term.tokens

        self.fdist = nltk.FreqDist(self.tokens)
        self.vocabulary = self.fdist.keys()
        # ======================================================================


class VocabularyVirtualProcessor(VirtualProcessor):

    def __init__(self, kwargs_terms):
        super(VocabularyVirtualProcessor, self).__init__()

        # ======================================================================
        # Produce the individual filtered VirtualTerms, storing them into a list
        # ======================================================================
        self.virtual_elements = []

        for kwargs_term in kwargs_terms:

            term = \
            self._factory_term_lex.build_tokens(kwargs_term['type_term'],
                                                 kwargs_term)

            vocabulary_object = VocabularyRaw(nltk.FreqDist(term.tokens))

            filtered_vocabulary = \
            Util.decorate_vocabulary_object(vocabulary_object,
                                             kwargs_term['filters_terms'])

            fdist = filtered_vocabulary.get_fdist_selected()

            self.virtual_elements += [VirtualVocabulary(kwargs_term, fdist)]

        # ======================================================================

        # ======================================================================
        # This block computes the fdist of all of the virtual_elements and 
        # creates a new one that includes all.
        # ======================================================================
        fdist = nltk.FreqDist()
        for virtual_vocabulary in self.virtual_elements:

            for token in virtual_vocabulary.fdist:

                if token in fdist:
                    fdist[token] += virtual_vocabulary.fdist[token]
                else:
                    fdist[token] = virtual_vocabulary.fdist[token]

        #print "SSSSSSSSSS:" +str(fdist)

        self.fdist = fdist
        self.vocabulary = self.fdist.keys()
        # ======================================================================


class VirtualElement(object):

    def __init__(self, kwargs_term):
        self.id_term = kwargs_term['id_term']
        self.kwargs_term = kwargs_term
        self.fdist = None
        self.vocabulary = None


class VirtualTerm(VirtualElement):

    def __init__(self, kwargs_term, tokens, description=""):
        super(VirtualTerm, self).__init__(kwargs_term)
        self.string_description = description+str(kwargs_term)
        self.tokens = tokens
        self.fdist = nltk.FreqDist(self.tokens)
        self.vocabulary = self.fdist.keys()

class VirtualVocabulary(VirtualElement):

    def __init__(self, kwargs_term, fdist, description=""):
        super(VirtualVocabulary, self).__init__(kwargs_term)
        self.string_description = description + str(kwargs_term)
        self.fdist = fdist
        self.vocabulary = self.fdist.keys()

class VirtualReProcessor(object):

    def __init__(self, virtual_elements, kwargs_terms_refilter):
        self.kwargs_terms_refilter = kwargs_terms_refilter
        self.new_virtual_elements = None
        self.fdist = None
        self.vocabulary = None


class FilterTermsVirtualReProcessor(VirtualReProcessor):

    def __init__(self, virtual_elements, kwargs_terms_refilter):
        super(FilterTermsVirtualReProcessor, self).__init__(virtual_elements,
                                                            kwargs_terms_refilter)

        self.new_virtual_elements = []

        for (virtual_term, kwargs_term_refilter) in zip(virtual_elements, kwargs_terms_refilter):

            term_list = TermsListRaw(virtual_term.tokens)

            filtered_terms_list = \
            Util.decorate_terms_list(term_list,
                                     kwargs_term_refilter['filters_terms'])

            tokens = filtered_terms_list.get_filtered_tokens()

            self.new_virtual_elements += [VirtualTerm(kwargs_term_refilter, tokens, description="Refiltered:")]

        # ======================================================================
        # This block computes the tokens
        # ======================================================================
        self.tokens = []
        for virtual_term in self.new_virtual_elements:
            self.tokens += virtual_term.tokens

        self.fdist = nltk.FreqDist(self.tokens)
        self.vocabulary = self.fdist.keys()
        # ======================================================================


class FilterVocabularyVirtualReProcessor(VirtualReProcessor):

    def __init__(self, virtual_elements, kwargs_terms_refilter):
        super(FilterVocabularyVirtualReProcessor, self).__init__(virtual_elements,
                                                                       kwargs_terms_refilter)

        self.new_virtual_elements = []
        for (virtual_element, kwargs_term_refilter) in zip(virtual_elements, kwargs_terms_refilter):

            vocabulary_object = VocabularyRaw(virtual_element.fdist)

            filtered_vocabualary_object = \
            Util.decorate_vocabulary_object(vocabulary_object,
                                            kwargs_term_refilter['filters_terms'])

            fdist = filtered_vocabualary_object.get_fdist_selected()

            self.new_virtual_elements += [VirtualVocabulary(kwargs_term_refilter, fdist, description="Refiltered:")]

        # ======================================================================
        # This block computes the fdist
        # ======================================================================
        fdist = nltk.FreqDist()
        for virtual_vocabulary in self.new_virtual_elements:
            for token in virtual_vocabulary.fdist:

                if(token in fdist):
                    fdist[token] += virtual_vocabulary.fdist[token]
                else:
                    fdist[token] = virtual_vocabulary.fdist[token]

        self.fdist = fdist
        self.vocabulary = self.fdist.keys()
        # ======================================================================

class VirtualGlobalProcessor(object):

    def __init__(self, virtual_elements, global_kwargs_filters_terms):
        self.virtual_elements = virtual_elements
        self.global_kwargs_filters_terms = global_kwargs_filters_terms
        self.fdist = None
        self.vocabulary = None

class FilterTermsVirtualGlobalProcessor(VirtualGlobalProcessor):

    def __init__(self, virtual_elements, global_kwargs_filters_terms):
        super(FilterTermsVirtualGlobalProcessor, self).__init__(virtual_elements,
                                                           global_kwargs_filters_terms)

        # ======================================================================
        # This block computes the tokens
        # ======================================================================
        self.all_tokens = []
        for virtual_term in self.virtual_elements:
            self.all_tokens += virtual_term.tokens

        self.all_fdist = nltk.FreqDist(self.all_tokens)
        self.all_vocabulary = self.all_fdist.keys()
        # ======================================================================

        # ================================kwargs_terms==========================
        # This block computes the tokens applying the final filters
        # ======================================================================
        term_list = TermsListRaw(self.all_tokens)
        filtered_terms_list = \
        Util.decorate_terms_list(term_list,
                                 self.global_kwargs_filters_terms)

        self.tokens = filtered_terms_list.get_filtered_tokens()
        self.fdist = nltk.FreqDist(self.tokens)
        self.vocabulary = self.fdist.keys()
        # ======================================================================


class FilterVocabularyVirtualGlobalProcessor(VirtualGlobalProcessor):

    def __init__(self, virtual_elements, global_kwargs_filters_terms):
        super(FilterVocabularyVirtualGlobalProcessor, self).__init__(virtual_elements,
                                                                 global_kwargs_filters_terms)

        # ======================================================================
        # This block computes the fdist
        # ======================================================================

        fdist = nltk.FreqDist()
        for virtual_vocabulary in self.virtual_elements:

            for token in virtual_vocabulary.fdist:
                if(token in fdist):
                    fdist[token] += virtual_vocabulary.fdist[token]
                else:
                    fdist[token] = virtual_vocabulary.fdist[token]

        self.all_fdist = fdist
        self.all_vocabulary = self.all_fdist.keys()
        # ======================================================================

        # ======================================================================
        # This block computes the fdists applying the final filters
        # ======================================================================

        vocabulary_object = VocabularyRaw(self.all_fdist)

        filtered_vocabualary_object = \
        Util.decorate_vocabulary_object(vocabulary_object,
                                         self.global_kwargs_filters_terms)

        fdist = filtered_vocabualary_object.get_fdist_selected()

        self.fdist = fdist
        self.vocabulary = self.fdist.keys()

        # ======================================================================


class EnumTermsProcessing(object):

    (FULL,
     SIMPLE) = range(2)


class FactoryTermsProcessing(object):

    __metaclass__ = ABCMeta

    def build(self, option):
        option = eval(option)
        return self.create(option)

    @abstractmethod
    def create(self, option):
        pass


class FactorySimpleTermsProcessing(FactoryTermsProcessing):

    def create(self, option):

        if option == EnumTermsProcessing.FULL:
            return FullFactoryProcessing()

        elif option == EnumTermsProcessing.SIMPLE:
            return SimpleFactoryProcessing()


class AbstractFactoryProcessing(object):

    def build_virtual_processor(self, kwargs_terms):
        return self.create_virtual_processor(kwargs_terms)

    def build_virtual_re_processor(self,
                                    virtual_elements,
                                    kwargs_terms_refilter):

        return self.create_virtual_re_processor(virtual_elements,
                                                kwargs_terms_refilter)

    def build_virtual_global_processor(self,
                                       virtual_elements,
                                       global_kwargs_filters_terms):

        return self.create_virtual_global_processor(virtual_elements,
                                                    global_kwargs_filters_terms)

    @abstractmethod
    def create_virtual_processor(self, kwargs_terms):
        pass

    @abstractmethod
    def create_virtual_re_processor(self,
                                    virtual_elements,
                                    kwargs_terms_refilter):
        pass

    @abstractmethod
    def create_virtual_global_processor(self,
                                        virtual_elements,
                                        global_kwargs_filters_terms):
        pass




class FullFactoryProcessing(AbstractFactoryProcessing):

    def create_virtual_processor(self, kwargs_terms):
        return TermsVirtualProcessor(kwargs_terms)

    def create_virtual_re_processor(self,
                                    virtual_elements,
                                    kwargs_terms_refilter):

        return FilterTermsVirtualReProcessor(virtual_elements,
                                             kwargs_terms_refilter)

    def create_virtual_global_processor(self,
                                        virtual_elements,
                                        global_kwargs_filters_terms):

        return FilterTermsVirtualGlobalProcessor(virtual_elements,
                                                 global_kwargs_filters_terms)


class SimpleFactoryProcessing(AbstractFactoryProcessing):

    def create_virtual_processor(self, kwargs_terms):
        return VocabularyVirtualProcessor(kwargs_terms)

    def create_virtual_re_processor(self,
                                    virtual_elements,
                                    kwargs_terms_refilter):

        return FilterVocabularyVirtualReProcessor(virtual_elements,
                                                  kwargs_terms_refilter)

    def create_virtual_global_processor(self,
                                        virtual_elements,
                                        global_kwargs_filters_terms):

        return FilterVocabularyVirtualGlobalProcessor(virtual_elements,
                                                      global_kwargs_filters_terms)


class VirtualTermSSSRProcessor(object):

    def __init__(self, tokens, global_kwargs_filter_terms):
        term_list_sssr = TermsListRaw(tokens)
        filtered_term_list_sssr = \
        Util.decorate_terms_list(term_list_sssr,
                                 global_kwargs_filter_terms)

        self.string_description = "SSSR_" + str(global_kwargs_filter_terms)
        self.tokens = filtered_term_list_sssr.get_filtered_tokens()
        self.fdist = nltk.FreqDist(self.tokens)
        self.vocabulary = self.fdist.keys()
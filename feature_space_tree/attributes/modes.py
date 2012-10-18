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

#===============================================================================
# Modes are Templates to choose how the terms will be calculated. The ModeCorpus
# receive the object corpus in kwargs["corpus"] and a list of files(can be a
# list of one)in kwargs[sources]; it iterates and get the respective tokens.
# The ModeString calculates the tokens in kwargs["string"].
#===============================================================================

import shelve
import re
from nltk.corpus.util import LazyCorpusLoader
from nltk.corpus.reader.plaintext import CategorizedPlaintextCorpusReader
from nltk.corpus.reader.tagged import CategorizedTaggedCorpusReader
from mode_options import EnumModes

from prefilter import EmptyRawStringNormalizer
from postfilter import EmptyByTokenNormalizer
import prefilter_config
import postfilter_config


class ModeCorpus(object):

    def build_terms(self, terms):
        # print "In ModeCorpus"
        cache_file = "%s.dat" % terms.name

        terms.tokens = []
        shelf = shelve.open(cache_file, protocol=2)

        for f_src in terms.kwargs["source"]:

            if f_src in shelf and terms.kwargs["lazy"]:
                terms.tokens += shelf[f_src]
                #print(str(f_src))
                #print("%s ... Found in \"%s\"" % (f_src, cache_file))
            else:
                # FIXME: This code is ok. However check how the "unicode" transformation
                # should be included in each of the other "Modes"!!!!
                terms.kwargs["string"] = \
                unicode(terms.kwargs["corpus"].raw(fileids=[f_src]), 'utf-8') # .lower()

                # Apply all RawStringNormalizers -------------------------------

                empty_raw_string_normalizer = \
                EmptyRawStringNormalizer(terms.kwargs['string'])

                # DEBUGGING: ---------------------------------------------------
                # print f_src
                # print terms.kwargs['string']
                # print empty_raw_string_normalizer.get_raw_string()
                # --------------------------------------------------------------

                if 'raw_string_normalizers' in terms.kwargs:
                    empty_raw_string_normalizer = \
                    prefilter_config.Util.decorate_raw_string(empty_raw_string_normalizer,
                                             terms.kwargs['raw_string_normalizers'])

                terms.kwargs["string"] = empty_raw_string_normalizer.get_raw_string()

                # --------------------------------------------------------------

                temp_tokens = terms.calc_terms()

                # Apply all ByTokenNormalizers ---------------------------------

                empty_by_token_normalizer = EmptyByTokenNormalizer(temp_tokens)

                if 'by_token_normalizers' in terms.kwargs:
                    empty_by_token_normalizer = \
                    postfilter_config.Util.decorate_by_token_normalizer(empty_by_token_normalizer,
                                                      terms.kwargs['by_token_normalizers'])

                temp_tokens = empty_by_token_normalizer.get_list_of_tokens()

                # --------------------------------------------------------------

                terms.tokens += temp_tokens

                if terms.kwargs["lazy"]:
                    shelf[f_src] = temp_tokens

                #print ("%s ... Recalculated in \"%s\"" % (f_src, cache_file))
        shelf.close()


class ModeString(object):

    def build_terms(self, terms):
        cache_file = "%s.dat" % terms.name
        terms.tokens = []
        shelf = shelve.open(cache_file, protocol=2)

        if terms.kwargs["string"] in shelf and terms.kwargs["lazy"]:
            terms.tokens += shelf[terms.kwargs["string"]]
            #print(str(f_src))
            #print("%s ... Found in \"%s\"" % (f_src, cache_file))
        else:
            temp_tokens = terms.calc_terms()
            terms.tokens += temp_tokens

            if terms.kwargs["lazy"]:
                shelf[terms.kwargs["string"]] = temp_tokens

        shelf.close()


class ModeWeightGlobalCollocation(object):

    def build_terms(self, terms):
        print "In ModeWeightGlobalCollocation"
        cache_file = "%s.dat" % terms.name
        terms.tokens = []
        shelf = shelve.open(cache_file, protocol=2)

        f_srcs = "|".join(terms.kwargs["source"])
        terms.kwargs["string"] = \
        terms.kwargs["corpus"].raw(fileids=terms.kwargs["source"]).lower()

        if f_srcs in shelf and terms.kwargs["lazy"]:
            terms.tokens += shelf[f_srcs]
            #print(str(f_src))
            #print("%s ... Found in \"%s\"" % (f_src, cache_file))
        else:
            terms.kwargs["string"] = \
            terms.kwargs["corpus"].raw(fileids=terms.kwargs["source"]).lower()

            temp_tokens = terms.calc_terms()
            terms.tokens += temp_tokens

            if terms.kwargs["lazy"]:
                shelf[f_srcs] = temp_tokens

            #print ("%s ... Recalculated in \"%s\"" % (f_src, cache_file))
        shelf.close()


class ModeWeightAuthorCollocation(object):
    '''
    This strategy is supposed to be used only one time, because it just have to
    analyze the author in the trainning set!!!.
    '''
    # XXX: This class is buggy

    def build_terms(self, terms):
        print "In ModeWeightClassCollocation"
        cache_file = "%s.dat" % terms.name
        terms.tokens = []
        shelf = shelve.open(cache_file, protocol=2)

        for author in terms.kwargs["corpus"].categories():

            author_files = set(terms.kwargs["corpus"].fileids([author])) & set(terms.kwargs["source"])
            author_files = list(author_files)
            if len(author_files) == 0:
                continue

            author_files.sort()
            #print "str(author_files): " + str(author_files)
            #print "str(terms.kwargs["corpus"]): " + str(terms.kwargs["corpus"]) + " str(terms.kwargs["corpus"].fileids([author])): " + str(terms.kwargs["corpus"].fileids([author])) + " str(terms.kwargs[\"source\"]): " + str(terms.kwargs["source"])
            f_srcs = "|".join(author_files)

            terms.kwargs["string"] = \
            terms.kwargs["corpus"].raw(fileids=author_files).lower()

            if f_srcs in shelf and terms.kwargs["lazy"]:
                terms.tokens += shelf[f_srcs]
                #print(str(f_src))
                #print("%s ... Found in \"%s\"" % (f_src, cache_file))
            else:
                terms.kwargs["string"] = \
                terms.kwargs["corpus"].raw(fileids=author_files).lower()

                temp_tokens = terms.calc_terms()

                # because the latter function calc:terms get off this option,
                # but we still needed
                terms.kwargs["boolBuildSetGlobal"] = True
                terms.kwargs["mode"] = EnumModes.MODE_GLOBALA
                ###############################################################

                terms.tokens += temp_tokens

                if terms.kwargs["lazy"]:
                    shelf[f_srcs] = temp_tokens

                #print ("%s ... Recalculated in \"%s\"" % (f_src, cache_file))
        terms.kwargs["boolBuildSetGlobal"] = False
        terms.kwargs["mode"] = EnumModes.MODE_CORPUS
        shelf.close()


# This is used for the ambiguous words :)
class ModeWeightAuthorPOS(object):
    '''
    This strategy is supposed to be used only one time, because it just have to
    analyze the author in the trainning set!!!.
    '''
    # XXX: This class is buggy

    def build_terms(self, terms):
        # save the original corpus
        corpus_temp = terms.kwargs["corpus"]
        groups = re.match(r'/home/aplm/nltk_data/corpora/c50/(.+)', corpus_temp.root.path)
        terms.kwargs["corpus"] = LazyCorpusLoader("c50_tagged/" + groups.group(1), CategorizedPlaintextCorpusReader, r'.+/.+', cat_pattern=r'(.+)/.+')

        print "In ModeWeightAuthorPOS"
        cache_file = "%s.dat" % terms.name
        terms.tokens = []
        shelf = shelve.open(cache_file, protocol=2)

        for author in terms.kwargs["corpus"].categories():

            author_files = set(terms.kwargs["corpus"].fileids([author])) & set(terms.kwargs["source"])
            author_files = list(author_files)
            if len(author_files) == 0:
                continue

            author_files.sort()
            #print "str(author_files): " + str(author_files)
            #print "str(terms.kwargs["corpus"]): " + str(terms.kwargs["corpus"]) + " str(terms.kwargs["corpus"].fileids([author])): " + str(terms.kwargs["corpus"].fileids([author])) + " str(terms.kwargs[\"source\"]): " + str(terms.kwargs["source"])
            f_srcs = "|".join(author_files)

            terms.kwargs["string"] = \
            terms.kwargs["corpus"].raw(fileids=author_files).lower()

            if f_srcs in shelf and terms.kwargs["lazy"]:
                terms.tokens += shelf[f_srcs]
                #print(str(f_src))
                #print("%s ... Found in \"%s\"" % (f_src, cache_file))
            else:
                terms.kwargs["string"] = \
                terms.kwargs["corpus"].raw(fileids=author_files).lower()

                temp_tokens = terms.calc_terms()

                # because the latter function calc:terms get off this option,
                # but we still needed
                terms.kwargs["boolBuildSetGlobal"] = True
                terms.kwargs["mode"] = EnumModes.MODE_CORPUS_AUTHOR_POS
                ###############################################################

                terms.tokens += temp_tokens

                if terms.kwargs["lazy"]:
                    shelf[f_srcs] = temp_tokens

                #print ("%s ... Recalculated in \"%s\"" % (f_src, cache_file))
        terms.kwargs["boolBuildSetGlobal"] = False
        terms.kwargs["mode"] = EnumModes.MODE_CORPUS_POS
        shelf.close()

        # restore the original corpus
        terms.kwargs["corpus"] = corpus_temp


class ModeCorpusPOS(object):

    def build_terms(self, terms):
        # save the original corpus
        corpus_temp = terms.kwargs["corpus"]
        groups = re.match(r'/home/aplm/nltk_data/corpora/c50/(.+)', corpus_temp.root.path)
        terms.kwargs["corpus"] = LazyCorpusLoader("c50_tagged/" + groups.group(1), CategorizedPlaintextCorpusReader, r'.+/.+', cat_pattern=r'(.+)/.+')

        #rint "In ModeCorpusPOS"
        cache_file = "%s.dat" % terms.name
        terms.tokens = []
        shelf = shelve.open(cache_file, protocol=2)

        for f_src in terms.kwargs["source"]:

            if f_src in shelf and terms.kwargs["lazy"]:
                terms.tokens += shelf[f_src]
                #print(str(f_src))
                #print("%s ... Found in \"%s\"" % (f_src, cache_file))
            else:
                terms.kwargs["string"] = \
                terms.kwargs["corpus"].raw(fileids=[f_src]).lower()

                temp_tokens = terms.calc_terms()
                terms.tokens += temp_tokens

                if terms.kwargs["lazy"]:
                    shelf[f_src] = temp_tokens

                #print ("%s ... Recalculated in \"%s\"" % (f_src, cache_file))
        shelf.close()

        # restore the original corpus
        terms.kwargs["corpus"] = corpus_temp


class ModeWeightAuthorCollocationPOS(object):
    '''
    This strategy is supposed to be used only one time, because it just have to
    analyze the author in the trainning set!!!.
    '''
    # XXX: This class is buggy

    def build_terms(self, terms):
        # save the original corpus
        corpus_temp = terms.kwargs["corpus"]
        groups = re.match(r'/home/aplm/nltk_data/corpora/c50/(.+)', corpus_temp.root.path)
        terms.kwargs["corpus"] = LazyCorpusLoader("c50_tags/" + groups.group(1), CategorizedPlaintextCorpusReader, r'.+/.+', cat_pattern=r'(.+)/.+')

        print "In ModeWeightClassCollocationPOS"
        cache_file = "%s.dat" % terms.name
        terms.tokens = []
        shelf = shelve.open(cache_file, protocol=2)

        for author in terms.kwargs["corpus"].categories():

            author_files = set(terms.kwargs["corpus"].fileids([author])) & set(terms.kwargs["source"])
            author_files = list(author_files)
            if len(author_files) == 0:
                continue

            author_files.sort()
            #print "str(author_files): " + str(author_files)
            #print "str(terms.kwargs["corpus"]): " + str(terms.kwargs["corpus"]) + " str(terms.kwargs["corpus"].fileids([author])): " + str(terms.kwargs["corpus"].fileids([author])) + " str(terms.kwargs[\"source\"]): " + str(terms.kwargs["source"])
            f_srcs = "|".join(author_files)

            terms.kwargs["string"] = \
            terms.kwargs["corpus"].raw(fileids=author_files).lower()

            if f_srcs in shelf and terms.kwargs["lazy"]:
                terms.tokens += shelf[f_srcs]
                #print(str(f_src))
                #print("%s ... Found in \"%s\"" % (f_src, cache_file))
            else:
                terms.kwargs["string"] = \
                terms.kwargs["corpus"].raw(fileids=author_files).lower()

                temp_tokens = terms.calc_terms()

                # because the latter function calc:terms get off this option,
                # but we still needed
                terms.kwargs["boolBuildSetGlobal"] = True
                terms.kwargs["mode"] = EnumModes.MODE_CORPUS_POS_GLOBAL_A
                ###############################################################

                terms.tokens += temp_tokens

                if terms.kwargs["lazy"]:
                    shelf[f_srcs] = temp_tokens

                #print ("%s ... Recalculated in \"%s\"" % (f_src, cache_file))
        terms.kwargs["boolBuildSetGlobal"] = False
        terms.kwargs["mode"] = EnumModes.MODE_CORPUS
        shelf.close()

        # restore the original corpus
        terms.kwargs["corpus"] = corpus_temp


# ==============================================================================


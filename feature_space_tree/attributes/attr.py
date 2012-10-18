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
# FeatureSpaceTree: Attributes module
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

"""
Util class to extract the attributes
"""

import re
import shelve
import codecs

import nltk.data
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import TrigramAssocMeasures
from nltk.corpus.reader.plaintext import CategorizedPlaintextCorpusReader
from nltk.corpus.reader.tagged import CategorizedTaggedCorpusReader
from nltk.corpus.util import LazyCorpusLoader

from attr_util import Util
from attr_util import RegExps

from abc import ABCMeta, abstractmethod
from nltk.tag import StanfordTagger
import Stemmer

from modes_config import EnumModes
from modes_config import FactoryMode

# -----------------------------------------------------------------------------
# All the following classes in a implicit way have the self.tokens property
# (we can say that it is the common interface of "Term"). This property will
# keep a list of strings. In each class this list is serialized in order
# to save time in future uses.

class Merged(object):
    def __init__(self, tokens):
        self.tokens = tokens


class Tokens(object):

    def __init__(self, kwargs_terms, term):
        self.term = term
        # print "KWARGS: " + str(kwargs_terms)

        cache_file = "%s.dat" % self.term.name

        self.tokens = []
        shelf = shelve.open(cache_file, protocol=2)
        for f_src in kwargs_terms["source"]:

            if f_src in shelf and kwargs_terms["lazy"]:
                self.tokens += shelf[f_src]
                #print(str(f_src))
                #print("%s ... Found in \"%s\"" % (f_src, cache_file))
            else:
                temp_tokens = self.term.calc_terms(kwargs_terms, f_src)
                self.tokens += temp_tokens

                if kwargs_terms["lazy"]:
                    shelf[f_src] = temp_tokens

                #print ("%s ... Recalculated in \"%s\"" % (f_src, cache_file))

        shelf.close()

#===============================================================================
# Terms are calculated based in a Strategy way. It choose the corpus mode, the
# string mode, and etc. This Strategy, pick the corresponding Template and cal-
# culates the terms delegating to the subclasses the concrete calculation.
#===============================================================================

class Terms(object):

    def __init__(self, kwargs_terms, name, m=EnumModes.MODE_STRING):
        # DEBUG: To see the content of kwargs
        # print kwargs_terms

        self.tokens = []
        self.kwargs = kwargs_terms

        # ----------------------------------------------------------------------
        # Get the name of the corpus.
        # this is useful because it handles the case where there are files with
        # the same name for a category but one in the train corpus, and the
        # other in the test corpus.
        #
        # This has to be in this way because in previous stages, we obtain all
        # the files for each corpus (train and test), and although each bunch of
        # files are in its own object, the "cache file" that we create is in
        # only one dictionary! This means that if we would have a file called
        # "Juan/texto_1.txt" in the corpus train and other in test corpus named
        # "Juan/texto_1", so we will have a problem with this "key" for our
        # python dictionary!!! (duplicated keys).

        match = re.match(".*/(.*)", self.kwargs["corpus"].root)
        corpus_name = match.group(1)

        # uncomment if you want to see the corpus_name
        # print corpus_name
        # ----------------------------------------------------------------------

        self.name = (kwargs_terms['term_path'] + "/"
                     + kwargs_terms["id_term"] + "_" + name + "_" + corpus_name)

        if "mode" in kwargs_terms:
            m = kwargs_terms["mode"]
        self.mode = FactoryMode.create(m)
        self.build_terms()

    def build_terms(self):
        self.mode.build_terms(self)

# ==============================================================================

class TermRegExp(Terms):

    def __init__(self, kwargs_terms):
        super(TermRegExp, self).__init__(kwargs_terms,
                                         "TermRegExp")

    def calc_terms(self):

        the_regexp = Util.get_the_regexp(self.kwargs)

        return Util.calc_regexp(self.kwargs["string"],
                                the_regexp)

class TermLocalRegExp(Terms):

    def __init__(self, kwargs_terms):
        super(TermLocalRegExp, self).__init__(kwargs_terms,
                                         "TermLocalRegExp")

    def calc_terms(self):

        the_regexp = Util.get_the_regexp(self.kwargs)

        return Util.calc_local_regexp(self.kwargs["string"],
                                the_regexp,
                                self.kwargs["local_k"])

class TermSplit(Terms):

    def __init__(self, kwargs_terms):
        super(TermSplit, self).__init__(kwargs_terms,
                                         "TermSplit")

    def calc_terms(self):
        return Util.calc_split(self.kwargs["string"])


class TermNGramChar(Terms):

    def __init__(self, kwargs_terms):
        super(TermNGramChar, self).__init__(kwargs_terms,
                                            "TermNGramChar")

    def calc_terms(self):
        return Util.calc_ngrams(self.kwargs["string"],
                                self.kwargs["nlen"])


class TermLocalNGramChar(Terms):

    def __init__(self, kwargs_terms):
        super(TermLocalNGramChar, self).__init__(kwargs_terms,
                                            "TermLocalNGramChar")

    def calc_terms(self):
        return Util.calc_local_ngrams(self.kwargs["string"],
                                self.kwargs["nlen"],
                                self.kwargs["local_k"])


class TermBigram(Terms):

    def __init__(self, kwargs_terms):
        super(TermBigram, self).__init__(kwargs_terms,
                                         "TermBigram")

    def calc_terms(self):
        the_regexp = Util.get_the_regexp(self.kwargs)

        return Util.calc_bigrams(self.kwargs["string"],
                                 the_regexp)

class TermTrigram(Terms):

    def __init__(self, kwargs_terms):
        super(TermTrigram, self).__init__(kwargs_terms,
                                         "TermTrigram")

    def calc_terms(self):
        the_regexp = Util.get_the_regexp(self.kwargs)

        return Util.calc_trigrams(self.kwargs["string"],
                                 the_regexp)

class TermNGramToken(Terms):

    def __init__(self, kwargs_terms):
        super(TermNGramToken, self).__init__(kwargs_terms,
                                            "TermNGramToken")

    def calc_terms(self):
        the_regexp = Util.get_the_regexp(self.kwargs)

        return Util.calc_ngrams_g(self.kwargs["string"],
                                 the_regexp,
                                 self.kwargs["nlen"])


class TermEmoticon(Terms):

    def __init__(self, kwargs_terms):
        super(TermNGramToken, self).__init__(kwargs_terms,
                                            "TermNGramToken")

    def calc_terms(self):
        the_regexp = Util.get_the_regexp(self.kwargs)

        return Util.calc_ngrams_g(self.kwargs["string"],
                                 the_regexp,
                                 self.kwargs["nlen"])


class TermCollocation(Terms):

    def __init__(self, kwargs_terms, name):
        super(TermCollocation, self).__init__(kwargs_terms,
                                              name)

    def calc_terms(self):
        print "#####################"
        print self.name
        print self.kwargs["boolBuildSetGlobal"]
        print "#####################"
        if self.kwargs["boolBuildSetGlobal"]:
            print "++++++++++++++++++++++#####################"
            print self.name
            print self.kwargs["boolBuildSetGlobal"]
            print "++++++++++++++++++++++#####################"
            self.kwargs["setCollocations"] = self.calc_collocation_set()
            self.kwargs["boolBuildSetGlobal"] = False
            self.kwargs["mode"] = EnumModes.MODE_CORPUS#MODE_CORPUS_POS
            return self.kwargs["setCollocations"]
        else:
            tokens = self.calc_collocation()
            return tokens


class TermAmbiguousWords(Terms):

    def __init__(self, kwargs_terms):
        super(TermAmbiguousWords, self).__init__(kwargs_terms,
                                                 "AmbiguousTags")

    def calc_terms(self):
        print "#####################"
        print self.name
        print self.kwargs["boolBuildSetGlobal"]
        print "#####################"
        if self.kwargs["boolBuildSetGlobal"]:
            print "++++++++++++++++++++++#####################"
            print self.name
            print self.kwargs["boolBuildSetGlobal"]
            print "++++++++++++++++++++++#####################"
            self.kwargs["setAmbiguous"] = Util.calc_ambiguous_words_set(self.kwargs['string'])
            self.kwargs["boolBuildSetGlobal"] = False
            self.kwargs["mode"] = EnumModes.MODE_CORPUS_POS#MODE_CORPUS_POS
            return self.kwargs["setAmbiguous"]
        else:
            tokens = Util.calc_ambiguous_words(self.kwargs['string'],
                                               self.kwargs['setAmbiguous'])
            return tokens


class TermBigramCollocation(TermCollocation):

    def __init__(self, kwargs_terms):
        super(TermBigramCollocation, self).__init__(kwargs_terms,
                                                    "TermBigramCollocation")

    def calc_collocation_set(self):
        return Util.calc_bigram_collocation_set(self.kwargs["string"],
                                                self.kwargs["regexp"],
                                                self.kwargs["boolStem"])

    def calc_collocation(self):
        return Util.calc_bigram_collocation(self.kwargs["string"],
                                            self.kwargs["regexp"],
                                            self.kwargs["boolStem"],
                                            self.kwargs["setCollocations"])


class TermTrigramCollocation(TermCollocation):

    def __init__(self, kwargs_terms):
        super(TermTrigramCollocation, self).__init__(kwargs_terms,
                                                     "TermTrigramCollocation")

    def calc_collocation_set(self):
        return Util.calc_trigram_collocation_set(self.kwargs["string"],
                                                self.kwargs["regexp"],
                                                self.kwargs["boolStem"])

    def calc_collocation(self):
        return Util.calc_trigram_collocation(self.kwargs["string"],
                                            self.kwargs["regexp"],
                                            self.kwargs["boolStem"],
                                            self.kwargs["setCollocations"])


class TermTokenLenght(Terms):

    def __init__(self, kwargs_terms):
        super(TermTokenLenght, self).__init__(kwargs_terms,
                                             "TokenLenght")

    def calc_terms(self):
        return Util.calc_token_lenght(self.kwargs["string"],
                                      self.kwargs["regexp"],
                                      self.kwargs["template"])#"word{len:%s}"


class TermSentLenght(Terms):

    def __init__(self, kwargs_terms):
        super(TermSentLenght, self).__init__(kwargs_terms,
                                             "SentLenght")

    def calc_terms(self):
        return Util.calc_sent_lenght(self.kwargs["string"],
                                     self.kwargs["regexp"],
                                     self.kwargs["template"])#"sentToken{len:%s}"


class TermSentStopsLenght(Terms):

    def __init__(self, kwargs_terms):
        super(TermSentStopsLenght, self).__init__(kwargs_terms,
                                                  "SentStopwordsLenght")

    def calc_terms(self):
        return Util.calc_sent_stopwords_lenght(self.kwargs["string"],
                                               RegExps.W_H_C)


class TermSentNOStopsLenght(Terms):

    def __init__(self, kwargs_terms):
        super(TermSentNOStopsLenght, self).__init__(kwargs_terms,
                                                    "SentNOStopwordsLenght")

    def calc_terms(self):
        return Util.calc_sent_nostopwords_lenght(self.kwargs["string"],
                                                 RegExps.W_H_C)


class TermBigramStop(Terms):

    def __init__(self, kwargs_terms):
        super(TermBigramStop, self).__init__(kwargs_terms,
                                             "TermBigramStopwords")

    def calc_terms(self):
        return Util.calc_bigrams(self.kwargs["string"],
                                 RegExps.STOPW,
                                 self.kwargs["boolStem"])


class TermTrigramStop(Terms):

    def __init__(self, kwargs_terms):
        super(TermTrigramStop, self).__init__(kwargs_terms,
                                              "TermTrigramStopwords")

    def calc_terms(self):
        return Util.calc_trigrams(self.kwargs["string"],
                                  RegExps.STOPW,
                                  self.kwargs["boolStem"])

class TermBigramStylePOS(Terms):

    def __init__(self, kwargs_terms):
        super(TermBigramStylePOS, self).__init__(kwargs_terms,
                                             "TermBigramStylePOS")

    def calc_terms(self):
        return Util.calc_bigrams(self.kwargs["string"],
                                 RegExps.STYLE_POS,
                                 self.kwargs["boolStem"])


class TermTrigramStylePOS(Terms):

    def __init__(self, kwargs_terms):
        super(TermTrigramStylePOS, self).__init__(kwargs_terms,
                                                  "TermTrigramStylePOS")

    def calc_terms(self):
        return Util.calc_trigrams(self.kwargs["string"],
                                  RegExps.STYLE_POS,
                                  self.kwargs["boolStem"])


class TermBigramCollocationStop(TermCollocation):

    def __init__(self, kwargs_terms):
        super(TermBigramCollocationStop, self).__init__(kwargs_terms,
                                                    "TermBigramCollocationStopwords")

    def calc_collocation_set(self):
        return Util.calc_bigram_collocation_set(self.kwargs["string"],
                                                RegExps.STOPW,
                                                self.kwargs["boolStem"])

    def calc_collocation(self):
        return Util.calc_bigram_collocation(self.kwargs["string"],
                                            RegExps.STOPW,
                                            self.kwargs["boolStem"],
                                            self.kwargs["setCollocations"])


class TermTrigramCollocationStop(TermCollocation):

    def __init__(self, kwargs_terms):
        super(TermTrigramCollocationStop, self).__init__(kwargs_terms,
                                                         "TermTrigramCollocationStopwords")

    def calc_collocation_set(self):
        return Util.calc_trigram_collocation_set(self.kwargs["string"],
                                                RegExps.STOPW,
                                                self.kwargs["boolStem"])

    def calc_collocation(self):
        return Util.calc_trigram_collocation(self.kwargs["string"],
                                            RegExps.STOPW,
                                            self.kwargs["boolStem"],
                                            self.kwargs["setCollocations"])

class TermBigramCollocationStopPuntc(TermCollocation):

    def __init__(self, kwargs_terms):
        super(TermBigramCollocationStopPuntc, self).__init__(kwargs_terms,
                                                    "TermBigramCollocationStopwordsPuntc")

    def calc_collocation_set(self):
        return Util.calc_bigram_collocation_set(self.kwargs["string"],
                                                RegExps.STOPW_PUNTC,
                                                self.kwargs["boolStem"])

    def calc_collocation(self):
        return Util.calc_bigram_collocation(self.kwargs["string"],
                                            RegExps.STOPW_PUNTC,
                                            self.kwargs["boolStem"],
                                            self.kwargs["setCollocations"])


class TermTrigramCollocationStopPuntc(TermCollocation):

    def __init__(self, kwargs_terms):
        super(TermTrigramCollocationStopPuntc, self).__init__(kwargs_terms,
                                                         "TermTrigramCollocationStopwordsPuntc")

    def calc_collocation_set(self):
        return Util.calc_trigram_collocation_set(self.kwargs["string"],
                                                RegExps.STOPW_PUNTC,
                                                self.kwargs["boolStem"])

    def calc_collocation(self):
        return Util.calc_trigram_collocation(self.kwargs["string"],
                                            RegExps.STOPW_PUNTC,
                                            self.kwargs["boolStem"],
                                            self.kwargs["setCollocations"])

class TermPOS(Terms):

    def __init__(self, kwargs_terms):
        super(TermPOS, self).__init__(kwargs_terms,
                                      "TermPOS")

    def calc_terms(self):
        pos_terms = Util.calc_lazy_POS(self.kwargs["string"],)
        return pos_terms


class TermSFM(Terms):

    def __init__(self, kwargs_terms):
        super(TermSFM, self).__init__(kwargs_terms,
                                      "TermSFM")

    def calc_terms(self, kwargs, f_src):
        # save the original corpus
        corpus_temp = kwargs["corpus"]

        groups = re.match(r'/home/aplm/nltk_data/corpora/c50/(.+)', corpus_temp.root.path)
        kwargs["corpus"] = LazyCorpusLoader("c50_term_SFM_23/" + groups.group(1), CategorizedPlaintextCorpusReader, r'.+/.+', cat_pattern=r'(.+)/.+')

        sfm_terms = Util.calc_SFM(kwargs["corpus"].raw(fileids=[f_src]))

        # restore the original corpus
        kwargs["corpus"] = corpus_temp
        return sfm_terms


class TermRegExpIgnore(Terms):

    def __init__(self, kwargs_terms):
        super(TermRegExpIgnore, self).__init__(kwargs_terms,
                                               "TermRegExpIgnore")

    def calc_terms(self):

        f_ignored_terms = open(self.kwargs["path_ignored_terms"])

        for line in f_ignored_terms:
            self.kwargs["string"] = self.kwargs["string"].replace(line.strip().lower(), "")
            print line.strip().lower()

        f_ignored_terms.close()

        return Util.calc_regexp(self.kwargs["string"],
                                self.kwargs["regexp"],
                                self.kwargs["boolStem"])

# -----------------------------------------------------------------------------


    

if __name__ == "__main__":
    print "You have to import this module!"
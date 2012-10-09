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
                                     self.kwargs["boolStem"],
                                     self.kwargs["template"])#"sentToken{len:%s}"


class TermSentStopsLenght(Terms):

    def __init__(self, kwargs_terms):
        super(TermSentStopsLenght, self).__init__(kwargs_terms,
                                                  "SentStopwordsLenght")

    def calc_terms(self):
        return Util.calc_sent_stopwords_lenght(self.kwargs["string"],
                                               RegExps.W_H_C,
                                               self.kwargs["boolStem"])


class TermSentNOStopsLenght(Terms):

    def __init__(self, kwargs_terms):
        super(TermSentNOStopsLenght, self).__init__(kwargs_terms,
                                                    "SentNOStopwordsLenght")

    def calc_terms(self):
        return Util.calc_sent_nostopwords_lenght(self.kwargs["string"],
                                                 RegExps.W_H_C,
                                                 self.kwargs["boolStem"])


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

#===============================================================================


class RegExps(object):

    W_H_C = r"[a-zA-Z']+-*[a-zA-Z']+"         # Words_Hyphens_Contractions
    PUNTC = r"[.]+|[,$?:;!()&%#=+{}*~.]+"
    STOPW = '''(?x)
            a|able|about|above|abst|accordance|according|accordingly|across|
            act|actually|added|adj|adopted|affected|affecting|affects|after|
            afterwards|again|against|ah|all|almost|alone|along|already|also|
            although|always|am|among|amongst|an|and|announce|another|any|
            anybody|anyhow|anymore|anyone|anything|anyway|anyways|anywhere|
            apparently|approximately|are|aren|arent|arise|around|as|aside|ask|
            asking|at|auth|available|away|awfully|back|be|became|because|become|
            becomes|becoming|been|before|beforehand|begin|beginning|beginnings|
            begins|behind|being|believe|below|beside|besides|between|beyond|
            biol|both|brief|briefly|but|by|ca|came|can|cannot|can't|cause|
            causes|certain|certainly|co|com|come|comes|contain|containing|
            contains|could|couldnt|date|did|didn't|different|do|does|doesn't|
            doing|done|don't|down|downwards|due|during|each|ed|edu|effect|eg|
            eight|eighty|either|else|elsewhere|end|ending|enough|especially|et|
            etc|even|ever|every|everybody|everyone|everything|everywhere|ex|
            except|far|few|ff|fifth|first|five|fix|followed|following|follows|
            for|former|formerly|forth|found|four|from|further|furthermore|gave|
            get|gets|getting|give|given|gives|giving|go|goes|gone|got|gotten|
            had|happens|hardly|has|hasn't|have|haven't|having|he|hed|hence|her|
            here|hereafter|hereby|herein|heres|hereupon|hers|herself|hes|hi|
            hid|him|himself|his|hither|home|how|howbeit|however|hundred|id|ie|
            if|i'll|im|immediate|immediately|importance|important|in|inc|
            indeed|index|information|instead|into|invention|inward|is|isn't|it|
            itd|it'll|its|itself|i've|just|keep|keeps|kept|keys|kg|km|know|
            known|knows|largely|last|lately|later|latter|latterly|least|less|
            lest|let|lets|like|liked|likely|line|little|'ll|look|looking|looks|
            ltd|made|mainly|make|makes|many|may|maybe|me|mean|means|meantime|
            meanwhile|merely|mg|might|million|miss|ml|more|moreover|most|
            mostly|mr|mrs|much|mug|must|my|myself|na|name|namely|nay|nd|near|
            nearly|necessarily|necessary|need|needs|neither|never|nevertheless|
            new|next|nine|ninety|no|nobody|non|none|nonetheless|noone|nor|
            normally|nos|not|noted|nothing|now|nowhere|obtain|obtained|
            obviously|of|off|often|oh|ok|okay|old|omitted|on|once|one|ones|only|
            onto|or|ord|other|others|otherwise|ought|our|ours|ourselves|out|
            outside|over|overall|owing|own|page|pages|part|particular|
            particularly|past|per|perhaps|placed|please|plus|poorly|possible|
            possibly|potentially|pp|predominantly|present|previously|primarily|
            probably|promptly|proud|provides|put|que|quickly|quite|qv|ran|
            rather|rd|re|readily|really|recent|recently|ref|refs|regarding|
            regardless|regards|related|relatively|research|respectively|
            resulted|resulting|results|right|run|said|same|saw|say|saying|says|
            sec|section|see|seeing|seem|seemed|seeming|seems|seen|self|selves|
            sent|seven|several|shall|she|shed|she'll|shes|should|shouldn't|show|
            showed|shown|showns|shows|significant|significantly|similar|
            similarly|since|six|slightly|so|some|somebody|somehow|someone|
            somethan|something|sometime|sometimes|somewhat|somewhere|soon|sorry|
            specifically|specified|specify|specifying|state|states|still|stop|
            strongly|sub|substantially|successfully|such|sufficiently|suggest|
            sup|sure|take|taken|taking|tell|tends|th|than|thank|thanks|thanx|
            that|that'll|thats|that've|the|their|theirs|them|themselves|then|
            thence|there|thereafter|thereby|thered|therefore|therein|there'll|
            thereof|therere|theres|thereto|thereupon|there've|these|they|theyd|
            they'll|theyre|they've|think|this|those|thou|though|thoughh|
            thousand|throug|through|throughout|thru|thus|til|tip|to|together|
            too|took|toward|towards|tried|tries|truly|try|trying|ts|twice|two|
            un|under|unfortunately|unless|unlike|unlikely|until|unto|up|upon|
            ups|us|use|used|useful|usefully|usefulness|uses|using|usually|
            value|various|'ve|very|via|viz|vol|vols|vs|want|wants|was|wasn't|
            way|we|wed|welcome|we'll|went|were|weren't|we've|what|whatever|
            what'll|whats|when|whence|whenever|where|whereafter|whereas|
            whereby|wherein|wheres|whereupon|wherever|whether|which|while|whim|
            whither|who|whod|whoever|whole|who'll|whom|whomever|whos|whose|why|
            widely|willing|wish|with|within|without|won't|words|world|would|
            wouldn't|www|yes|yet|you|youd|you'll|your|youre|yours|yourself|
            yourselves|you've|zero'''

    STOPW_PUNTC = '''(?x)
            a|able|about|above|abst|accordance|according|accordingly|across|
            act|actually|added|adj|adopted|affected|affecting|affects|after|
            afterwards|again|against|ah|all|almost|alone|along|already|also|
            although|always|am|among|amongst|an|and|announce|another|any|
            anybody|anyhow|anymore|anyone|anything|anyway|anyways|anywhere|
            apparently|approximately|are|aren|arent|arise|around|as|aside|ask|
            asking|at|auth|available|away|awfully|back|be|became|because|become|
            becomes|becoming|been|before|beforehand|begin|beginning|beginnings|
            begins|behind|being|believe|below|beside|besides|between|beyond|
            biol|both|brief|briefly|but|by|ca|came|can|cannot|can't|cause|
            causes|certain|certainly|co|com|come|comes|contain|containing|
            contains|could|couldnt|date|did|didn't|different|do|does|doesn't|
            doing|done|don't|down|downwards|due|during|each|ed|edu|effect|eg|
            eight|eighty|either|else|elsewhere|end|ending|enough|especially|et|
            etc|even|ever|every|everybody|everyone|everything|everywhere|ex|
            except|far|few|ff|fifth|first|five|fix|followed|following|follows|
            for|former|formerly|forth|found|four|from|further|furthermore|gave|
            get|gets|getting|give|given|gives|giving|go|goes|gone|got|gotten|
            had|happens|hardly|has|hasn't|have|haven't|having|he|hed|hence|her|
            here|hereafter|hereby|herein|heres|hereupon|hers|herself|hes|hi|
            hid|him|himself|his|hither|home|how|howbeit|however|hundred|id|ie|
            if|i'll|im|immediate|immediately|importance|important|in|inc|
            indeed|index|information|instead|into|invention|inward|is|isn't|it|
            itd|it'll|its|itself|i've|just|keep|keeps|kept|keys|kg|km|know|
            known|knows|largely|last|lately|later|latter|latterly|least|less|
            lest|let|lets|like|liked|likely|line|little|'ll|look|looking|looks|
            ltd|made|mainly|make|makes|many|may|maybe|me|mean|means|meantime|
            meanwhile|merely|mg|might|million|miss|ml|more|moreover|most|
            mostly|mr|mrs|much|mug|must|my|myself|na|name|namely|nay|nd|near|
            nearly|necessarily|necessary|need|needs|neither|never|nevertheless|
            new|next|nine|ninety|no|nobody|non|none|nonetheless|noone|nor|
            normally|nos|not|noted|nothing|now|nowhere|obtain|obtained|
            obviously|of|off|often|oh|ok|okay|old|omitted|on|once|one|ones|only|
            onto|or|ord|other|others|otherwise|ought|our|ours|ourselves|out|
            outside|over|overall|owing|own|page|pages|part|particular|
            particularly|past|per|perhaps|placed|please|plus|poorly|possible|
            possibly|potentially|pp|predominantly|present|previously|primarily|
            probably|promptly|proud|provides|put|que|quickly|quite|qv|ran|
            rather|rd|re|readily|really|recent|recently|ref|refs|regarding|
            regardless|regards|related|relatively|research|respectively|
            resulted|resulting|results|right|run|said|same|saw|say|saying|says|
            sec|section|see|seeing|seem|seemed|seeming|seems|seen|self|selves|
            sent|seven|several|shall|she|shed|she'll|shes|should|shouldn't|show|
            showed|shown|showns|shows|significant|significantly|similar|
            similarly|since|six|slightly|so|some|somebody|somehow|someone|
            somethan|something|sometime|sometimes|somewhat|somewhere|soon|sorry|
            specifically|specified|specify|specifying|state|states|still|stop|
            strongly|sub|substantially|successfully|such|sufficiently|suggest|
            sup|sure|take|taken|taking|tell|tends|th|than|thank|thanks|thanx|
            that|that'll|thats|that've|the|their|theirs|them|themselves|then|
            thence|there|thereafter|thereby|thered|therefore|therein|there'll|
            thereof|therere|theres|thereto|thereupon|there've|these|they|theyd|
            they'll|theyre|they've|think|this|those|thou|though|thoughh|
            thousand|throug|through|throughout|thru|thus|til|tip|to|together|
            too|took|toward|towards|tried|tries|truly|try|trying|ts|twice|two|
            un|under|unfortunately|unless|unlike|unlikely|until|unto|up|upon|
            ups|us|use|used|useful|usefully|usefulness|uses|using|usually|
            value|various|'ve|very|via|viz|vol|vols|vs|want|wants|was|wasn't|
            way|we|wed|welcome|we'll|went|were|weren't|we've|what|whatever|
            what'll|whats|when|whence|whenever|where|whereafter|whereas|
            whereby|wherein|wheres|whereupon|wherever|whether|which|while|whim|
            whither|who|whod|whoever|whole|who'll|whom|whomever|whos|whose|why|
            widely|willing|wish|with|within|without|won't|words|world|would|
            wouldn't|www|yes|yet|you|youd|you'll|your|youre|yours|yourself|
            yourselves|you've|zero|[.]+|[-,$?:;!()&%#=+{}*~.]+'''

    STOPW_ES = '''(?x)
            de|la|que|el|en|y|a|los|del|se|las|por|un|para|con|no|una|su|al|lo|
            como|más|pero|sus|le|ya|o|este|sí|porque|esta|entre|cuando|muy|sin|
            sobre|también|me|hasta|hay|donde|quien|desde|todo|nos|durante|todos|
            uno|les|ni|contra|otros|ese|eso|ante|ellos|e|esto|mí|antes|algunos|
            qué|unos|yo|otro|otras|otra|él|tanto|esa|estos|mucho|quienes|nada|
            muchos|cual|poco|ella|estar|estas|algunas|algo|nosotros|mi|mis|tú|
            te|ti|tu|tus|ellas|nosotras|vosostros|vosostras|os|mío|mía|míos|mías
            |tuyo|tuya|tuyos|tuyas|suyo|suya|suyos|suyas|nuestro|nuestra|
            nuestros|nuestras|vuestro|vuestra|vuestros|vuestras|esos|esas|estoy|
            estás|está|estamos|estáis|están|esté|estés|estemos|estéis|estén|
            estaré|estarás|estará|estaremos|estaréis|estarán|estaría|estarías|
            estaríamos|estaríais|estarían|estaba|estabas|estábamos|estabais|
            estaban|estuve|estuviste|estuvo|estuvimos|estuvisteis|estuvieron|
            estuviera|estuvieras|estuviéramos|estuvierais|estuvieran|estuviese|
            estuvieses|estuviésemos|estuvieseis|estuviesen|estando|estado|
            estada|estados|estadas|estad|he|has|ha|hemos|habéis|han|haya|hayas|
            hayamos|hayáis|hayan|habré|habrás|habrá|habremos|habréis|habrán|
            habría|habrías|habríamos|habríais|habrían|había|habías|habíamos|
            habíais|habían|hube|hubiste|hubo|hubimos|hubisteis|hubieron|hubiera|
            hubieras|hubiéramos|hubierais|hubieran|hubiese|hubieses|hubiésemos|
            hubieseis|hubiesen|habiendo|habido|habida|habidos|habidas|soy|eres|
            es|somos|sois|son|sea|seas|seamos|seáis|sean|seré|serás|será|
            seremos|seréis|serán|sería|serías|seríamos|seríais|serían|era|eras|
            éramos|erais|eran|fui|fuiste|fue|fuimos|fuisteis|fueron|fuera|fueras|
            fuéramos|fuerais|fueran|fuese|fueses|fuésemos|fueseis|fuesen|
            sintiendo|sentido|sentida|sentidos|sentidas|siente|sentid|tengo|
            tienes|tiene|tenemos|tenéis|tienen|tenga|tengas|tengamos|tengáis|
            tengan|tendré|tendrás|tendrá|tendremos|tendréis|tendrán|tendría|
            tendrías|tendríamos|tendríais|tendrían|tenía|tenías|teníamos|
            teníais|tenían|tuve|tuviste|tuvo|tuvimos|tuvisteis|tuvieron|tuviera|
            tuvieras|tuviéramos|tuvierais|tuvieran|tuviese|tuvieses|tuviésemos|
            tuvieseis|tuviesen|teniendo|tenido|tenida|tenidos|tenidas|tened'''

    STYLE_POS = r"cc|cd|dt|ex|fw|in|jj|jjr|jjs|ls|md|pdt|pos|prp|prp$|rb|rbr|rbs|rp|sym|to|uh|vb|vbd|vbg|vbn|vbp|vbz|wdt|wp|wp$|wrb|[.]+|[,$?:;!()&%#=+{}*~.]+"#r"CC|CD|DT|EX|FW|IN|JJ|JJR|JJS|LS|MD|PDT|POS|PRP|PRP$|RB|RBR|RBS|RP|SYM|TO|UH|VB|VBD|VBG|VBN|VBP|VBZ|WDT|WP|WP$|WRB"#NN|NNS|NNP|NNPS|
# TAGS OF THE TREEBANK CORPUS
#1.     CC     Coordinating conjunction
#2.     CD     Cardinal number
#3.     DT     Determiner
#4.     EX     Existential there
#5.     FW     Foreign word
#6.     IN     Preposition or subordinating conjunction
#7.     JJ     Adjective
#8.     JJR     Adjective, comparative
#9.     JJS     Adjective, superlative
#10.     LS     List item marker
#11.     MD     Modal
#12.     NN     Noun, singular or mass
#13.     NNS     Noun, plural
#14.     NNP     Proper noun, singular
#15.     NNPS     Proper noun, plural
#16.     PDT     Predeterminer
#17.     POS     Possessive ending
#18.     PRP     Personal pronoun
#19.     PRP$     Possessive pronoun
#20.     RB     Adverb
#21.     RBR     Adverb, comparative
#22.     RBS     Adverb, superlative
#23.     RP     Particle
#24.     SYM     Symbol
#25.     TO     to
#26.     UH     Interjection
#27.     VB     Verb, base form
#28.     VBD     Verb, past tense
#29.     VBG     Verb, gerund or present participle
#30.     VBN     Verb, past participle
#31.     VBP     Verb, non-3rd person singular present
#32.     VBZ     Verb, 3rd person singular present
#33.     WDT     Wh-determiner
#34.     WP     Wh-pronoun
#35.     WP$     Possessive wh-pronoun
#36.     WRB     Wh-adverb
#===============================================================================



# Regular Expression for URL validation
#
# Author: Diego Perini
# Updated: 2010/12/05
#
# the regular expression composed & commented
# could be easily tweaked for RFC compliance,
# it was expressly modified to fit & satisfy
# these test for an URL shortener:
#
#   http://mathiasbynens.be/demo/url-regex
#
# Notes on possible differences from a standard/generic validation:
#
# - utf-8 char class take in consideration the full Unicode range
# - TLDs have been made mandatory so single names like "localhost" fails
# - protocols have been restricted to ftp, http and https only as requested
#
# Changes:
#
# - IP address dotted notation validation, range: 1.0.0.0 - 223.255.255.255
#   first and last IP address of each class is considered invalid
#   (since they are broadcast/network addresses)
#
# - Added exclusion of private, reserved and/or local networks ranges
#
# Compressed one-line versions:
#
# Javascript version
#
# /^(?:(?:https?|ftp):\/\/)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/[^\s]*)?$/i
#
# PHP version
#
# _^(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)(?:\.(?:[a-z\x{00a1}-\x{ffff}0-9]+-?)*[a-z\x{00a1}-\x{ffff}0-9]+)*(?:\.(?:[a-z\x{00a1}-\x{ffff}]{2,})))(?::\d{2,5})?(?:/[^\s]*)?$_iuS

    URL =  ("" +
            # protocol identifier
            "(?:(?:https?|ftp)://)" +
            # user:pass authentication
            "(?:\\S+(?::\\S*)?@)?" +
            "(?:" +
            # IP address exclusion
            # private & local networks
            "(?!10(?:\\.\\d{1,3}){3})" +
            "(?!127(?:\\.\\d{1,3}){3})" +
            "(?!169\\.254(?:\\.\\d{1,3}){2})" +
            "(?!192\\.168(?:\\.\\d{1,3}){2})" +
            "(?!172\\.(?:1[6-9]|2\\d|3[0-1])(?:\\.\\d{1,3}){2})" +
            # IP address dotted notation octets
            # excludes loopback network 0.0.0.0
            # excludes reserved space >= 224.0.0.0
            # excludes network & broacast addresses
            # (first & last IP address of each class)
            "(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])" +
            "(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}" +
            "(?:\\.(?:[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-4]))" +
            "|" +
            # host name
            "(?:(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)" +
            # domain name
            "(?:\\.(?:[a-z\\u00a1-\\uffff0-9]+-?)*[a-z\\u00a1-\\uffff0-9]+)*" +
            # TLD identifier
            "(?:\\.(?:[a-z\\u00a1-\\uffff]{2,}))" +
            ")" +
            # port number
            "(?::\\d{2,5})?" +
            # resource path
            "(?:/[^\\s]*)?" +
            "", "i" )[0];

    EMOTION = r"""[<>]?[:;=8][\-o\*\']?[\)\]\(\[oOdDpP/\:\}\{@\|\\3\*]|[\)\]\(\[oOdDpP/\:\}\{@\|\\3\*][\-o\*\']?[:;=8][<>]?"""

    TWITTER_USER = r"@[\w_]+"

    TWITTER_HASHTAG = r"\#+[\w_]+[\w\'_\-]*[\w_]+"   
    

if __name__ == "__main__":
    print "You have to import this module!"
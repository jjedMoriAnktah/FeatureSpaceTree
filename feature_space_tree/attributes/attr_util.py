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

import re
import nltk.data
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from nltk.metrics import TrigramAssocMeasures

from nltk.tag import StanfordTagger
import Stemmer

class Util(object):

    #shelf_ngram_char = shelve.open("TermNGramChar.txt", protocol=2)
    #shelf_ngram_word = shelve.open("TermNGramWord.txt", protocol=2)
    #shelf_regexp = shelve.open("TermRegExp.txt", protocol=2)

    @staticmethod
    def get_the_regexp(kwargs):
        the_regexp = kwargs['regexp']
        if ('defined_regexp' in kwargs):
            if (kwargs['defined_regexp'] == True):
                the_regexp = eval(the_regexp)
                # print the_regexp
        return the_regexp

    @staticmethod
    def applyStem(my_list):
        porter = Stemmer.PorterStemmer()
        data = []
        for token in my_list:
            if re.match(r'[a-z]+', token):
                token=porter.stem(token, 0, len(token)-1)

            data +=[token]

        return data

    @staticmethod
    def applyRepeater(my_list, bias):
        data = []
        for token in my_list:
            i = 0
            cont = 0
            flag_exag = False
            for c in token:
                #print token
                #print c
                #print i
                #print cont
                #print flag_exag
                #print '(i+1): ' + str(i+1) + ' < len(token): ' + str(len(token)) + ' and c == token[i+1]'
                if (i+1) < len(token):
                    if c == token[i+1]:
                        cont += 1
                        if cont >= bias:
                            print "WORD REPEATING DETECTED : " + token
                            data += ['exag']
                            cont = 0
                            flag_exag = True
                            break
                    else:
                        cont = 0
                i += 1

                #print ""

            if not flag_exag:
                data += [token]

        return data

    @staticmethod
    def calc_ngrams(string, nlen):
        inputstring = string
        c = re.compile(r"\s")
        inputstring = inputstring.strip()
        inputstring = c.sub("~", inputstring)
        return [inputstring[x:x+nlen] for x in xrange(len(inputstring)-nlen+1)]

    @staticmethod
    def calc_local_ngrams(string, nlen, k):
        inputstring = string
        c = re.compile(r"\s")
        inputstring = inputstring.strip()
        inputstring = c.sub("~", inputstring)
        tokens = [inputstring[x:x+nlen] for x in xrange(len(inputstring)-nlen+1)]
        size_partition = len(tokens) / k
        #fd = nltk.FreqDist(tokens)
        #set_valid_tokens = set(fd.keys()[:2500])

        final_tokens = []

        processed_tokens = 0
        current_partition = 0
        for token in tokens:

            if(processed_tokens >= size_partition):
                processed_tokens = 0
                if current_partition >= k:
                    current_partition = k - 1
                else:
                    current_partition += 1

            #if(set([token]) & set_valid_tokens):
            final_tokens += ["partition_%s{%s}" % (current_partition, token)]

            processed_tokens += 1

        return final_tokens

    @staticmethod
    def calc_local_regexp(string, regexp, k):

        tokens = nltk.regexp_tokenize(string, regexp)

        size_partition = len(tokens) / k
        #fd = nltk.FreqDist(tokens)
        #set_valid_tokens = set(fd.keys()[:2500])

        final_tokens = []

        processed_tokens = 0
        current_partition = 0
        for token in tokens:

            if(processed_tokens >= size_partition):
                processed_tokens = 0
                if current_partition >= k:
                    current_partition = k - 1
                else:
                    current_partition += 1

            #if(set([token]) & set_valid_tokens):
            final_tokens += ["partition_%s{%s}" % (current_partition, token)]

            processed_tokens += 1

        return final_tokens


    @staticmethod
    def calc_bigrams(string, regexp):
        tokens = nltk.regexp_tokenize(string, regexp)

        bigrams = nltk.bigrams(tokens)

        final_tokens = []
        for bigram in bigrams:
            final_tokens += ['~'.join(list(bigram))]

        return final_tokens

    @staticmethod
    def calc_trigrams(string, regexp):
        tokens = nltk.regexp_tokenize(string, regexp)

        trigrams = nltk.trigrams(tokens)

        final_tokens = []
        for trigram in trigrams:
            final_tokens += ['~'.join(list(trigram))]

        return final_tokens

    @staticmethod
    def calc_ngrams_g(string, regexp, n):
        tokens = nltk.regexp_tokenize(string, regexp)

        ngrams = nltk.ngrams(tokens, n)

        final_tokens = []
        for ngram in ngrams:
            final_tokens += ['~'.join(list(ngram))]

        return final_tokens

    @staticmethod
    def calc_regexp(string, regexp):
        #print 'string: ' + str(type(string))
        #print 'regexp: ' + str(type(regexp))
        tokens = nltk.regexp_tokenize(string, regexp)

#        f = open("/home/aplm/orig.txt" , "w")
#        f.write("\n\n\n")
#        f.write(string+"\n\n\n")
#
#        f.close()
#
#        f = open("/home/aplm/todo.txt" , "w")
#
#        f.write(str(tokens))
#
#        f.close()
#
#        f = open("/home/aplm/todo2.txt" , "w")
#
#        infor = u' '.join(tokens)
#
#        f.write(infor.encode("utf-8"))
#
#        f.close()
#        #print "NO STEM!!!"
#        if boolStem:
#            print "STEM!!!"
#            tokens = Util.applyStem(tokens)

        return tokens

    @staticmethod
    def calc_split(string):
        tokens = string.split()
        return tokens

    @staticmethod
    def calc_ambiguous_words_set(string):
        term_tuples = [nltk.tag.str2tuple(t) for t in string.strip().lower().split()]
        #print "set_term: " + str(term_tuples)

        cfdist = nltk.ConditionalFreqDist(term_tuples)

        final_tokens = []

        for term in cfdist.conditions():
            tags = cfdist[term].keys()

            noun_flag = False
            for tag in tags:
                if tag.startswith('NN'):
                    noun_flag = True

            if not noun_flag:
                final_tokens += [term + "/" + tag.lower() for tag in tags]
#        for term in cfdist.conditions():
#            if len(cfdist[term]) > 2:
#                tags = cfdist[term].keys()
#                final_tokens += [term + "/" + tag.lower() for tag in tags]

        return final_tokens

    @staticmethod
    def calc_ambiguous_words(string, set_ambiguous_terms):
        terms = string.strip().lower().split()
        print terms

        valid_set_ambiguous_terms = set(terms) & set(set_ambiguous_terms)
        final_tokens = []
        for t in terms:
            print "term: " + str(t)
            print "set_term: " + str(valid_set_ambiguous_terms)

            if t in valid_set_ambiguous_terms:
                print "IN THE AMBIGUOUS SET."
                final_tokens += [t]

        return final_tokens

    @staticmethod
    def calc_bigram_collocation(string, regexp, boolStem, set_bigram_collocations):
        tokens = nltk.regexp_tokenize(string, regexp)

        if boolStem:
            tokens = Util.applyStem(tokens)

        bigrams = nltk.bigrams(tokens)
        final_tokens = []
        for bigram in bigrams:
            final_tokens += ['~'.join(list(bigram))]

        valid_set_bigram_collocations = set(final_tokens) & set(set_bigram_collocations)

        final_tokens = [token
                        for token in final_tokens
                        if token in valid_set_bigram_collocations]

        return final_tokens

    @staticmethod
    def calc_trigram_collocation(string, regexp, boolStem, set_trigram_collocations):
        tokens = nltk.regexp_tokenize(string, regexp)

        if boolStem:
            tokens = Util.applyStem(tokens)

        trigrams = nltk.trigrams(tokens)
        final_tokens = []
        for trigram in trigrams:
            final_tokens += ['~'.join(list(trigram))]

        valid_set_trigram_collocations = set(final_tokens) & set(set_trigram_collocations)

        final_tokens = [token
                        for token in final_tokens
                        if token in valid_set_trigram_collocations]

        return final_tokens


    @staticmethod
    def calc_bigram_collocation_set(string, regexp, boolStem):
        tokens = nltk.regexp_tokenize(string, regexp)

        if boolStem:
            tokens = Util.applyStem(tokens)

        bigram_collocation_finder = \
        BigramCollocationFinder.from_words(tokens)
        #bigram_collocation_finder.apply_freq_filter(10)
        bigrams = \
        bigram_collocation_finder.nbest(BigramAssocMeasures.chi_sq, len(tokens)/10)
        #bigram_collocation_finder.apply_freq_filter(2)

        final_tokens = []
        for bigram in bigrams:
            final_tokens += ['~'.join(list(bigram))]

        return final_tokens

    @staticmethod
    def calc_trigram_collocation_set(string, regexp, boolStem):
        tokens = nltk.regexp_tokenize(string, regexp)

        if boolStem:
            tokens = Util.applyStem(tokens)

        trigram_collocation_finder = \
        TrigramCollocationFinder.from_words(tokens)
        #trigram_collocation_finder.apply_freq_filter(5)
        trigrams = \
        trigram_collocation_finder.nbest(TrigramAssocMeasures.chi_sq, len(tokens)/10)
        #trigram_collocation_finder.apply_freq_filter(2)

        final_tokens = []
        for trigram in trigrams:
            final_tokens += ['~'.join(list(trigram))]

        return final_tokens

    @staticmethod
    def calc_token_lenght(string, regexp, template):
        tokens_temp = nltk.regexp_tokenize(string, regexp)

        tokens = []
        for token in tokens_temp:
            elem = ""
            l = len(token)

#            if l <= 15:
#                elem = "word{len:"+str(l)+"}"
#            elif l <= 18:
#                elem = "word{len:16_18}"
#            else:
#                elem = "word{len:>=19}"

            elem = template % str(l)#"word{len:"+str(l)+"}"
            tokens += [elem]

        return tokens

    @staticmethod
    def calc_sent_lenght(string, regexp, template):
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sents = tokenizer.tokenize(string)

        tokens = []
        for sent in sents:
            elem = ""
            l = len(nltk.regexp_tokenize(sent, regexp))

#            if l <= 5:
#                elem = template % "<=5"
#            elif l <= 40:
#                elem = template % str(l)
#            elif l <= 50:
#                elem = template % "41_50"
#            elif l <= 70:
#                elem = template % "51_70"
#            else:
#                elem = template % ">=71"

            elem = template % str(l)
            tokens += [elem]

        return tokens

    @staticmethod
    def calc_sent_stopwords_lenght(string, regexp):
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sents = tokenizer.tokenize(string)

        english_stopwords = set(stopwords.words('english'))
        tokens= []

        for sent in sents:
            elem = ""
            l = len([word
                     for word in nltk.regexp_tokenize(sent, regexp)
                     if word in english_stopwords])

#            if l <= 19:
#                elem = "sent_stop{len:" + str(l) + "}"
#            else:
#                elem = "sent_stop{len:>=20}"

            elem = "sent_stop{len:" + str(l) + "}"
            tokens += [elem]

        return tokens

    @staticmethod
    def calc_sent_nostopwords_lenght(string, regexp):
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        sents = tokenizer.tokenize(string)

        english_stopwords = set(stopwords.words('english'))

        tokens = []
        for sent in sents:
            elem = ""
            l = len([word
                     for word in nltk.regexp_tokenize(sent, regexp)
                     if word not in english_stopwords])

#            if l <=30:
#                elem = "sent_nostop{len:" + str(l) + "}"
#            else:
#                elem = "sent_nostop{len:>=31}"

            elem = "sent_nostop{len:" + str(l) + "}"
            tokens += [elem]

        return tokens

    @staticmethod
    def calc_SFM(string):
        return string.split()

#    @staticmethod
#    def get_merged_tokens(kwargs):
#
#        tokens = []
#        for kwarg in kwargs:
#            tokens += FactoryTermLex.create(kwarg["type_term"], [kwarg]).tokens
#
#        return tokens


    @staticmethod
    def calc_POS(string, regexp, boolStem):
        tokens = nltk.regexp_tokenize(string, regexp)

        if boolStem:
            tokens = Util.applyStem(tokens)

        tagger = StanfordTagger('../lib/stanford-postagger-2012-01-06/models/' +
                                'english-bidirectional-distsim.tagger',
                                '../lib/stanford-postagger-2012-01-06/' +
                                'stanford-postagger.jar')

        tagged_tokens = tagger.tag(tokens)

        final_tokens = []
        for (token, tag) in tagged_tokens:
            final_tokens += [tag]

        return final_tokens


    @staticmethod
    def calc_lazy_POS(string):
        final_tokens = string.split()
        return final_tokens
    
    
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
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
    def calc_sent_lenght(string, regexp, boolStem, template):
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
    def calc_sent_stopwords_lenght(string, regexp, boolStem):
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
    def calc_sent_nostopwords_lenght(string, regexp, boolStem):
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
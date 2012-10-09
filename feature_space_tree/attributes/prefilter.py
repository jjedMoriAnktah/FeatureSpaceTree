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


# ==============================================================================
# The following classes helps to normalize the text when each term is being
# extracted. The "ByTokenNormalizer" like classes are normalizer applied after
# each term is extracted, this is when we have the tokens in a list. For example,
# when all the words are extracted using TermRegExp calc_terms method, in this
# way, each token receives the normalization.

# The RawStringNormalizer
# ==============================================================================



import re
import codecs
from abc import ABCMeta, abstractmethod
from attr import Util

class RawStringNormalizer(object):

    __metaclass__ = ABCMeta

    def __init__(self, raw_string):
        self._raw_string = raw_string

    @abstractmethod
    def get_raw_string(self):
        return self._raw_string


class EmptyRawStringNormalizer(RawStringNormalizer):

    def __init__(self, raw_string):
        super(EmptyRawStringNormalizer, self).__init__(raw_string)

    def get_raw_string(self):
        return self._raw_string


class DecoratorRawStringNormalizer(RawStringNormalizer):

    __metaclass__ = ABCMeta

    def __init__(self, raw_string_normalizer):
        self._raw_string_normalizer = raw_string_normalizer

    @abstractmethod
    def get_raw_string(self):
        return self._raw_string_normalizer.get_raw_string()


class ToLowerDecoratorRawStringNormalizer(DecoratorRawStringNormalizer):

    def __init__(self, raw_string_normalizer):
        super(ToLowerDecoratorRawStringNormalizer, self).__init__(raw_string_normalizer)

    def get_raw_string(self):

        old_raw_string = self._raw_string_normalizer.get_raw_string()

        new_raw_string = old_raw_string.lower()

        return new_raw_string


class ToUpperDecoratorRawStringNormalizer(DecoratorRawStringNormalizer):

    def __init__(self, raw_string_normalizer):
        super(ToUpperDecoratorRawStringNormalizer, self).__init__(raw_string_normalizer)

    def get_raw_string(self):

        old_raw_string = self._raw_string_normalizer.get_raw_string()

        new_raw_string = old_raw_string.upper()

        return new_raw_string


class JustRegExpDecoratorRawStringNormalizer(DecoratorRawStringNormalizer):
    '''
    This decorator returns an string just with the tokens extracted using the
    regular expression in regexp. One use of this filter is when you want to
    get n-grams but just using the words, and omiting all other tokens, for
    instace punctuation marks and numbers.

    If you want the inverse thing (ignore specific character or tokens), you
    should use/build another filter.
    '''

    def __init__(self, raw_string_normalizer, regexp):
        super(JustRegExpDecoratorRawStringNormalizer, self).__init__(raw_string_normalizer)
        self.regexp = regexp

    def get_raw_string(self):

        old_raw_string = self._raw_string_normalizer.get_raw_string()

        list_of_tokens = Util.calc_regexp(old_raw_string, self.regexp)

        new_raw_string = " ".join(list_of_tokens)

        return new_raw_string


class IgnoreStringsDecoratorRawStringNormalizer(DecoratorRawStringNormalizer):
    '''
    This decorator returns an string just with the tokens extracted using the
    regular expression in regexp. One use of this filter is when you want to
    get n-grams but just using the words, and omiting all other tokens, for
    instace punctuation marks and numbers.

    If you want the inverse thing (ignore specific character or tokens), you
    should use/build another filter.
    '''

    def __init__(self, raw_string_normalizer, path_ignored_strings, to_lower = False):
        super(IgnoreStringsDecoratorRawStringNormalizer, self).__init__(raw_string_normalizer)
        self.path_ignored_strings = path_ignored_strings
        self.to_lower = to_lower

    def get_raw_string(self):

        old_raw_string = self._raw_string_normalizer.get_raw_string()

        f_ignored_strings = codecs.open(self.path_ignored_strings, encoding='utf-8')
        for line in f_ignored_strings:
            if self.to_lower:
                line = line.lower()
            old_raw_string = old_raw_string.replace(line.strip(), "")
            #print line.strip()
        f_ignored_strings.close()

        new_raw_string = old_raw_string

        return new_raw_string


class ReplaceRegExpDecoratorRawStringNormalizer(DecoratorRawStringNormalizer):
    '''
    '''

    def __init__(self, raw_string_normalizer, regexp, replacement):
        super(ReplaceRegExpDecoratorRawStringNormalizer, self).__init__(raw_string_normalizer)
        self.regexp = regexp
        self.replacement = replacement

    def get_raw_string(self):

        old_raw_string = self._raw_string_normalizer.get_raw_string()
        # print self.regexp
        # print old_raw_string
        # print re.findall(self.regexp,old_raw_string)
        old_raw_string = re.sub(self.regexp, self.replacement, old_raw_string)

        new_raw_string = old_raw_string

        return new_raw_string
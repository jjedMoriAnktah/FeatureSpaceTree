# ==============================================================================
# The following classes helps to normalize the text when each term is being
# extracted. The "ByTokenNormalizer" like classes are normalizer applied after
# each term is extracted, this is when we have the tokens in a list. For example,
# when all the words are extracted using TermRegExp calc_terms method, in this
# way, each token receives the normalization.

# The RawStringNormalizer
# ==============================================================================
from prefilter import *

class Util(object):

    @staticmethod
    def decorate_raw_string(raw_string_normalizer,
                            raw_string_normalizers):

        for kwargs_raw_string_normalizer in raw_string_normalizers:

            decorated_raw_string_normalizer = FactorySimpleDecoratorRawStringNormalizer.create(kwargs_raw_string_normalizer['type_raw_string_normalizer'],
                                                                                               kwargs_raw_string_normalizer,
                                                                                               raw_string_normalizer)

            raw_string_normalizer = decorated_raw_string_normalizer

        return raw_string_normalizer


class EnumDecoratorRawStringNormalizer(object):

    (TO_LOWER,
     TO_UPPER,
     JUST_REGEXP,
     IGNORE_STRINGS,
     REPLACE_REGEXP) = range(5)
     

class FactorySimpleDecoratorRawStringNormalizer(object):

    @staticmethod
    def create(option, kwargs, raw_string_normalizer):
        # DEBUG: print "????????" + str(option)
        option = eval(option)
        
        if option == EnumDecoratorRawStringNormalizer.TO_LOWER:
            return ToLowerDecoratorRawStringNormalizer(raw_string_normalizer)
        
        elif option == EnumDecoratorRawStringNormalizer.TO_UPPER:
            return ToUpperDecoratorRawStringNormalizer(raw_string_normalizer)
        
        elif option == EnumDecoratorRawStringNormalizer.JUST_REGEXP:
            return JustRegExpDecoratorRawStringNormalizer(raw_string_normalizer,
                                                          kwargs['regexp'])
            
        elif option == EnumDecoratorRawStringNormalizer.IGNORE_STRINGS:
            return IgnoreStringsDecoratorRawStringNormalizer(raw_string_normalizer,
                                                          kwargs['path_ignored_strings'],
                                                          (False, True)['to_lower' in kwargs])
        
        elif option == EnumDecoratorRawStringNormalizer.REPLACE_REGEXP:
            regexp = Util.get_the_regexp(kwargs)
            return ReplaceRegExpDecoratorRawStringNormalizer(raw_string_normalizer,
                                                             regexp,
                                                             kwargs['replacement'])
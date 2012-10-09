from postfilter import *

class Util(object):

    @staticmethod
    def decorate_by_token_normalizer(by_token_normalizer,
                                     by_token_normalizers):
        for kwargs_by_token_normalizer in by_token_normalizers:

            decorated_by_token_normalizer = FactorySimpleDecoratorByTokenNormalizer.create(kwargs_by_token_normalizer['type_by_token_normalizer'],
                                                                                           kwargs_by_token_normalizer,
                                                                                           by_token_normalizer)

            by_token_normalizer = decorated_by_token_normalizer

        return by_token_normalizer

class EnumDecoratorByTokenNormalizer(object):

    (STEMMER,
     TOKEN_X_COLAPSE,
     INVERSE_SPECIFIC_FILTER,
     CHAR_REPEATER,
     INVERSE_CONTAINS_SPECIFIC_FILTER) = range(5)
     

class FactorySimpleDecoratorByTokenNormalizer(object):

    @staticmethod
    def create(option, kwargs, by_token_normalizer):
        # DEBUG: print "#######" + str(option)
        option = eval(option)
        if option == EnumDecoratorByTokenNormalizer.STEMMER:
            return StemmerDecoratorByTokenNormalizer(by_token_normalizer)
        
        if option == EnumDecoratorByTokenNormalizer.TOKEN_X_COLAPSE:
            return TokenXColapseDecoratorByTokenNormalizer(by_token_normalizer, kwargs['token'], kwargs['until'])
        
        if option == EnumDecoratorByTokenNormalizer.INVERSE_SPECIFIC_FILTER:
            return InverseSpecificFilterDecoratorByTokenNormalizer(by_token_normalizer, kwargs['tokens'])
        
        if option == EnumDecoratorByTokenNormalizer.CHAR_REPEATER:
            return CharRepeaterDecoratorByTokenNormalizer(by_token_normalizer, kwargs['bias'])
        
        if option == EnumDecoratorByTokenNormalizer.INVERSE_CONTAINS_SPECIFIC_FILTER:
            return InverseContainsSpecificFilterDecoratorByTokenNormalizer(by_token_normalizer, kwargs['tokens'])
        

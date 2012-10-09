#===============================================================================
# Modes are Templates to choose how the terms will be calculated. The ModeCorpus
# receive the object corpus in kwargs["corpus"] and a list of files(can be a
# list of one)in kwargs[sources]; it iterates and get the respective tokens.
# The ModeString calculates the tokens in kwargs["string"].
#===============================================================================

from mode_options import EnumModes
from modes import *
     

class FactoryMode(object):

    @staticmethod
    def create(option):

        if option == EnumModes.MODE_CORPUS:
            return ModeCorpus()
        
        elif option == EnumModes.MODE_STRING:
            return ModeString()
        
        elif option == EnumModes.MODE_GLOBALW:
            return ModeWeightGlobalCollocation()
        
        elif option == EnumModes.MODE_GLOBALA:
            return ModeWeightAuthorCollocation()
        
        elif option == EnumModes.MODE_CORPUS_POS:
            return ModeCorpusPOS()
        
        elif option == EnumModes.MODE_CORPUS_POS_GLOBAL_A:
            return ModeWeightAuthorCollocationPOS()
        
        elif option == EnumModes.MODE_CORPUS_AUTHOR_POS:
            return ModeWeightAuthorPOS()
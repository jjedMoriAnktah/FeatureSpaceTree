import codecs
from prefilter import DecoratorRawStringNormalizer

class IgnoreStringsDecoratorRawStringNormalizer(DecoratorRawStringNormalizer):
    '''
    This decorator returns an string that ignore Strings in the path_ignored_string 
    file. One use of this filter is when you want to clean a String from some TAGS :)
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
    


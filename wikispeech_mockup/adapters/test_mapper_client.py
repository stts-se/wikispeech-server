import unittest
try:
    from wikispeech_mockup.adapters.mapper_client import *
except:
    from mapper_client import *

import wikispeech_mockup.log as log


    
class TestMapper(unittest.TestCase):

    def testNewMapper(self):
        from_symbol_set = "sv-se_ws-sampa"
        to_symbol_set = "sv-se_sampa_mary"
        mapper = Mapper(from_symbol_set, to_symbol_set)
        self.assertEqual(str(type(mapper)), "<class 'wikispeech_mockup.adapters.mapper_client.Mapper'>")

    def testMap(self):
        from_symbol_set = "sv-se_ws-sampa"
        to_symbol_set = "sv-se_sampa_mary"
        mapper = Mapper(from_symbol_set, to_symbol_set)

        expected = "\" A: - p a"
        trans = "\"\" A: . p a"
        result = mapper.map(trans)
        self.assertEqual(expected,result)

    def testMapperException1(self):
        from_symbol_set = "sv-se_ws-sampa_DOES_NOT_EXIST"
        to_symbol_set = "sv-se_sampa_mary_DOES_NOT_EXIST"
        log.log_level = "fatal"
        with self.assertRaises(MapperException):
            mapper = Mapper(from_symbol_set, to_symbol_set)
        
    def testMapperException2(self):
        from_symbol_set = "sv-se_ws-sampa"
        to_symbol_set = "sv-se_sampa_mary"
        log.log_level = "fatal"
        with self.assertRaises(MapperException):
            mapper = Mapper(from_symbol_set, to_symbol_set)
            mapper.from_symbol_set = "SYMBOL_SET_THAT_DOES_NOT_EXIST"
            mapper.map("\" A: . p a")
        
        
if __name__ == "__main__":
    log.log_level = "error" #debug, info, warning, error
    unittest.main()

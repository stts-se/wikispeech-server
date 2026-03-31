from . import textproc_adapter
#import textproc_adapter

class TestSSML:
    
    def testSubAlias1(self):
        input = "<speak>Jag heter <sub alias=\"Karl den tolfte\">Karl XII</sub></speak>"
        expect = [
            {'text': 'Jag heter', 'type': 'text'},
            {'text': 'Karl XII', 'type': 'alias', 'alias': 'Karl den tolfte'}
        ]
        output = textproc_adapter.mapSSMLToTextproc(input)
        assert output == expect

    def testPhoneme1(self):
        input = "<speak>Jag heter <phoneme ph=\"' a . p a\">Apa</phoneme></speak>"
        expect = [
            {'text': 'Jag heter', 'type': 'text'},
            {'text': 'Apa', 'type': 'phonemes', 'phonemes': "' a . p a"}
        ]
        output = textproc_adapter.mapSSMLToTextproc(input)
        assert output == expect

    def testWithXMLNS1(self):
        input = """<speak xml:lang="sv" version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemalocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd">
"All Apologies" hamnade på plats sju över de <sub alias="tjugo">
20</sub>
 mest spelade Nirvana-låtarna någonsin i Storbritannien, vilket var en lista framtagen av Phonographic Performance Limited för att hedra Cobains <sub alias="femtio">
50</sub>-årsdag som <phoneme ph="f'i:.ra.des">
firades</phoneme>
 den <sub alias="tjugonde februari tjugo hundra sjutton">
20 februari 2017</sub>
.</speak>"""
        expect = [
            {'text': '"All Apologies" hamnade på plats sju över de', 'type': 'text'},
            {'text': '20', 'type': 'alias', 'alias': 'tjugo'},
            {'text': 'mest spelade Nirvana-låtarna någonsin i Storbritannien, vilket var en lista framtagen av Phonographic Performance Limited för att hedra Cobains ', 'type': 'text'},
            {'text': '50', 'type': 'alias', 'alias': 'femtio'},
            {'text': '-årsdag som ', 'type': 'text'},
            {'text': 'firades', 'type': 'phonemes', 'phonemes': 'f\'i:.ra.des'},            
            {'text': 'den ', 'type': 'text'},
            {'text': '20 februari 2017', 'type': 'alias', 'alias': 'tjugonde februari tjugo hundra sjutton'},
            {'text': '.', 'type': 'text'}
        ]
        output = textproc_adapter.mapSSMLToTextproc(input)
        assert output == expect

    def testWithXMLNS2(self):
        input = """<speak xml:lang="sv" version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemalocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd">
"All Apologies" hamnade på plats sju över de <sub alias="tjugo">20</sub> mest spelade Nirvana-låtarna någonsin i Storbritannien, vilket var en lista framtagen av Phonographic Performance Limited för att hedra Cobains <sub alias="femtio">50</sub>-årsdag som <phoneme ph="f'i:.ra.des">firades</phoneme> den <sub alias="tjugonde februari tjugo hundra sjutton">20 februari 2017</sub>.</speak>"""
        expect = [
            {'text': '"All Apologies" hamnade på plats sju över de', 'type': 'text'},
            {'text': '20', 'type': 'alias', 'alias': 'tjugo'},
            {'text': 'mest spelade Nirvana-låtarna någonsin i Storbritannien, vilket var en lista framtagen av Phonographic Performance Limited för att hedra Cobains ', 'type': 'text'},
            {'text': '50', 'type': 'alias', 'alias': 'femtio'},
            {'text': '-årsdag som ', 'type': 'text'},
            {'text': 'firades', 'type': 'phonemes', 'phonemes': 'f\'i:.ra.des'},            
            {'text': 'den ', 'type': 'text'},
            {'text': '20 februari 2017', 'type': 'alias', 'alias': 'tjugonde februari tjugo hundra sjutton'},
            {'text': '.', 'type': 'text'}
        ]
        output = textproc_adapter.mapSSMLToTextproc(input)
        assert output == expect

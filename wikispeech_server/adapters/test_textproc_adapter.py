from . import textproc_adapter

class TestSSML:

    def testSubAlias1(self):
        input = "<speak>Jag heter <sub alias=\"Karl den tolfte\">Karl XII</sub></speak>"
        expected = [
            {'text': 'Jag heter', 'type': 'text'},
            {'text': 'Karl XII', 'type': 'alias', 'alias': 'Karl den tolfte'}
        ]
        output = textproc_adapter.mapSSMLToTextproc(input, "sv")
        assert output == expected

    def testPhoneme1(self):
        input = "<speak>Jag heter <phoneme ph=\"' a . p a\">Apa</phoneme></speak>"
        expected = [
            {'text': 'Jag heter', 'type': 'text'},
            {'text': 'Apa', 'type': 'phonemes', 'phonemes': "' a . p a"}
        ]
        output = textproc_adapter.mapSSMLToTextproc(input, "sv")
        assert output == expected


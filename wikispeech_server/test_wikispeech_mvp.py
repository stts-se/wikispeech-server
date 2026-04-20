## This tests a running server, using the config_mvp.env et al. In other words, the Wikispeech server must be started before running these tests.

# pytest test_wikispeech_mvp.py

import pytest
import requests

class TestMVP:

    # First of all, ping the server.
    # ("_aaa_" so that this test appears
    # first if sorted alphabetically)
    def test_aaa_ping_server(self,client, base_url):
        try:
            response = client.get(f"{base_url}/ping", timeout=2)
            assert response.text == "wikispeech"
        except requests.exceptions.ConnectionError:
            pytest.exit(f"Server not reachable at {base_url}/ping, is it running?")
        except requests.exceptions.Timeout:
            pytest.exit(f"Server did not respond within 2 seconds")

    # Test that a few calls return 200, etc


    def test_root(self,client, base_url):
        response = client.get(f"{base_url}/")
        assert response.status_code == 200

    def test_list_voices(self,client, base_url):
        response = client.get(f"{base_url}/synthesis/voices")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        frst = data[0]
        assert "adapter" in frst
        assert "name" in frst

    def test_list_textprocs(self,client, base_url):
        response = client.get(f"{base_url}/textprocessing/textprocessors")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        frst = data[0]
        assert "components" in frst

    def test_list_lexicons(self,client, base_url):    
        response = client.get(f"{base_url}/lexserver/lexicon/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        frst = data[0]
        assert "name" in frst


    # Look up "apa" in Braxen
    # http://localhost:10000/lexserver/lexicon/lookup?lexicons=sv_se_braxen_lex%3Asv-se.braxen&words=apa
    def test_list_lexicons(self,client, base_url):    
        response = client.get(f"{base_url}/lexserver/lexicon/lookup?lexicons=sv_se_braxen_lex:sv-se.braxen&words=apa")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        frst = data[0]
        assert "strn" in frst
        assert "transcriptions" in frst
        assert "partOfSpeech" in frst
        assert "lemma" in frst

    # lexicon info http://localhost:10000/lexserver/lexicon/info/sv_se_braxen_lex:sv-se.braxen
    def test_list_lexicons(self,client, base_url):    
        response = client.get(f"{base_url}/lexserver/lexicon/info/sv_se_braxen_lex:sv-se.braxen")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "symbolSetName" in data

    def test_default_voices(self,client, base_url):
        response = client.get(f"{base_url}/default_voices")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        frst = data[0]
        assert (frst["lang"] == "sv" or frst["lang"] == "en") 

    def test_no_such_path_404(self,client, base_url):
        response = client.get(f"{base_url}/gabbatgabbahey")
        assert response.status_code == 404

    def test_invalid_voice_name(self,client, base_url):
        response = client.get(f"{base_url}/?lang=sv&input=Vi%20testar%20matcha%20talsyntes&voice=NO_SUCH_VOICE_EXISTS&input_type=text")
        assert response.status_code == 200
        assert "error" in response.json()
        #assert response.text.lower().startswith("error")


    def test_mapper(self,client, mapper_url):
        response = client.get(f"{mapper_url}/mapper/map/sv-se_ws-sampa/ipa/p%20I%20N%20.%20%22%20v%20i%3A%20n")
        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "from" in data
        assert "to" in data
        assert data["to"] == "ipa"

    # curl 'http://localhost:10000/?lang=sv&input=dessutom&voice=sv_vc_m2f_p'
    # https://github.com/stts-se/wikispeech-server/issues/33
    def test_symbolset_mapping_error_1(self, client, base_url):
        payload = {
            "lang": "sv",
            "voice": "sv_vc_m2f_p",
            "input": "dessutom"
        }
        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]

        
    # https://github.com/stts-se/wikispeech-server/issues/33
    def test_symbolset_mapping_error_2(self, client, base_url):
        payload = {
            "lang": "sv",
            "voice": "sv_vc_m2f_p",
            "input": "graphein"
        }
        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]

        
    def test_en_mixed_case(self,client, base_url):
        payload = {
            "lang": "en",
            "voice": "en_US-bryce-medium",
            "input": "MediaWiki"
        }
        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        #assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        #assert "skip_test" in data["voice"]



    def test_en_year(self,client, base_url):
        payload = {
            "lang": "en",
            "voice": "en_US-bryce-medium",
            "input": "1971"
        }
        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        #assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        #assert "skip_test" in data["voice"]




    # lang and voice    
    def test_sv_vc_m2m_p(self,client, base_url):
        response = client.get(f"{base_url}/?lang=sv&input=Ett+test+med+en+manlig+r%C3%B6st&voice=sv_vc_m2m_p")
        assert response.status_code == 200
        assert not response.text.lower().startswith("error"), f"Server returned error: {response.text}"
        data = response.json()
        assert "audio" in data
        assert "audio_data" in data
        assert "tokens" in data
        assert len(data["tokens"]) > 5
        assert len(data["tokens"]) < 10
        # Timestamps change for each run, but they should increase
        t1 = data["tokens"][0]["endtime"]
        t2 = data["tokens"][1]["endtime"]
        assert t1 < t2
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        assert "skip_test" in data["voice"]


    # lang and voice   
    def test_sv_vc_m2f_p(self,client, base_url):
        response = client.get(f"{base_url}/?lang=sv&input=Ett+test+med+en+kvinnlig+r%C3%B6st&voice=sv_vc_m2f_p")
        assert response.status_code == 200
        assert not response.text.lower().startswith("error"), f"Server returned error: {response.text}"
        data = response.json()
        assert "audio" in data
        assert "audio_data" in data
        assert "tokens" in data
        assert len(data["tokens"]) > 5
        assert len(data["tokens"]) < 10
        # Timestamps change for each run, but they should increase
        t1 = data["tokens"][0]["endtime"]
        t2 = data["tokens"][1]["endtime"]
        assert t1 < t2
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        assert "skip_test" in data["voice"]



    #lang and IPA and default voice ?lang=sv&input=ˈhɛj&input_type=ipa
    def test_lang_IPA_default_voice(self,client, base_url):
        response = client.get(f"{base_url}/?lang=sv&input=ˈhɛj&input_type=ipa")
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        assert "skip_test" in data["voice"]


    # Same as above, but with voice specified
    def test_lang_IPA_voice(self,client, base_url):
        response = client.get(f"{base_url}?lang=sv&voice=sv_vc_m2m_p&input=ˈɑ̀ː.pa&input_type=ipa")
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        assert "skip_test" in data["voice"]


    # POSTing JSON request to the root URL, must be "data"  
    def test_post_synthesis(self,client, base_url):
        payload = {
            "lang": "en",
            "input": "test."
        }
        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        #assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        #assert "skip_test" in data["voice"]


    def test_post_synthesis_sv(self,client, base_url):
        payload = {
            "lang": "sv",
            "input": "en häst betar.",
            "voice": "sv_vc_m2m_p"
        }
        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        assert "skip_test" in data["voice"]


    def test_post_synthesis_sv_textproc(self,client, base_url):
        payload = {
            "lang": "sv",
            "input": "Jag heter Karl XII",
            "voice": "sv_vc_m2m_p"
        }
        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200
        data = response.json()
        assert "audio" in data
        assert len(data["audio_data"]) > 1000
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        assert "mapper" in data["voice"]
        assert "name" in data["voice"]
        assert "skip_test" in data["voice"]
        # Test sv textproc
        assert "tokens" in data
        xii = data["tokens"][2] #jag heter Karl XII <- [3]
        assert xii["orth"] == "Karl XII"
        assert xii["expanded"] == "Karl den tolfte"

    def test_SSML_1(self,client, base_url):
        ssml = """<speak xml:lang="sv" version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemalocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd">
        Det här är en enkel text utan uppmärkning. 
    </speak>"""
        payload = {"lang": "sv",
                   "input": ssml,
                   "input_type": "ssml",
                   "voice": "sv_vc_m2m_p"}

        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200


    def test_SSML_1b(self,client, base_url):
        ssml = """<speak xml:lang="sv" version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemalocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd">
        " Det här är en enkel text som börjar med citattecken. 
    </speak>"""
        payload = {"lang": "sv",
                   "input": ssml,
                   "input_type": "ssml",
                   "voice": "sv_vc_m2m_p"}

        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200



    #@pytest.mark.skip(reason="working on it")    
    def test_SSML_2(self,client, base_url):
        ssml = """<speak xml:lang="sv" version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemalocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd">
    "<phoneme ph="&quot; o: l">All</phoneme> Apologies" hamnade på plats sju över de <sub alias="tjugo">
    20</sub>
     mest spelade Nirvana-låtarna någonsin i Storbritannien, vilket var en lista framtagen av Phonographic Performance Limited för att hedra Cobains <sub alias="femtio">
    50</sub>-årsdag som <phoneme ph="f &quot;&quot; i: . r a . d e s">
    firades</phoneme>
     den <sub alias="tjugonde februari tjugo hundra sjutton">
    20 februari 2017</sub>
    .</speak>"""
        payload = {"lang": "sv",
                   "input": ssml,
                   "input_type": "ssml",
                   "voice": "sv_vc_m2m_p"}

        response = client.post(f"{base_url}/", data=payload)
        assert response.status_code == 200

    #@pytest.mark.skip(reason="working on it")
    def test_SSML_textproc_1(self,client, base_url):
        ssml = """<speak xml:lang="sv" version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemalocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd">
    "<phoneme ph="&quot; o: l">All</phoneme> Apologies" hamnade på plats sju över de <sub alias="tjugo">
    20</sub>
     mest spelade Nirvana-låtarna.</speak>"""
        payload = {"lang": "sv",
                   "input": ssml,
                   "input_type": "ssml",
                   "voice": "sv_vc_m2m_p"}

        response = client.post(f"{base_url}/textprocessing", data=payload)
        assert response.status_code == 200
        data = response.json()
        tokens_got = data["paragraphs"][0]["sentences"][0]["phrases"][0]["tokens"]
        tokens_exp = [{
            "input_orth": "\"",
            "name": "token0",
            "words": [
                {
                    "orth": "\""
                }
            ]
        },
        {
            "input_orth": "All",
            "mtu": True,
            "name": "token1",
            "words": [
                {
                    "g2p_method": "ssml",
                    "orth": "All",
                    "trans": "\" o: l"
                }
            ]
        },
        {
            "input_orth": "Apologies\"",
            "name": "token2",
            "words": [
                {
                    "orth": "Apologies",
                    "postpunct": "\""
                }
            ]
        },
        {
            "input_orth": "hamnade",
            "name": "token3",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "hamnade",
                    "pos": "VB PRT AKT",
                    "trans": "\"\" h a m . % n a . d @"
                }
            ]
        },
        {
            "input_orth": "p\u00e5",
            "name": "token4",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "p\u00e5",
                    "pos": "AB",
                    "trans": "\" p o:"
                }
            ]
        },
        {
            "input_orth": "plats",
            "name": "token5",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "plats",
                    "pos": "NN UTR SIN IND GEN",
                    "trans": "\" p l a t s"
                }
            ]
        },
        {
            "input_orth": "sju",
            "name": "token6",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "sju",
                    "pos": "RG NOM",
                    "trans": "\" x }:"
                }
            ]
        },
        {
            "input_orth": "\u00f6ver",
            "name": "token7",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "\u00f6ver",
                    "pos": "AB",
                    "trans": "\" 2: . v @ r"
                }
            ]
        },
        {
            "input_orth": "de",
            "name": "token8",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "de",
                    "pos": "DT UTR/NEU PLU DEF",
                    "trans": "\" d O m"
                }
            ]
        },
        {
            "input_orth": "20",
            "name": "token9",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "tjugo",
                    "pos": "RG NOM",
                    "trans": "\"\" C }: . % g U"
                }
            ]
        },
        {
            "input_orth": "mest",
            "name": "token10",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "mest",
                    "pos": "AB",
                    "trans": "\" m e s t"
                }
            ]
        },
        {
            "input_orth": "spelade",
            "name": "token11",
            "words": [
                {
                    "g2p_method": "lexicon",
                    "orth": "spelade",
                    "pos": "PC PRF UTR/NEU PLU IND/DEF NOM",
                    "trans": "\"\" s p e: . % l a . d @"
                }
            ]
        },
        {
            "input_orth": "Nirvana-l\u00e5tarna.",
            "name": "token12",
            "words": [
                {
                    "orth": "Nirvana-l\u00e5tarna",
                    "postpunct": "."
                }
            ]
        }
        ]
        assert tokens_got == tokens_exp

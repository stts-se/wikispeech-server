## This tests a running server, using the config_mvp.env et al. In other words, the Wikispeech server must be started before running these tests.

# pytest test_wikispeech_mvp.py

import pytest
import requests

# First of all, ping the server.
# ("_aaa_" so that this test appears
# first if sorted alphabetically)
def test_aaa_ping_server(client, base_url):
    try:
        response = client.get(f"{base_url}/ping", timeout=2)
        assert response.text == "wikispeech"
    except requests.exceptions.ConnectionError:
        pytest.exit(f"Server not reachable at {base_url}/ping, is it running?")
    except requests.exceptions.Timeout:
        pytest.exit(f"Server did not respond within 2 seconds")

# Test that a few calls return 200, etc

    
def test_root(client, base_url):
    response = client.get(f"{base_url}/")
    assert response.status_code == 200
        
def test_list_voices(client, base_url):
    response = client.get(f"{base_url}/synthesis/voices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    frst = data[0]
    assert "adapter" in frst
    assert "name" in frst

def test_list_textprocs(client, base_url):
    response = client.get(f"{base_url}/textprocessing/textprocessors")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    frst = data[0]
    assert "components" in frst

def test_list_lexicons(client, base_url):    
    response = client.get(f"{base_url}/lexserver/lexicon/list")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    frst = data[0]
    assert "name" in frst

    
# Look up "apa" in Braxen
# http://localhost:10000/lexserver/lexicon/lookup?lexicons=sv_se_braxen_lex%3Asv-se.braxen&words=apa
def test_list_lexicons(client, base_url):    
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
def test_list_lexicons(client, base_url):    
    response = client.get(f"{base_url}/lexserver/lexicon/info/sv_se_braxen_lex:sv-se.braxen")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "symbolSetName" in data

def test_default_voices(client, base_url):
    response = client.get(f"{base_url}/default_voices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    frst = data[0]
    assert (frst["lang"] == "sv" or frst["lang"] == "en") 

def test_no_such_path_404(client, base_url):
    response = client.get(f"{base_url}/gabbatgabbahey")
    assert response.status_code == 404
    
def test_invalid_voice_name(client, base_url):
    response = client.get(f"{base_url}/?lang=sv&input=Vi%20testar%20matcha%20talsyntes&voice=NO_SUCH_VOICE_EXISTS&input_type=text")
    assert response.status_code == 200
    assert response.text.lower().startswith("error")
    
# lang and voice    
def test_sv_vc_male_mart2nik_p(client, base_url):
    response = client.get(f"{base_url}/?lang=sv&input=Ett+test+med+en+manlig+r%C3%B6st&voice=sv_vc_male_mart2nik_p")
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
def test_sv_vc_female_mart2han_p(client, base_url):
    response = client.get(f"{base_url}/?lang=sv&input=Ett+test+med+en+kvinnlig+r%C3%B6st&voice=sv_vc_female_mart2han_p")
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
def test_lang_IPA_deafult_voice(client, base_url):
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
def test_lang_IPA_voice(client, base_url):
    response = client.get(f"{base_url}?lang=sv&voice=sv_vc_male_mart2nik_p&input=ˈɑ̀ː.pa&input_type=ipa")
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

    
# POSTing JSON request to the root URL doesn't currently work with JSON, must be "data"  
def test_post_synthesis(client, base_url):
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


def test_post_synthesis_sv(client, base_url):
    payload = {
        "lang": "sv",
        "input": "en häst betar.",
        "voice": "sv_vc_male_mart2nik_p"
    }
    response = client.post(f"{base_url}/", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "audio" in data
    print("AUDIO", data["audio"])
    assert len(data["audio_data"]) > 1000
    assert "adapter" in data["voice"]
    assert "config_file" in data["voice"]
    assert "engine" in data["voice"]    
    assert "lang" in data["voice"]
    assert "longname" in data["voice"]
    assert "mapper" in data["voice"]
    assert "name" in data["voice"]
    assert "skip_test" in data["voice"]

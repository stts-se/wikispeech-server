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
            
def testNoSuchPath404(client, base_url):
    response = client.get(f"{base_url}/gabbatgabbahey")
    assert response.status_code == 404
    
def test_invalidVoiceName(client, base_url):
    response = client.get(f"{base_url}/?lang=sv&input=Vi%20testar%20matcha%20talsyntes&voice=NO_SUCH_VOICE_EXISTS&input_type=text")
    assert response.status_code == 200
    assert response.text.lower().startswith("error")
    
    
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

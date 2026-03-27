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

# Test that a few calls return 200

    
def test_root(client, base_url):
    response = client.get(f"{base_url}/")
    assert response.status_code == 200
        
def test_list_voices(client, base_url):
    response = client.get(f"{base_url}/synthesis/voices")
    assert response.status_code == 200
            
def testNoSuchPath404(client, base_url):
    response = client.get(f"{base_url}/gabbatgabbahey")
    assert response.status_code == 404
    
def test_sv_se_nst_male1(client, base_url):
    response = client.get(f"{base_url}/?lang=sv&input=Vi%20testar%20matcha%20talsyntes&voice=sv_se_nst_male1&input_type=text")
    assert response.status_code == 200
                
def test_sv_vc_male_mart2nik_p(client, base_url):
    response = client.get(f"{base_url}/?lang=sv&input=Ett+test+med+en+manlig+r%C3%B6st&voice=sv_vc_male_mart2nik_p")
    assert response.status_code == 200

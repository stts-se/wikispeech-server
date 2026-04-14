## This tests a running server, using the config_mvp2.env et al. In other words, the Wikispeech server must be started before running these tests.

import pytest
import requests

class TestAllVoices:

    server_voices = None

    def test_all_voices(self, client, base_url):
        response = client.get(f"{base_url}/synthesis/voices")
        assert response.status_code == 200
        voices = response.json()
        for voice in voices:
            self.exec_single_voice(client, base_url, voice)

    def exec_single_voice(self, client, base_url, voice):
        if self.server_voices is None:
            r = client.get(f"{base_url}/synthesis/voices")
            assert r.status_code == 200
            self.server_voices = r.json()

        voice_exists = False
        for sv in self.server_voices:
            if sv["name"] == voice["name"]:
                voice_exists = True
        if not voice_exists:
            pytest.xfail(f"Couldn't find voice {voice} in server voices")
            
        lang = voice["lang"]
        voice_name = voice["name"]        
        text = "ciao bello amore mio"
        url = f"{base_url}/?lang={lang}&input={text}&voice={voice_name}"
        print(f"Testing {url}")
        response = client.get(url)
        assert response.status_code == 200, f"Server returned: {response} for {url}"
        assert not response.text.lower().startswith("error"), f"Server returned error: {response.text}"
        data = response.json()
        assert "audio" in data
        assert "audio_data" in data
        assert "tokens" in data
        assert len(data["tokens"]) > 3
        assert len(data["tokens"]) < 6
        # Timestamps change for each run, but they should increase
        t1 = data["tokens"][0]["endtime"]
        t2 = data["tokens"][1]["endtime"]
        assert t1 < t2
        assert "adapter" in data["voice"]
        assert "config_file" in data["voice"]
        assert "engine" in data["voice"]    
        assert "lang" in data["voice"]
        assert "longname" in data["voice"]
        if data["voice"]["engine"] in ["piper","matcha"] and lang == "sv":
            assert "mapper" in data["voice"]
        assert "name" in data["voice"]

## This tests a running server, using the config_mvp2.env et al. In other words, the Wikispeech server must be started before running these tests.

# pytest stresstest_article_text_mvp2_piper.py

import pytest
import requests

class TestArticleTextsMVP2Piper:
    def test_aaa_ping_server(self,client, base_url):
        try:
            response = client.get(f"{base_url}/ping", timeout=2)
            assert response.text == "wikispeech"
        except requests.exceptions.ConnectionError:
            pytest.exit(f"Server not reachable at {base_url}/ping, is it running?")
        except requests.exceptions.Timeout:
            pytest.exit(f"Server did not respond within 2 seconds")

    def run_article(self, client, base_url, data_dir, lang, voice, article_filename):
        with open(data_dir / article_filename) as f:
            lines = [line.rstrip() for line in f if line.strip() and not line.startswith("#")]
            assert len(lines) > 2
            for i, l in enumerate(lines):
                id = '{:0>3}'.format(i)
                payload = {
                    "lang": lang,
                    "voice": voice,
                    "input": l
                }
                response = client.post(f"{base_url}/", data=payload)
                assert response.status_code == 200
                data = response.json()
                assert "audio" in data
                assert len(data["audio_data"]) > 1000
                print(id, data["audio"], l)
            
    def test_medeltidens_mat(self, client, base_url, data_dir):
        self.run_article(client, base_url, data_dir, "sv", "sv_vc_m2f_p", "article_text_sv_medeltidens_mat.txt")

    def test_nevermind(self, client, base_url, data_dir):
        self.run_article(client, base_url, data_dir, "sv", "sv_vc_m2f_p", "article_text_sv_nevermind.txt")

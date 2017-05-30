if __name__ == "__main__":
    import sys
    sys.path.append(sys.path[0]+"/..")

import unittest
try:
    from wikispeech_server.voice import *
except:
    from voice import *

import wikispeech_server.log as log


    
class TestVoice(unittest.TestCase):

    def testNewVoice(self):
        voice_config = {
            "lang":"sv",
            "name":"stts_sv_nst-hsmm",
            "engine":"marytts",
            "adapter":"adapters.marytts_adapter",
            "mapper": {
                "from":"sv-se_ws-sampa",
                "to":"sv-se_sampa_mary"
            }
        }

        v = Voice(voice_config)

        self.assertEqual(v.name, voice_config["name"])
        self.assertEqual(v.engine, voice_config["engine"])
        self.assertEqual(str(type(v.mapper)), "<class 'wikispeech_server.adapters.mapper_client.Mapper'>")

    def testBrokenVoice(self):
        default_log_level = log.log_level
        log.log_level = "fatal"
        voice_config = {
            "lang":"sv",
            "name":"stts_sv_nst-hsmmXXXX",
            "engine":"marytts",
            "adapter":"adapters.marytts_adapter",
            "mapper": {
                "from":"sv-se_ws-sampa",
                "to":"sv-se_sampa_mary"
            }
        }
        with self.assertRaises(VoiceException):
            v = Voice(voice_config)
        log.log_level = default_log_level

    def testBrokenMapper(self):
        default_log_level = log.log_level
        log.log_level = "fatal"
        voice_config = {
            "lang":"sv",
            "name":"stts_sv_nst-hsmm",
            "engine":"marytts",
            "adapter":"adapters.marytts_adapter",
            "mapper": {
                "from":"sv-se_ws-sampa",
                "to":"sv-se_sampa_maryXXXX"
            }
        }
        with self.assertRaises(VoiceException):
            v = Voice(voice_config)
        log.log_level = default_log_level


    
if __name__ == "__main__":
    log.log_level = "error" #debug, info, warning, error
    unittest.main()

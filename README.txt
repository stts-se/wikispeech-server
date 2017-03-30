server for wikispeech tts.


Install:
sudo python3 setup.py install

or, without sudo, for example

mkdir ~/python3
export PYTHONPATH=~/python3/lib/python
export PATH=$PATH:~/python3/bin
python3 setup.py install --home=~/python3/



Usage:
wikispeech
or
python3 wikispeech_mockup/wikispeech.py



Configuration:

For local configuration, make a copy of wikispeech_mockup/user-host_example.conf,
name it <username>-<hostname>.conf, and edit it as needed.

The usage examples will both test that the configuration is correct, and that a lexicon server and a marytts server are accessible.

Test:
python3 test/test_api.py
(tests that the api calls return what is expected)

python3 test/test_voice_configs.py
(tests voice/server configurations)

chromium-browser test.html
(may not work to load the audio, depends on setup)



Documentation:

started in https://github.com/stts-se/wikispeech_mockup/wiki


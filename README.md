# wikispeech_mockup

Initial tests of wikispeech api. 



Prerequisites:

sudo apt-get install python-flask

sudo pip3 install flask-cors




Marytts server:

If Arabic is included, first start mishkal vocalisation service.

cd ../mishkal/; python interfaces/web/mishkal-webserver.py

cd ../marytts; sh target/marytts-5.2-SNAPSHOT/bin/marytts-server

Lexicon server: 

cd $GOPATH/src/github.com/stts-se/pronlex/lexserver; go run lexserver.go

Wikispeech server:

This will test that lexicon and marytts servers are up.

python3 wikispeech.py



Test:

python3 test/test_api.py

python3 test/test_voice_configs.py

chromium-browser test.html 



Documentation:

started in https://github.com/stts-se/wikispeech_mockup/wiki


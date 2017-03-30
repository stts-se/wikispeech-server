import configparser
import getpass
user = getpass.getuser()


config = configparser.SafeConfigParser()
config.read("/home/harald/git/wikispeech_mockup/wikispeech_mockup/default.conf")
config.read("%s.conf" % user)

import configparser
import sys, getpass, os, os.path

home = os.path.expanduser("~")
user = getpass.getuser()
hostname = os.uname()[1]


config = configparser.SafeConfigParser()

#default_config_file = "%s/git/wikispeech_mockup/wikispeech_mockup/default.conf" % home
default_config_file = "wikispeech_mockup/default.conf"
print("Default config file: %s" % default_config_file)
config.read(default_config_file)

#user_config_file = "%s/git/wikispeech_mockup/wikispeech_mockup/%s-%s.conf" % (home,user, hostname)
user_config_file = "wikispeech_mockup/%s-%s.conf" % (user, hostname)
print("User config file: %s" % user_config_file)

config.read(user_config_file)

print("Testing config: Services|lexicon = %s" % config.get("Services", "lexicon"))

sys.exit()

import configparser
import sys, getpass, os, os.path

config = configparser.SafeConfigParser()

print("\nCONFIG\n\nChecking for default and user config files..")

user = getpass.getuser()
hostname = os.uname()[1]



default_config_file = "wikispeech_server/default.conf"
    
if not os.path.isfile(default_config_file):
    print("ERROR: Default config file %s not found" % default_config_file)
    sys.exit(1)

#print("Default config file found: %s" % default_config_file)
config.read(default_config_file)

user_config_file = "wikispeech_server/%s-%s.conf" % (user, hostname)
if not os.path.isfile(user_config_file):
    print("User config file %s not found, using default config file %s" % (user_config_file, default_config_file))
else:
    print("User config file found: %s" % user_config_file)
    config.read(user_config_file)

print("Edit user config file %s if needed\n\nEND CONFIG\n" % user_config_file)





try:
    from setuptools import setup
except:
    print("setuptools was not found. You should probably run something like\nsudo apt-get install python3-setuptools")
    import sys
    sys.exit(1)
    

setup(name='wikispeech-server',
      version='0.1',
      description='Server for wikispeech tts',
      url='https://github.com/stts-se/wikispeech-server',
      author='Harald Berthelsen',
      author_email='haraldberthelsen@gmail.com',
      license='MIT',
      packages=[
          'wikispeech-server',
          'wikispeech-server.adapters'
      ],
      install_requires=[
          'requests',
          'flask',
          'flask_cors'
      ],
      scripts=['bin/wikispeech'],
      include_package_data=True,
      zip_safe=False)


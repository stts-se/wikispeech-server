from setuptools import setup

setup(name='wikispeech_mockup',
      version='0.1',
      description='Server for wikispeech tts',
      url='https://github.com/HaraldBerthelsen/wikispeech_mockup',
      author='Harald Berthelsen',
      author_email='haraldberthelsen@gmail.com',
      license='MIT',
      packages=['wikispeech_mockup'],
      install_requires=[
          'requests',
          'flask',
          'flask_cors',
      ],
      scripts=['bin/wikispeech_server'],
      zip_safe=False)

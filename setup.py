#from setuptools import setup
from distutils.core import setup

#for distutils
setup(name='wikispeech_mockup',
      version='0.1',
      description='Server for wikispeech tts',
      url='https://github.com/HaraldBerthelsen/wikispeech_mockup',
      author='Harald Berthelsen',
      author_email='haraldberthelsen@gmail.com',
      license='MIT',
      packages=[
          'wikispeech_mockup',
          'wikispeech_mockup.adapters',
      ],
      requires=[
          'requests',
          'flask',
          'flask_cors',
      ],
      scripts=['bin/wikispeech_server', 'bin/wikispeech']
#      include_package_data=True,
#      zip_safe=False
)

# for setuptools
# setup(name='wikispeech_mockup',
#       version='0.1',
#       description='Server for wikispeech tts',
#       url='https://github.com/HaraldBerthelsen/wikispeech_mockup',
#       author='Harald Berthelsen',
#       author_email='haraldberthelsen@gmail.com',
#       license='MIT',
#       packages=[
#           'wikispeech_mockup',
#           'wikispeech_mockup.adapters',
#       ],
#       install_requires=[
#           'requests',
#           'flask',
#           'flask_cors',
#       ],
#       scripts=['bin/wikispeech_server', 'bin/wikispeech'],
#       include_package_data=True,
#       zip_safe=False)


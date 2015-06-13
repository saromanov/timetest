from distutils.core import setup
import sys

sys.path.append('timetest')


def requirements(filename):
    with open(filename) as f:
        return [x.strip() for x in f.readlines() if x.strip()]

setup(name='timetest',
      version='0.1',
      author='Sergey Romanov',
      author_email='xxsmotur@gmail.com',
      url='https://github.com/saromanov/timetest',
      download_url='https://github.com/saromanov/timetest/',
      description='Time tests for code',
      #long_description=timetest.__doc__,
      package_dir={'': 'timetest'},
      py_modules=['timetest'],
      provides=['timtest'],
      keywords='time test',
      license='MIT',
      classifiers=['Development Status :: 1 - Planning',
                   'Intended Audience :: Developers',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Testing',
                  ],
      install_requires=requirements('requirements.txt'),
     )

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


required = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    'sqlalchemy',
    'requests',
]

extras = {
    'test': [
        'mock',
        'webtest',
    ]
}

long_description= read('README.md') + '\n' + read('CHANGELOG')

setup(
    name='detectoid',
    version=read('version.txt').strip(),
    description="Detectoid, a simple website to guess whether a Twitch stream has viewbots",
    long_description=long_description,
    author="Benjamin Maisonnas",
    author_email="ben@wainei.net",
    url="https://github.com/Benzhaomin/detectoid.git",
    license = 'GPLv3',
    packages=[
        'detectoid',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=required,
    extras_require=extras,
    test_suite="detectoid.tests",
    entry_points="""\
    [paste.app_factory]
    main = detectoid:main
    """,
      )

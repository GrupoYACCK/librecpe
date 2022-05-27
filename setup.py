import os
from setuptools import setup

README_PATH = 'README.rst'
LONG_DESC = ''
if os.path.exists(README_PATH):
    with open(README_PATH) as readme:
        LONG_DESC = readme.read()

INSTALL_REQUIRES = ['lxml','xmlsec','pysimplesoap']
PACKAGE_NAME = 'librecpe'
PACKAGE_DIR = 'src'

setup(
    name=PACKAGE_NAME,
    version='0.0.20',
    author='Alex Cuellar',
    author_email='acuellar@grupoyacck.com',
    maintainer='Alex Cuellar',
    maintainer_email='acuellar@grupoyacck.com',
    description=(
        "Libre CPE"
    ),
    long_description=LONG_DESC,
    license='GPLv3',
    keywords='librecpe',
    url='',
    packages=[PACKAGE_NAME,"%s.common"%PACKAGE_NAME,
              "%s.cpe"%PACKAGE_NAME, "%s.nubefact"%PACKAGE_NAME],
    package_dir={PACKAGE_NAME: PACKAGE_DIR},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': ['{0} = {0}.{0}:main'.format(PACKAGE_NAME)]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)

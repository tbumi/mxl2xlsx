from setuptools import setup, find_packages

setup(
    name='mxl2xlsx',

    version='0.1.0',

    description='A tool to convert MusicXML files to Excel partitur',

    # The project's main homepage.
    url='https://bitbucket.org/traphole/mxl2xlsx',

    # Author details
    author='Trapsilo Bumi',
    author_email='tbumi@thpd.io',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='musicxml partitur angklung excel',

    package_dir={'': 'src'},
    packages=find_packages(where='src', exclude=['docs', 'tests']),

    entry_points={
        'console_scripts': [
            'mxl2xlsx=mxl2xlsx:main',
        ],
    },
)
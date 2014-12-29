from setuptools import setup 


with open('README.md') as f:
    long_description = f.read()

setup(
    name = "moderate",
    version = "0.1",
    license = 'MIT',
    description = "A Python Distrubted System",
    author = 'Thomas Huang',
    url = 'https://github.com/thomashuang/Moderate',
    packages = ['moderate', 'moderate.queue'],

    install_requires = ['setuptools',
                        ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: Distrubted System',
        ],
    long_description=long_description,
)
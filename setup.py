import os
import shutil

import setuptools

import guetzlidir

if not os.path.exists('guetzlidir'):
    os.mkdir('guetzlidir')
shutil.copyfile('guetzlidir.py', 'guetzlidir/__init__.py')

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    'pyguetzli>=1.0.8',
    'Pillow>=8.0.1',
    'tinify>=1.5.1',
    'git+https://github.com/kraken-io/kraken-python'
]

setuptools.setup(
    name="guetzlidir",  # Replace with your own username
    version=guetzlidir.__version__,
    author="Evgeny Varnavskiy",
    author_email="varnavruz@gmail.com",
    description="Will recursively process image files in source directory, optimizing them with Guetzli and writing "
                "to output directory.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varnav/guetzlidir",
    keywords=["jpeg", "filesystem", "filetime"],
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Utilities",
        "Topic :: Multimedia :: Graphics",
        "Environment :: Console",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "guetzlidir = guetzlidir.__init__:main",
        ]
    }
)

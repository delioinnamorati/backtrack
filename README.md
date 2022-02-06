   __author__ = "Delio Innamorati"

with open("README.md", "r", encoding="utf-8") as f:
    README = f.read()

with open("requirements.txt", "r") as f:
    # stripping out the index urls
    INSTALL_REQUIRES = [
        req_line for req_line in f.read().splitlines() if not req_line.startswith("--")
    ]

setuptools.setup(
    name="backtrack",
    version="0.1",
    author=__author__,
    author_email="",
    description="Backtrack: Back up your network devices fast and efficiently!",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    extras_require={},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
)
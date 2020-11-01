import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rdv", 
    version="0.0.2-dev5",
    author="Raymon.ai",
    author_email="dev@raymon.ai",
    description="Raymon Data Validation Package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://raymon.ai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    install_requires=[
        "inquirer>=2.7.0"
        "click",
        "selenium",
        "dash",
        "numpy",
        "imagehash",
        "plotly"
    ],
    # entry_points='''
    #     [console_scripts]
    #     rdv=raymon.cli.rayctl:cli
    # ''',
)

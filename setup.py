import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()


setuptools.setup(
    name='quickforex',
    version="0.0.2",
    description="Simple foreign exchange rates retrieval API",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Jean-Edouard Boulanger",
    url="https://github.com/jean-edouard-boulanger/quickforex",
    author_email="jean.edouard.boulanger@gmail.com",
    license="MIT",
    packages=["quickforex", "quickforex.backends"],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        "requests",
    ]
)

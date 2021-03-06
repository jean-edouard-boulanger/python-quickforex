import pathlib
import setuptools
import re

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
VERSION_REGEX = re.compile(r'__version__\s+=\s+["\'](\d+\.\d+\.\d+)["\']')
PACKAGE_NAME = "quickforex"


def parse_package_version():
    package_file_path = HERE.joinpath(PACKAGE_NAME, "__init__.py")
    with package_file_path.open() as f:
        candidates = [
            line.strip() for line in f.readlines() if VERSION_REGEX.match(line)
        ]
        if len(candidates) != 1:
            raise RuntimeError(
                f"did not find __version__ defined in {package_file_path}."
                f" Hint: is '__version__ = \"<major>.<minor>.<patch>\"' present in this file?"
            )
        return VERSION_REGEX.match(candidates[0])[1]


setuptools.setup(
    name=PACKAGE_NAME,
    version=parse_package_version(),
    description="Simple foreign exchange rates retrieval API",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Jean-Edouard Boulanger",
    url="https://github.com/jean-edouard-boulanger/quickforex",
    author_email="jean.edouard.boulanger@gmail.com",
    license="MIT",
    packages=["quickforex", "quickforex.providers"],
    entry_points={"console_scripts": ["quickforex=quickforex.command_line:main"]},
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
    ],
)

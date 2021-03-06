from setuptools import find_packages, setup

PACKAGE_VERSION = "1.1.1"
PACKAGE_NAME = "spotify-cli"

if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        author="Adrien Kühn",
        description="Spotify command line tool",
        packages=find_packages(),
        python_requires=">=3.7",
        install_requires=[
            "click==7.1.2",
            "coloredlogs==14.0",
            "spotipy==2.13.0"
        ],
        entry_points={"console_scripts": ["spotify-cli=spotify:main"]}
    )

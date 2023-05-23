from setuptools import find_packages, setup

PACKAGE_VERSION = "0.0.12"
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
            "requests==2.31.0",
            "spotipy==2.22.1"
        ],
        entry_points={"console_scripts": ["spotify-cli=spotify:main"]}
    )

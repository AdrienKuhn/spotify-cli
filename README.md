# spotify-cli

[![CircleCI](https://circleci.com/gh/AdrienKuhn/spotify-cli/tree/main.svg?style=shield)](https://circleci.com/gh/AdrienKuhn/spotify-cli/tree/main)

This CLI allows:
* to you sync your followed artists with your current saved tracks (Spotify doesn't automatically follow artists when saving tracks)
* to import a CSV file into a playlist

## Requirements
* Python >=3.7
* a [Spotify for Developers](https://developer.spotify.com/) application

## Usage

### Docker images

Multi-arch docker images are available on [Docker Hub](https://hub.docker.com/r/krewh/spotify-cli):

* The `latest` tag is built from the main branch.  
* The `latest` tag and the last release tag are refreshed nightly to get the latest security updates.

```bash
export SPOTIPY_CLIENT_ID=
export SPOTIPY_CLIENT_SECRET=

docker run \
  -e SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID \
  -e SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET \
  -e SPOTIPY_REDIRECT_URI=http://localhost:8000 \
  krewh/spotify-cli spotify-cli
```

## Examples

### Follow artists from liked tracks

```bash
spotify-cli artists follow liked-tracks-artists --help
Usage: spotify-cli artists follow liked-tracks-artists [OPTIONS]

  Follow artists from all liked tracks

Options:
  --batch-size INTEGER RANGE
  --all-artists               If set, will process liked tracks secondary
                              artists

  --commit                    Use this flag to commit changes.
  --help                      Show this message and exit
```

### Unfollow orphans artists

Unfollow artists without liked tracks in library

```bash
spotify-cli artists follow orphan-artists --help
Usage: spotify-cli artists follow orphan-artists [OPTIONS]

  Unfollow orphan artists

Options:
  --batch-size INTEGER RANGE
  --all-artists               If set, will process liked tracks secondary
                              artists

  --commit                    Use this flag to commit changes.
  --help                      Show this message and exit.
```

### Import CSV file into a playlist

CSV should have the following syntax:

```
title,artist,album,year,rating
"Carolina Low","The Decemberists","What a Terrible World, What a Beautiful World",2015,10
```

Only `title` and `artist` are mandatory.

```bash
spotify-cli playlists sync csv-file --help
Usage: spotify-cli playlists sync csv-file [OPTIONS]

  Import music from CSV to playlist

Options:
  --batch-size INTEGER RANGE
  --file PATH
  --playlist TEXT             Spotify playlist id  [required]
  --commit                    Use this flag to commit changes.
  --help                      Show this message and exit.
```

## Kubernetes CronJobs

See [k8s](./k8s).

## Development

In a virtual environment, follow installation instructions but use the `--editable` flag with `pip`:

```bash
pip install --editable .

export SPOTIPY_CLIENT_ID=
export SPOTIPY_CLIENT_SECRET=
export SPOTIPY_REDIRECT_URI=http://localhost:8000

spotify-cli --help
Usage: spotify-cli [OPTIONS] COMMAND [ARGS]...

Options:
  --level [CRITICAL|ERROR|WARNING|INFO|DEBUG]
                                  Verbose level
  --help                          Show this message and exit.

Commands:
  artists    Use this command to manage artists
  playlists  Use this command to manage playlists
```

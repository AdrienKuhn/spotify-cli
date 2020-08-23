# spotify-cli

Spotify doesn't automatically follow artists when saving tracks.  
This CLI allows to you sync your followed artists with your current saved tracks.

## Requirements
* Python >=3.7
* a [Spotify for Developers](https://developer.spotify.com/) application

## Installation

```bash
pip install .

export SPOTIPY_CLIENT_ID=
export SPOTIPY_CLIENT_SECRET=

spotify-cli --help
Usage: spotify-cli [OPTIONS] COMMAND [ARGS]...

Options:
  --level [CRITICAL|ERROR|WARNING|INFO|DEBUG]
                                  Verbose level
  --help                          Show this message and exit.

Commands:
  artists  Use this command to manage artists
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

  --commit                    Use this flag to actually follow artists.
  --help                      Show this message and exit
```

### Unfollow orphans artists

Unfollow artists without liked tracks in library

```bash
Usage: spotify-cli artists follow orphan-artists [OPTIONS]

  Unfollow orphan artists

Options:
  --batch-size INTEGER RANGE
  --all-artists               If set, will process liked tracks secondary
                              artists

  --commit                    Use this flag to actually unfollow artists.
  --help                      Show this message and exit.
```

## Development

Follow installation instructions but use the `--editable` flag with `pip`:

```bash
pip install --editable .
```

# spotify-cli

## Installation

```bash
pip install --editable .

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
  --all-artists               If true, will process liked tracks secondary
                              artists

  --commit                    Use this flag to actually follow artists.
  --help                      Show this message and exit
```

### List orphans artists

List followed artists without liked tracks in library

```bash
spotify-cli artists follow orphan-artists --help
Usage: spotify-cli artists follow orphan-artists [OPTIONS]

  List orphan artists

Options:
  --batch-size INTEGER RANGE
  --all-artists               If true, will process liked tracks secondary
                              artists

  --help                      Show this message and exit.
```

import click
import spotipy
import logging
from spotipy.oauth2 import SpotifyOAuth
scope = "user-library-read,user-follow-modify"
redirect_uri = "http://localhost:8000/callback"
cache_path = "cache"


@click.group()
def follow():
    """
    Follow artists
    """
    pass


@follow.command("liked-tracks")
@click.option('--batch-size', type=click.IntRange(1, 50), default=50)
@click.option('--commit', is_flag=True, default=False, help="Use this flag to actually follow artists.")
def liked_tracks(batch_size, commit):
    """Follow artists from all liked tracks"""
    try:
        logging.info("Starting Spotify API OAuth flow")
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=scope,
            redirect_uri=redirect_uri,
            show_dialog=True,
            cache_path=cache_path))

        logging.info(f"Batch size is set to {batch_size}")

        # Fetch liked tracks
        results = _fetch_liked_tracks(sp, batch_size)

        # Extract artists
        artists = _extract_unique_artists(results)

        # Follow liked tracks artists
        _follow_artists(sp, artists, batch_size, commit)

        logging.info("Done!")

    except Exception as err:
        print("Exception : %s\n" % err)
        raise click.Abort()


def _fetch_liked_tracks(sp, batch_size):
    results = sp.current_user_saved_tracks(limit=batch_size)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        logging.info(f"Fetched {results['offset']}/{results['total']} tracks... ")
        tracks.extend(results['items'])
    logging.info(f"Fetched {results['total']} tracks")

    return tracks


def _extract_unique_artists(tracks):
    artists = []
    for idx, item in enumerate(tracks):
        track = item['track']
        logging.info(f"Processing #{idx + 1} {track['name']}- {track['artists'][0]['name']}")

        if track['artists'][0]['id'] not in artists:
            logging.warning(f"Adding {track['artists'][0]['name']} to the list of unique artists to follow")
            artists.append(track['artists'][0]['id'])

    logging.info(f"Found {len(artists)} unique artists")
    return artists


def _follow_artists(sp, artists, batch_size, commit):
    if commit:
        logging.warning(f"Will follow {len(artists)} artists")

        logging.info("Following artists...")
        for i in range(0, len(artists), batch_size):
            if i + batch_size > len(artists):
                limit = len(artists) - i
            else:
                limit = batch_size

            # Follow artists per batch
            batch = artists[i:i + limit]
            sp.user_follow_artists(batch)
            logging.info(f"Followed {i + limit}/{len(artists)} artists...")

    else:
        logging.warning(f"Would have followed {len(artists)} artists. Use --commit flag to proceed.")

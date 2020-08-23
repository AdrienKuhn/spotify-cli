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


@follow.command("liked-tracks-artists")
@click.option('--batch-size', type=click.IntRange(1, 50), default=50)
@click.option('--commit', is_flag=True, default=False, help="Use this flag to actually follow artists.")
def liked_tracks_artists(batch_size, commit):
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
        liked_tracks = _fetch_liked_tracks(sp, batch_size)

        # Fetch followed artists
        followed_artist_ids = _fetch_followed_artists(sp, batch_size)

        # Extract artists to follow
        artist_ids_to_follow = _extract_artists_to_follow(liked_tracks, followed_artist_ids)

        # [[artist for artist in artists if artist not in followed_artists], [artist for artist in followed_artists if artist not in artists]]

        if artist_ids_to_follow:
            # Follow liked tracks artists
            _follow_artists(sp, artist_ids_to_follow, batch_size, commit)

        logging.info("Done!")

    except Exception as err:
        print("Exception : %s\n" % err)
        raise click.Abort()


def _fetch_liked_tracks(sp, batch_size):
    results = sp.current_user_saved_tracks(limit=batch_size)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        logging.info(f"Fetched {results['offset']}/{results['total']} liked tracks... ")
        tracks.extend(results['items'])
    logging.info(f"Fetched {results['total']} tracks")

    return tracks


def _fetch_followed_artists(sp, batch_size):
    results = sp.current_user_followed_artists(limit=batch_size)
    offset = batch_size
    logging.info(f"Fetched {offset}/{results['artists']['total']} artists... ")
    artists = results['artists']['items']
    while results['artists']['next']:
        results = sp.next(results['artists'])
        offset = offset + batch_size if (offset + batch_size) < results['artists']['total'] else results['artists']['total']
        logging.info(f"Fetched {offset}/{results['artists']['total']} followed artists... ")
        artists.extend(results['artists']['items'])
    logging.info(f"Fetched {results['artists']['total']} artists")

    artist_ids = [artist['id'] for artist in artists]

    return artist_ids


def _extract_artists_to_follow(tracks, followed_artist_ids):
    artists_to_follow = []

    for idx, item in enumerate(tracks):
        track = item['track']
        logging.debug(f"Processing #{idx + 1} {track['name']}- {track['artists'][0]['name']}")

        if (
                track['artists'][0]['id'] not in followed_artist_ids
                and track['artists'][0]['id'] not in artists_to_follow
        ):
            logging.info(f"Adding {track['artists'][0]['name']} to the list of artists to follow")
            artists_to_follow.append(track['artists'][0]['id'])

    logging.warning(f"Found {len(artists_to_follow)} new artist{'s' if len(artists_to_follow) > 1 else ''} to follow")
    return artists_to_follow


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
        logging.warning(f"Would have followed {len(artists)} artist{'s' if len(artists) > 1 else ''}. "
                        f"Use --commit flag to proceed.")

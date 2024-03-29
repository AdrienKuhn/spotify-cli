import click
import logging


@click.group()
def follow():
    """
    Follow artists
    """
    pass


@follow.command("liked-tracks-artists")
@click.option('--batch-size', type=click.IntRange(1, 50), default=50)
@click.option('--all-artists', is_flag=True, default=False, help="If set, will process liked tracks secondary artists")
@click.option('--commit', is_flag=True, default=False, help="Use this flag to commit changes.")
@click.pass_obj
def liked_tracks_artists(spotify, batch_size, all_artists, commit):
    """Follow artists from all liked tracks"""
    try:
        api = spotify.api

        logging.info(f"Batch size is set to {batch_size}")

        # Fetch liked tracks
        liked_tracks = _fetch_liked_tracks(api, batch_size)

        # Extract artists from liked tracks
        liked_tracks_artists = _extract_liked_tracks_artists(liked_tracks, all_artists)

        # Fetch followed artists
        followed_artists = _fetch_followed_artists(api, batch_size)

        # Extract artists to follow
        artists_to_follow = _extract_artists_to_follow(liked_tracks_artists, followed_artists)

        if artists_to_follow:
            # Follow liked tracks artists
            _follow_artists(api, artists_to_follow, batch_size, commit)
        else:
            logging.warning(f"No new artist to follow.")

        logging.info("Done!")

    except Exception as err:
        print("Exception : %s\n" % err)
        raise click.Abort()\



@follow.command("orphan-artists")
@click.option('--batch-size', type=click.IntRange(1, 50), default=50)
@click.option('--all-artists', is_flag=True, default=False, help="If set, will process liked tracks secondary artists")
@click.option('--commit', is_flag=True, default=False, help="Use this flag to commit changes.")
@click.pass_obj
def orphan_artists(spotify, batch_size, all_artists, commit):
    """Unfollow orphan artists"""
    try:
        api = spotify.api

        logging.info(f"Batch size is set to {batch_size}")

        # Fetch liked tracks
        liked_tracks = _fetch_liked_tracks(api, batch_size)

        # Extract artists from liked tracks
        liked_tracks_artists = _extract_liked_tracks_artists(liked_tracks, all_artists)

        # Fetch followed artists
        followed_artists = _fetch_followed_artists(api, batch_size)

        # Extract orphan artists
        orphans = _extract_orphan_artists(liked_tracks_artists, followed_artists)

        if orphans:
            _unfollow_artists(api, orphans, batch_size, commit)
        else:
            logging.info(f"No orphan artist found.")

        logging.info("Done!")

    except Exception as err:
        print("Exception : %s\n" % err)
        raise click.Abort()


def _fetch_liked_tracks(api, batch_size):
    results = api.current_user_saved_tracks(limit=batch_size)
    tracks = results['items']
    while results['next']:
        results = api.next(results)
        logging.info(f"Fetched {results['offset']}/{results['total']} liked tracks... ")
        tracks.extend(results['items'])
    logging.info(f"Fetched {results['total']} tracks")

    return tracks


def _fetch_followed_artists(api, batch_size):
    results = api.current_user_followed_artists(limit=batch_size)
    offset = batch_size
    logging.info(f"Fetched {offset}/{results['artists']['total']} artists... ")
    artists = results['artists']['items']
    while results['artists']['next']:
        results = api.next(results['artists'])
        offset = offset + batch_size if (offset + batch_size) < results['artists']['total'] else results['artists']['total']
        logging.info(f"Fetched {offset}/{results['artists']['total']} followed artists... ")
        artists.extend(results['artists']['items'])
    logging.info(f"Fetched {results['artists']['total']} artists")

    return artists


def _extract_artists_to_follow(liked_tracks_artists, followed_artists):
    followed_artist_ids = [artist['id'] for artist in followed_artists]
    artists_to_follow = [artist for artist in liked_tracks_artists if artist['id'] not in followed_artist_ids]
    return artists_to_follow


def _extract_liked_tracks_artists(liked_tracks, all_artists=False):
    liked_tracks_artists = []
    for liked_track in liked_tracks:
        if all_artists:
            for artist in liked_track['track']['artists']:
                if artist not in liked_tracks_artists:
                    liked_tracks_artists.append(artist)
        else:
            artist = liked_track['track']['artists'][0]
            if artist not in liked_tracks_artists:
                liked_tracks_artists.append(artist)
    return liked_tracks_artists


def _extract_orphan_artists(liked_tracks_artists, followed_artists):
    liked_tracks_artists_ids = [artist['id'] for artist in liked_tracks_artists]
    orphans = [artist for artist in followed_artists if artist['id'] not in liked_tracks_artists_ids]
    return orphans


def _follow_artists(api, artists, batch_size, commit):
    if commit:
        logging.warning(f"Will follow {len(artists)} artists")

        logging.info("Following artists...")
        artist_ids_to_follow = [artist['id'] for artist in artists]
        for i in range(0, len(artist_ids_to_follow), batch_size):
            if i + batch_size > len(artist_ids_to_follow):
                limit = len(artist_ids_to_follow) - i
            else:
                limit = batch_size

            # Follow artists per batch
            batch = artist_ids_to_follow[i:i + limit]
            api.user_follow_artists(batch)
            logging.info(f"Followed {i + limit}/{len(artist_ids_to_follow)} artists...")

    else:
        logging.warning(f"Would have followed {len(artists)} artist{'s' if len(artists) > 1 else ''}:")
        [logging.warning(f"- {artist['name']}") for artist in artists]
        logging.warning(f"Use --commit flag to proceed.")


def _unfollow_artists(api, artists, batch_size, commit):
    if commit:
        logging.warning(f"Will unfollow {len(artists)} artists")

        logging.info("Unfollowing artists...")
        artist_ids_to_unfollow = [artist['id'] for artist in artists]
        for i in range(0, len(artist_ids_to_unfollow), batch_size):
            if i + batch_size > len(artist_ids_to_unfollow):
                limit = len(artist_ids_to_unfollow) - i
            else:
                limit = batch_size

            # Unfollow artists per batch
            batch = artist_ids_to_unfollow[i:i + limit]
            api.user_unfollow_artists(batch)
            logging.info(f"Unfollowed {i + limit}/{len(artist_ids_to_unfollow)} artists...")

    else:
        logging.warning(f"Would have followed {len(artists)} artist{'s' if len(artists) > 1 else ''}:")
        [logging.warning(f"- {artist['name']}") for artist in artists]
        logging.warning(f"Use --commit flag to proceed.")

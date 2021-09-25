import click
import csv
import os
import re
import requests
import logging


@click.group()
def sync():
    """
    Use this command to sync data into playlists
    """
    pass


@sync.command("csv-file")
@click.option('--batch-size', type=click.IntRange(1, 50), default=50)
@click.option('--file', type=click.Path(exists=True))
@click.option('--playlist', required=True, help="Spotify playlist id")
@click.option('--commit', is_flag=True, default=False, help="Use this flag to commit changes.")
@click.pass_obj
def csv_file(spotify, batch_size, file, playlist, commit):
    """Import music from CSV to playlist"""
    try:
        api = spotify.api
        _process_csv(api, file, playlist, batch_size, commit)
        logging.info("Done!")

    except Exception as err:
        print("Exception : %s\n" % err)
        raise click.Abort()


@sync.command("rp")
@click.option('--batch-size', type=click.IntRange(1, 50), default=50)
@click.option('--rp-user-id', required=True, help="Radio Paradise user ID")
@click.option('--lower-limit', type=click.IntRange(1, 10), default=7, help="Radio Paradise rating lower limit")
@click.option('--higher-limit', type=click.IntRange(1, 10), default=10, help="Radio Paradise rating higher limit")
@click.option('--tmp-file', default='spotify-cli.downloaded.csv')
@click.option('--playlist', required=True, help="Spotify playlist id")
@click.option('--commit', is_flag=True, default=False, help="Use this flag to commit changes.")
@click.pass_obj
def rp(spotify, batch_size, rp_user_id, lower_limit, higher_limit, tmp_file, playlist, commit):
    """Import music from Radio Paradise favorites to playlist"""
    try:
        api = spotify.api

        content = requests.get(
            f"https://api.radioparadise.com/siteapi.php?"
            f"file=music::download-favorites&"
            f"lower_limit={lower_limit}&"
            f"upper_limit={higher_limit}&"
            f"user_id={rp_user_id}&"
            f"format=csv"
        ).content

        csv_file = open(tmp_file, 'wb')
        csv_file.write(content)
        csv_file.close()

        _process_csv(api, tmp_file, playlist, batch_size, commit)
        os.remove(tmp_file)
        logging.info("Done!")

    except Exception as err:
        print("Exception : %s\n" % err)
        raise click.Abort()


def _process_csv(api, file, playlist, batch_size, commit):
    """
    Process a CSV file

    :param api:
    :param file:
    :param playlist:
    :param batch_size:
    :param commit:
    :return:
    """
    tracks_to_add = []
    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        failures = 0

        playlist_tracks = _get_playlist_tracks(api, playlist, batch_size)

        for row in csv_reader:
            if line_count == 0:
                logging.debug(f'Column names are {", ".join(row)}')
                line_count += 1

            tracks = _search_track(api, row['title'], row['artist'])
            line_count += 1

            if not len(tracks):
                logging.error(f"No result for {row['title']} - {row['artist']}")
                failures += 1
                continue

            logging.debug(f"Found {row['title']} - {row['artist']}")

            if not _track_in_playlist(tracks, playlist_tracks):
                logging.warning(f"{row['title']} - {row['artist']} will be added to playlist")
                tracks_to_add.extend([tracks[0]['uri']])
            else:
                logging.info(f"{row['title']} - {row['artist']} is already in playlist, skipping...")

        logging.info(f'Processed {line_count} lines ({failures} failures).')

    if len(tracks_to_add):
        if commit:
            logging.info(f"Adding {len(tracks_to_add)} tracks to playlist")
            _add_tracks_to_playlist(api, playlist, tracks_to_add, batch_size)
        else:
            logging.warning(f"Would have added {len(tracks_to_add)} tracks to playlist")
            logging.warning(f"Use --commit flag to proceed.")
    else:
        logging.info('No new tracks to add')


def _search_track(api, title, artist):
    """
    Search for a Spotify track based on title and artist

    :param api:
    :param title:
    :param artist:
    :return:
    """
    # Query
    q = f'artist:{_sanitize_str(artist)} track:{_sanitize_str(title)}'
    logging.debug(q)
    results = api.search(
        q=q,
        type='track'
    )

    return results['tracks']['items']


def _track_in_playlist(tracks, playlist_tracks):
    """
    Check if a track URI is already in the Spotify playlist

    :param tracks:
    :param playlist_tracks:
    :return:
    """
    playlist_tracks_uris = [item['track']['uri'] for item in playlist_tracks]

    for track in tracks:
        if track['uri'] in playlist_tracks_uris:
            return True

    return False


def _get_playlist_tracks(api, playlist, batch_size):
    """
    Get all tracks from the Spotify playlist

    :param api:
    :param playlist:
    :param batch_size:
    :return:
    """
    results = api.playlist_tracks(playlist, limit=batch_size)
    offset = batch_size
    logging.info(f"Fetched {offset}/{results['total']} tracks from existing playlist...")
    tracks = results['items']
    while results['next']:
        results = api.next(results)
        offset = offset + batch_size if (offset + batch_size) < results['total'] else results['total']
        logging.info(f"Fetched {offset}/{results['total']} tracks from existing playlist... ")
        tracks.extend(results['items'])
    logging.info(f"Fetched {len(tracks)} tracks from existing playlist")

    return tracks


def _split_chunks(chunk, size):
    chunks = [chunk[i * size:(i + 1) * size] for i in range((len(chunk) + size - 1) // size)]

    return chunks


def _add_tracks_to_playlist(api, playlist, tracks, batch_size):
    """
    Add a track to the Spotify playlist

    :param api:
    :param playlist:
    :param tracks:
    :param batch_size:
    :return:
    """
    chunks = _split_chunks(tracks, batch_size)
    offset = batch_size

    for chunk in chunks:
        api.playlist_add_items(playlist, chunk)
        logging.info(f"Added {offset}/{len(tracks)} tracks to playlist...")
        offset = offset + batch_size if (offset + batch_size) < len(tracks) else len(tracks)

    logging.info(f"Added {len(tracks)} tracks to playlist")


def _sanitize_str(s):
    """
    Remove special characters from string
    :param s:
    :return:
    """
    return re.sub("[`\'$@&.]", "", s)
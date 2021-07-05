import click
import csv
import os
import requests
import logging


@click.group()
def sync():
    """
    Use this command to sync data into playlists
    """
    pass


@sync.command("csv-file")
@click.option('--file', type=click.Path(exists=True))
@click.option('--playlist', required=True)
@click.option('--commit', is_flag=True, default=False, help="Use this flag to commit changes.")
@click.pass_obj
def csv_file(spotify, file, playlist, commit):
    """Import music from CSV to playlist"""
    try:
        api = spotify.api
        _process_csv(api, file, playlist, commit)
        logging.info("Done!")

    except Exception as err:
        print("Exception : %s\n" % err)
        raise click.Abort()


@sync.command("rp")
@click.option('--rp-user-id', required=True)
@click.option('--lower-limit', type=click.IntRange(1, 10), default=7)
@click.option('--higher-limit', type=click.IntRange(1, 10), default=10)
@click.option('--tmp-file', default='spotify-cli.downloaded.csv')
@click.option('--playlist', required=True)
@click.option('--commit', is_flag=True, default=False, help="Use this flag to commit changes.")
@click.pass_obj
def rp(spotify, rp_user_id, lower_limit, higher_limit, tmp_file, playlist, commit):
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

        _process_csv(api, tmp_file, playlist, commit)
        os.remove(tmp_file)
        logging.info("Done!")

    except Exception as err:
        print("Exception : %s\n" % err)
        raise click.Abort()


def _process_csv(api, file, playlist, commit):
    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        failures = 0

        playlist_tracks = _get_playlist_tracks(api, playlist)

        for row in csv_reader:
            if line_count == 0:
                logging.debug(f'Column names are {", ".join(row)}')
                line_count += 1

            track_uri = _search_track(api, row['title'], row['artist'])
            line_count += 1

            if not track_uri:
                failures += 1
                continue

            if not _track_in_playlist(track_uri, playlist_tracks):
                if commit:
                    logging.info(f"Adding {row['title']} - {row['artist']} to playlist")
                    api.playlist_add_items(playlist, [track_uri])
                else:
                    logging.warning(f"Would have added {row['title']} - {row['artist']} to playlist")
                    logging.warning(f"Use --commit flag to proceed.")
            else:
                logging.info(f"{row['title']} - {row['artist']} is already in playlist, skipping...")

        logging.info(f'Processed {line_count} lines ({failures} failures).')


def _search_track(api, title, artist):
    logging.debug(f"Query: artist: {artist} track: {title}")
    results = api.search(q=f"artist: {artist} track: {title}", type='track')

    if len(results['tracks']['items']) == 0:
        logging.error(f"No result for {title} - {artist}")
        return 0

    logging.debug(f"Found {title} - {artist}")

    return results['tracks']['items'][0]['uri']


def _track_in_playlist(track_uri, playlist_tracks):
    return any(item['track']['uri'] == track_uri for item in playlist_tracks)


def _get_playlist_tracks(api, playlist):
    tracks = api.playlist_tracks(playlist)
    return tracks['items']

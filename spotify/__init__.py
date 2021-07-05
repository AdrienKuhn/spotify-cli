#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import logging
import coloredlogs

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotify.artists import artists
from spotify.playlists import playlists


class Spotify(object):
    def __init__(self):
        self.scope = "user-library-read,user-follow-read,user-follow-modify,playlist-modify-private,playlist-modify-public"
        self.redirect_uri = "http://localhost:8000/callback"
        self.cache_path = "cache"
        self.api = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=self.scope,
            redirect_uri=self.redirect_uri,
            show_dialog=True,
            cache_path=self.cache_path
        ))


@click.group()
@click.option('--level', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']), help='Verbose level', default='INFO')
@click.pass_context
def main(ctx, level):
    # Enabling logs
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % level)
    logging.basicConfig(level=numeric_level)
    coloredlogs.install(
        level=level.upper(),
        fmt='%(asctime)s,%(msecs)03d %(name)s[%(process)d] %(levelname)s %(message)s'
    )

    ctx.obj = Spotify()
    pass


main.add_command(artists)
main.add_command(playlists)

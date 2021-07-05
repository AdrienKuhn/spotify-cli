#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from .sync import sync


@click.group()
def playlists():
    """
    Use this command to manage playlists
    """
    pass


playlists.add_command(sync)

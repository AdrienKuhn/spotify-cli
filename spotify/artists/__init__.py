#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from .follow import follow


@click.group()
def artists():
    """
    Use this command to manage artists
    """
    pass


artists.add_command(follow)

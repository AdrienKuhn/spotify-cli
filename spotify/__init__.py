#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import logging
import coloredlogs

from spotify.artists import artists


@click.group()
@click.option('--level', type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']), help='Verbose level', default='INFO')
def main(level):
    # Enabling logs
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % level)
    logging.basicConfig(level=numeric_level)
    coloredlogs.install(
        level=level.upper(),
        fmt='%(asctime)s,%(msecs)03d %(name)s[%(process)d] %(levelname)s %(message)s'
    )
    pass


main.add_command(artists)

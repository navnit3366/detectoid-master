#!/usr/bin/env python
"""
detectoid
------------------------------
Detectoid, a simple website to guess whether a Twitch stream has viewbots
"""

from pyramid.config import Configurator

from detectoid.config import set_config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    set_config(settings)
    config = Configurator(settings=settings)

    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('stream', '/stream/{stream}')
    config.add_route('chatters', '/stream/{stream}/chatters')
    config.add_route('directory', '/directory/{directory}')

    config.scan(ignore='detectoid.tests')

    return config.make_wsgi_app()

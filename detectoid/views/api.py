"""
"""

from pyramid.view import view_config
import pyramid.httpexceptions as exc

from detectoid.twitch import Twitch


@view_config(route_name='home', renderer='detectoid:templates/directory.pt',
             accept="text/html")
def home(request):
    """
    /

    Either a simple homepage or a proxy to an api endpoint depending on params
    """
    if "stream" in request.params:
        request.matchdict["stream"] = request.params["stream"]
        return stream(request)
    elif "directory" in request.params:
        request.matchdict["directory"] = request.params["directory"]
        return directory(request)
    else:
        return {
            'streams': [],
        }


@view_config(route_name='stream', renderer="json")
@view_config(route_name='stream', renderer='detectoid:templates/directory.pt',
             accept="text/html")
def stream(request):
    """
    /stream/{stream}

    - stream: stream name

    Returns basic stream info (viewers, chatters, followers, etc)
    """
    name = request.matchdict["stream"].lower()
    info = Twitch().stream(name)

    if info is None:
        raise exc.HTTPInternalServerError("Error while loading stream details {}".format(name))  # NOQA

    if info is False:
        raise exc.HTTPNotFound("Offline stream {}".format(name))

    return {
        'streams': [info],
    }

@view_config(route_name='directory', renderer="json")
@view_config(route_name='directory', renderer='detectoid:templates/directory.pt',
             accept="text/html")
def directory(request):
    """
    /directory/{directory} (optional)

    - directory: sub-section of the directory

    Returns basic stream info (viewers, chatters, followers, etc) for the top 20
    streams in a section
    """
    directory = request.matchdict["directory"].lower()
    info = Twitch().streams(directory)

    if info is None:
        raise exc.HTTPInternalServerError("Error while loading streams details {}".format(directory))  # NOQA

    if info is False:
        raise exc.HTTPNotFound("Unknown directory {}".format(directory))

    return {
        'streams': info,
    }


@view_config(route_name='chatters', renderer="json")
def chatters(request):
    """
    /{stream}

    - stream: stream name

    Returns a list of chatters with their registration date
    """
    channel = request.matchdict["stream"].lower()
    users = Twitch().chatters(channel)

    if users is None:
        raise exc.HTTPInternalServerError("Error while loading channel details {}".format(channel))

    return {
        'chatters': users,
    }

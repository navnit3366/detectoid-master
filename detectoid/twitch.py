"""
Twitch API consumption
"""

import datetime
import logging

import json
import requests

from detectoid.config import get_config
from detectoid.model import get_session
from detectoid.model.user import User

logger = logging.getLogger()

endpoints = {
    'streams': "https://api.twitch.tv/kraken/streams?limit=15&{}",
    'stream': "https://api.twitch.tv/kraken/streams/{}",
    'chatters': "http://tmi.twitch.tv/group/user/{}/chatters",
    'profile': "https://api.twitch.tv/kraken/users/{}",
    'follows': "https://api.twitch.tv/kraken/users/{}/follows/channels?limit=1",
}


def parse_date(string):
    return datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")


class Twitch(object):

    def __init__(self):
        self.tcp = requests.Session()
        self.tcp.headers.update({'client_id': get_config()["twitch.client_id"]})

        self.db = get_session()

    def _load_json(self, uri):
        try:
            return self.tcp.get(uri).json()
        except (json.decoder.JSONDecodeError, TypeError):
            try:
                return self.tcp.get(uri).json()
            except (json.decoder.JSONDecodeError, TypeError):
                logger.warning("failed to load the json at %s", uri)

    def streams(self, game):
        """
        Returns basic stats about the top 20/25 streams of a section
        """
        if game is None or game == "all":
            data = self._load_json(endpoints['streams'].format(""))
        else:
            data = self._load_json(endpoints['streams'].format("game="+game))

        if data is None:
            return None

        if "status" in data and data["status"] in [404, 422]:
            return False

        if "streams" not in data or data["streams"] is None:
            return False

        streams = []
        for stream in data["streams"]:
            info = self._stream_details(stream)

            if info:
                streams.append(info)

        return streams

    def stream(self, name):
        """
        Returns basic stats about a stream
        """
        data = self._load_json(endpoints['stream'].format(name))

        if data is None:
            return None

        if "status" in data and data["status"] in [404, 422]:
            return False

        if "stream" not in data or data["stream"] is None:
            return False

        return self._stream_details(data["stream"])

    def chatters(self, channel):
        """
        Returns a list of Users logged into a chat channel
        """
        names = self._list_chatters(channel)

        if names is None:
            return None

        # load existing users from db and schedule others to be loaded from Twitch
        users = []
        to_load = []
        for name in names:
            user = self.db.query(User).filter(User.name == name).one_or_none()

            if user:
                users.append(user)
            else:
                to_load.append(name)

        # load new users
        new_users = self._load_users(to_load)
        self.db.bulk_save_objects(new_users, return_defaults=True)
        users.extend(new_users)

        return users

    def _stream_details(self, data):
        """
        Returns details about a stream from pre-loaded data
        """
        if data is None or "name" not in data["channel"]:
            return None

        chatters = self._list_chatters(data["channel"]["name"])

        if chatters is None:
            chatters_count = 0
        else:
            chatters_count = len(chatters)

        return {
            'name': data["channel"]["display_name"],
            'views': data["channel"]["views"],
            'followers': data["channel"]["followers"],
            'viewers': data["viewers"],
            'chatters': chatters_count,
        }

    def _list_chatters(self, channel):
        """
        Returns a list of usernames logged into a chat channel
        """
        data = self._load_json(endpoints['chatters'].format(channel))

        if data is None:
            logger.warning("no data in _list_chatters(%s)", channel)
            return None

        if "chatters" not in data:
            logger.warning("bogus data in _list_chatters(%s)", channel)
            return None

        return data["chatters"]["moderators"] + data["chatters"]["viewers"]

    def _load_users(self, names):
        """
        Returns Users objects loaded from Twitch
        """
        users = [self._load_user(name) for name in names]
        users = list(filter(None.__ne__, users))

        return users

    def _load_user(self, username):
        """
        Returns a loaded User object from its username
        """
        # new user, load details and persist it
        logger.debug("loading new user %s", username)

        # load user profile
        record = self._user_profile(username)

        if record is None:
            return None

        # load follows count
        # follows = self._user_follows(username)

        # if follows is None:
        follows = 0

        # TODO: the Twitch to ORM conversion might be done somewhere else
        user = User(name=record["name"],
                    created=parse_date(record["created_at"]),
                    updated=parse_date(record["updated_at"]),
                    follows=follows)

        return user

    def _user_profile(self, username):
        """
        Returns a user profile, as a dictionnary, loaded from Twitch
        """
        data = self._load_json(endpoints['profile'].format(username))

        if data is None:
            logger.warning("no data in _user_profile(%s)", username)
            return None

        if "created_at" not in data:
            return None

        return data

    def _user_follows(self, username):
        """
        Returns the number of channels followed by a user
        """
        data = self._load_json(endpoints['follows'].format(username))

        if data is None:
            logger.warning("no data in _user_follows(%s)", username)
            return None

        if "_total" not in data:
            logger.warning("bogus data in _user_follows(%s)", username)
            return None

        return data["_total"]

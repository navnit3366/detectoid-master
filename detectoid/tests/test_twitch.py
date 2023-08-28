
import os
import json
import datetime
from unittest import TestCase

from mock import Mock, patch  # NOQA

from detectoid.model import get_session
from detectoid.model.user import User
from detectoid.twitch import Twitch, parse_date  # NOQA


class TwitchTests(TestCase):

    def setUp(self):
        self.db = get_session()
        self.db.query(User).delete()

    def create_user(self, username):
        created = datetime.datetime.now()
        updated = created + datetime.timedelta(days=10)
        user = User(name=username, created=created, updated=updated, follows=8)

        self.db.add(user)
        self.db.flush()

        return user

    def test_load_json_decode_error(self):
        """
        """
        twitch = Twitch()
        twitch.tcp.get = Mock(side_effect=json.decoder.JSONDecodeError('a', 'b', 10))  # NOQA

        self.assertEqual(None, twitch._load_json("bar"))

    def test_load_json_type_error(self):
        """
        """
        twitch = Twitch()
        twitch.tcp.get = Mock(side_effect=TypeError)

        self.assertEqual(None, twitch._load_json("baz"))

    def test_chatters(self):
        """
        """
        viewer = self.create_user("viewer")
        moderator = self.create_user("moderator")
        chatters = {
            "chatters": {
                "viewers": [viewer.name, "foobar"],
                "moderators": [moderator.name]
            }
        }
        twitch = Twitch()
        mock_response = Mock()
        mock_response.json.return_value = chatters
        twitch.tcp.get = Mock(return_value=mock_response)

        self.assertEqual(twitch.chatters("foo"), [moderator, viewer])

    @patch('detectoid.twitch.Twitch._load_json', return_value=None)
    def test_chatters_failed(self, _load_json):
        """
        """
        twitch = Twitch()

        self.assertEqual(None, twitch.chatters("bar"))

    @patch('detectoid.twitch.Twitch._load_json', return_value={})
    def test_chatters_bogus(self, _load_json):
        """
        """
        twitch = Twitch()

        self.assertEqual(None, twitch.chatters("boo"))

    def test_load_user(self):
        """
        """
        record = {
            "name": "bazbar",
            "created_at": "2016-02-26T17:29:16Z",
            "updated_at": "2016-03-26T17:29:16Z",
        }

        twitch = Twitch()
        twitch._user_profile = Mock(return_value=record)
        twitch._user_follows = Mock(return_value=None)

        user = twitch._load_user(record["name"])

        self.assertEqual(user.name, record["name"])
        self.assertEqual(user.created, parse_date(record["created_at"]))
        self.assertEqual(user.updated, parse_date(record["updated_at"]))
        self.assertEqual(user.follows, 0)

    def test_load_user_failed(self):
        """
        """
        twitch = Twitch()
        twitch._user_profile = Mock(return_value=None)

        self.assertEqual(None, twitch._load_user("foo11"))

    def test_user_profile(self):
        """
        """
        record = {
            "name": "bazbar",
            "created_at": "2016-02-26T17:29:16Z",
            "updated_at": "2016-03-26T17:29:16Z",
        }
        twitch = Twitch()
        mock_response = Mock()
        mock_response.json.return_value = record
        twitch.tcp.get = Mock(return_value=mock_response)

        self.assertEqual(record, twitch._user_profile("randomuser"))

    @patch('detectoid.twitch.Twitch._load_json', return_value=None)
    def test_user_profile_failed(self, _load_json):
        """
        """
        twitch = Twitch()

        self.assertEqual(None, twitch._user_profile("bar23"))

    @patch('detectoid.twitch.Twitch._load_json', return_value={})
    def test_user_profile_bogus(self, _load_json):
        """
        """
        twitch = Twitch()

        self.assertEqual(None, twitch._user_profile("bar23"))

    @patch('detectoid.twitch.Twitch._load_json', return_value={"_total": 420})
    def test_user_follows(self, _load_json):
        """
        """
        twitch = Twitch()

        self.assertEqual(420, twitch._user_follows("randomuser34"))

    @patch('detectoid.twitch.Twitch._load_json', return_value=None)
    def test_user_follows_failed(self, _load_json):
        """
        """
        twitch = Twitch()

        self.assertEqual(None, twitch._user_follows("bar45"))

    @patch('detectoid.twitch.Twitch._load_json', return_value={})
    def test_user_follows_bogus(self, _load_json):
        """
        """
        twitch = Twitch()

        self.assertEqual(None, twitch._user_follows("bar43"))

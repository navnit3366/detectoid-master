import unittest
import datetime

from mock import Mock, patch  # NOQA
from pyramid import testing
import pyramid.httpexceptions as exc

from detectoid.views.api import stream, chatters  # NOQA
from detectoid.model.user import User


class ChannelTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @patch('detectoid.twitch.Twitch._load_json')
    @patch('detectoid.twitch.Twitch._list_chatters')
    def test_stream(self, list_chatters, load_json):
        """
        """
        request = testing.DummyRequest()
        request.matchdict = {'stream': "foobar"}

        load_json.return_value = {
            "stream": {
                "viewers": 2025,
                "channel": {
                    "name":"foobar",
                    "display_name":"FooBar",
                    "views": 4164868,
                    "followers": 110218,
                }
            },
            "status": 200,
        }

        list_chatters.return_value = ["foo", "bar", "baz"]

        result = stream(request)["streams"][0]

        self.assertEqual(result["name"],
                         load_json.return_value["stream"]["channel"]["display_name"])  # NOQA
        self.assertEqual(result["viewers"],
                         load_json.return_value["stream"]["viewers"])
        self.assertEqual(result["views"],
                         load_json.return_value["stream"]["channel"]["views"])
        self.assertEqual(result["followers"],
                         load_json.return_value["stream"]["channel"]["followers"])  # NOQA
        self.assertEqual(result["chatters"], 3)

    @patch('detectoid.twitch.Twitch._load_json', return_value=None)
    def test_stream_invalid_stream(self, load_json):
        """
        """
        request = testing.DummyRequest()
        request.matchdict = {'stream': "foobarbaz"}
        self.assertRaises(exc.HTTPInternalServerError, lambda: stream(request))

    @patch('detectoid.twitch.Twitch._load_json')
    def test_stream_offline_stream(self, load_json):
        """
        """
        request = testing.DummyRequest()
        request.matchdict = {'stream': "foobarbaz"}

        load_json.return_value = {"stream": None}

        self.assertRaises(exc.HTTPNotFound, lambda: stream(request))

    @patch("detectoid.twitch.Twitch.chatters")
    def test_chatters(self, twitch_chatters):
        """
        """
        request = testing.DummyRequest()
        request.matchdict = {'stream': "foobarbaz"}

        now = datetime.datetime.now()
        twitch_chatters.return_value = [
            User(name="foo", created=now, updated=now, follows=1),
            User(name="bar", created=now, updated=now, follows=1),
        ]

        result = chatters(request)

        self.assertEqual(len(result["chatters"]), 2)

    @patch("detectoid.twitch.Twitch.chatters", return_value=None)
    def test_chatters_500(self, twitch_chatters):
        """
        """
        request = testing.DummyRequest()
        request.matchdict = {'stream': "foobarbaz"}
        self.assertRaises(exc.HTTPInternalServerError,
                          lambda: chatters(request))

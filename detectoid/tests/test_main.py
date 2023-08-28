"""
High-level/integration tests
"""
import os
import logging.config
import unittest

from pyramid import testing
from paste.deploy.loadwsgi import appconfig
from webtest import TestApp

from detectoid import main

here = os.path.dirname(__file__)
settings = appconfig('config:' + os.path.join(here, '../../', 'pyramid.ini'))
logging.config.fileConfig(os.path.join(here, '../../', 'pyramid.ini'))


class IntegrationTestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)
        super(IntegrationTestBase, cls).setUpClass()

    def setUp(self):
        self.testapp = TestApp(self.app)
        self.config = testing.setUp()
        super(IntegrationTestBase, self).setUp()


class HomeTests(IntegrationTestBase):
    """
    /home tests
    """

    def test_home(self):
        """
        /home
        """
        self.testapp.get('/', status=200)

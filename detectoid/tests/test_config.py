
from unittest import TestCase

from detectoid.config import get_config, set_config

class ConfigTests(TestCase):

    def test_config(self):
        """
        """
        old_config = get_config()
        set_config(None)

        get_config()
        set_config(old_config)

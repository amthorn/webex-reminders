import json
from unittest.mock import mock_open, patch
import typing

import pytest

from tests.util import mock_secrets


@pytest.fixture(autouse=True)
def setup_fixture() -> typing.Generator:
    with patch('webexteamssdk.WebexTeamsAPI') as mock_webex, \
            patch("builtins.open", mock_open(read_data=json.dumps(mock_secrets))):
        yield mock_webex

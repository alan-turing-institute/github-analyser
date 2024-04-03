"""Pytest configuration file."""
from unittest.mock import patch

import pytest
import responses
from github_analyser.utils import GITHUB_API_URL_GRAPHQL

from .mock_github import request_to_response


@pytest.fixture(scope="session")
def mock_github():
    with patch(
        "github_analyser.utils.os.environ",
        {"GITHUB_TOKEN": "this is a very good token, it gives much access"},
    ), responses.RequestsMock() as rsps:
        for request, response in request_to_response:
            rsps.add(
                responses.POST,
                GITHUB_API_URL_GRAPHQL,
                match=[responses.matchers.json_params_matcher(request)],
                json=response,
            )
        yield rsps

"""Utility functions."""
from __future__ import annotations

import logging
import os
import re
import time
from functools import reduce
from typing import Any

import requests

GITHUB_API_URL_GRAPHQL = "https://api.github.com/graphql"
GITHUB_API_URL_REST = "https://api.github.com"


def request_github_rest(
    method: str,
    end_point: str,
    payload: Any = None,
    headers: Any | None = None,
    max_tries: int = 10,
    sleep_time: float = 1.0,
) -> Any:
    """Run an autheticated query against the GitHub API.

    Assumes that the GitHub token is set in the environment variable GITHUB_TOKEN.

    Args:
        method: The HTTP method to use, e.g. "get" or "post".
        end_point: The end point to query.
        payload: The payload to send with the request.
        headers: Any additional headers to pass to the request.
        max_tries: The maximum number of times to try the request. Optional, default is 10.
        sleep_time: The time to sleep between tries. Optional, default is 1.0.

    Returns:
        The response from the GitHub API as parsed JSON.
    """
    if headers is None:
        headers = {}
    github_token = os.environ["GITHUB_TOKEN"]
    headers["Authorization"] = f"Bearer {github_token}"
    request_func = getattr(requests, method)
    url = f"{GITHUB_API_URL_REST}/{end_point}"
    response = request_func(url, json=payload, headers=headers)
    counter = 0
    while response.status_code == 202 and counter < max_tries:
        # This is GitHub's way of saying "I'm working on it, come back later".
        time.sleep(sleep_time)
        response = request_func(url, json=payload, headers=headers)
    if response.status_code != 200:
        msg = f"GitHub query failed by code {response.status_code}."
        raise Exception(msg)
    return response.json()


def request_github_graphql(payload: Any, headers: Any | None = None) -> Any:
    """Run an autheticated query against the GitHub API.

    Assumes that the GitHub token is set in the environment variable GITHUB_TOKEN.

    Args:
        payload: The query to run.
        headers: Any additional headers to pass to the request.

    Returns:
        The response from the GitHub API as parsed JSON.
    """
    if headers is None:
        headers = {}
    github_token = os.environ["GITHUB_TOKEN"]
    headers["Authorization"] = f"Bearer {github_token}"
    response = requests.post(GITHUB_API_URL_GRAPHQL, json=payload, headers=headers)
    if response.status_code != 200:
        msg = f"GitHub query failed by code {response.status_code}."
        raise Exception(msg)
    return response.json()


def query_with_pagination(
    query, page_info_path=None, cursor_variable_name="pagination_cursor", max_pages=None
) -> list[Any]:
    """Run a query with pagination.

    Args:
        query: The query to run.
        page_info_path: The path to the page info object in the response, on which we
            are paginating. This should be a list of keys, e.g.
            `["data", "repository", "issues"]`, would mean that
            `response["data"]["repository"]["issues"]["pageInfo"]` is the block from
            which we get the value for next cursor. By default, this is None, which
            means no pagination is done and the return value will be a list of length 1.
        cursor_variable_name: The name of the cursor variable in the query.
            "pagination_cursor" by default.

    Returns:
        A list of responses from the GitHub API as JSON.
    """
    if page_info_path is None:
        # There is no pagination to do.
        return [request_github_graphql({"query": query})]
    has_next_page = True
    end_cursor = None
    return_value = []
    page_counter = 0
    while has_next_page:
        page_counter += 1
        logging.debug("Requesting page %s", page_counter)
        payload = {"query": query, "variables": {cursor_variable_name: end_cursor}}
        data = request_github_graphql(payload)
        return_value.append(data)
        try:
            pagination = reduce(
                lambda d, key: d[key], page_info_path, data
            )  # reduce(function, sequence to go through, initial)
        except KeyError as e:
            msg = (
                f'Could not find page info path "{page_info_path}" in response {data}.'
            )
            raise KeyError(msg) from e
        end_cursor = pagination["pageInfo"]["endCursor"]
        has_next_page = pagination["pageInfo"]["hasNextPage"]
        if max_pages is not None and page_counter >= max_pages:
            logging.warning("Reached maximum number of pages %s.", max_pages)
            break
    return return_value


def camel_to_snake(name):
    """Convert a camel case string to snake case."""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

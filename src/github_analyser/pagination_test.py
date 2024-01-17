"""Testing paging using the issues query."""
from __future__ import annotations

import logging
import os
from typing import Any, Optional

import requests

GITHUB_API_URL = "https://api.github.com/graphql"


def request_github(payload: Any, headers: Optional[Any] = None) -> Any:
    """Run an autheticated query against the GitHub API.

    Args:
        payload: The query to run.
        headers: Any additional headers to pass to the request.

    Returns:
        The response from the GitHub API as JSON.
    """
    headers = headers if headers else {}
    github_token = os.environ["GITHUB_TOKEN"]
    headers = headers | {"Authorization": f"Bearer {github_token}"}
    response = requests.post(GITHUB_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub query failed by code {response.status_code}.")
    return response.json()


def query_with_pagination(
    query, page_info_path=None, cursor_variable_name="pagination_cursor"
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
        return [request_github({"query": query})]
    has_next_page = True
    end_cursor = None
    return_value = []
    page_counter = 0
    while has_next_page:
        page_counter += 1
        logging.debug(f"Requesting page {page_counter}")
        payload = {"query": query, "variables": {cursor_variable_name: end_cursor}}
        data = request_github(payload)
        return_value.append(data)
        subobject = data
        for key in page_info_path:
            subobject = subobject[key]
        end_cursor = subobject["pageInfo"]["endCursor"]
        has_next_page = subobject["pageInfo"]["hasNextPage"]
    return return_value


def main():
    logging.basicConfig(level=logging.DEBUG)
    query = """
    query ($issues_end_cursor: String) {
      repository(owner: "alan-turing-institute", name: "DTBase") {
        issues(first: 10, after: $issues_end_cursor, states: OPEN) {
          pageInfo {
            endCursor
            hasNextPage
          }
          totalCount
          edges {
            node {
              title
              createdAt
              closedAt
              author {
                login
              }
              comments(first: 1) {
                totalCount
                pageInfo {
                    endCursor
                    hasNextPage
                }
                edges {
                  node {
                    author {
                      login
                    }
                    createdAt
                  }
                }
              }
              labels(first: 10) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data = query_with_pagination(
        query,
        page_info_path=["data", "repository", "issues"],
        cursor_variable_name="issues_end_cursor",
    )
    for page in data:
        issues = page["data"]["repository"]["issues"]["edges"]
        print("\nNext 10 issues:")
        for issue in issues:
            print(issue["node"])


if __name__ == "__main__":
    main()

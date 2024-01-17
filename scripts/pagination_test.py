from __future__ import annotations

import logging

from github_analyser.utils import query_with_pagination


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

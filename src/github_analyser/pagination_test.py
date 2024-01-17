"""Testing paging using the issues query."""
import os

import requests


def main():
    github_token = os.environ["GITHUB_TOKEN"]

    # Define the headers for the request
    headers = {"Authorization": f"Bearer {github_token}"}

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

    url = "https://api.github.com/graphql"
    issues_has_next_page = True
    issues_end_cursor = None
    while issues_has_next_page:
        payload = {
            "query": query,
            "variables": {
                "issues_end_cursor": issues_end_cursor,
            },
        }
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        # Extract the repositories
        issues = data["data"]["repository"]["issues"]["edges"]

        print("\nNext 10 issues:")
        for issue in issues:
            print(issue["node"])
        issues_end_cursor = data["data"]["repository"]["issues"]["pageInfo"][
            "endCursor"
        ]
        issues_has_next_page = data["data"]["repository"]["issues"]["pageInfo"][
            "hasNextPage"
        ]


if __name__ == "__main__":
    main()

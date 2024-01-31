import os
import json

import pandas as pd
import requests

from github_analyser.utils import query_with_pagination

def get_pull_requests():
    github_token = os.environ["GITHUB_TOKEN"]

    # Define the headers for the request
    headers = {"Authorization": f"Bearer {github_token}"}

    query = """
        query ($issues_end_cursor: String) {
            repository(owner: "alan-turing-institute", name: "AutSPACEs") {
                pullRequests(first: 10, after: $issues_end_cursor, states: OPEN) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    totalCount
                    edges {
                        node {
                            id
                            author {
                                login
                            }
                            changedFiles
                            comments(first:100) {
                                edges {
                                    node {
                                        author {
                                            login
                                        }
                                    }
                                }
                            }
                            closed
                            closedAt
                            createdAt
                            lastEditedAt
                            merged
                            mergedAt
                            mergedBy {
                                login
                            }
                            state
                            updatedAt
                            totalCommentsCount
                            reviews(first: 10) {
                                edges {
                                    node {
                                        author {
                                            login
                                        }
                                        state
                                    }
                                }
                            }
                        }
                    }
                }
            }
    }
    """

    data = query_with_pagination(query, ["data", "repository", "pullRequests"])
    return data

if __name__ == "__main__":
    data = get_pull_requests()
    data_nodes  = [edge["node"] for datum in data for edge in datum["data"]["repository"]["pullRequests"]["edges"]]
    df = pd.json_normalize(data_nodes)
    df.to_csv("data/pull_requests.csv")
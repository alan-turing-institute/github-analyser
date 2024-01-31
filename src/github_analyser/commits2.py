import os
import requests
import pandas as pd
from github_analyser.utils import query_with_pagination
import logging


def flatten_author_field(commit_node):
    """Flatten the author field in a commit node."""
    author_data = commit_node.get('author', {})
    commit_node['author_name'] = author_data.get('name')
    commit_node['author_date'] = author_data.get('date')
    del commit_node['author']  # Remove the original author dictionary
    return commit_node

def fetch_commits(repo_owner: str, repo_name: str, total_commits_to_fetch=20) -> pd.DataFrame:
    query_template = """
    query ($afterCursor: String) {
        repository(owner: "%s", name: "%s") {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 10, after: $afterCursor) {
                            edges {
                                node {
                                    messageHeadline
                                    author {
                                        name
                                        date
                                    }
                                    additions
                                    deletions
                                }
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
            }
        }
    }
    """ % (repo_owner, repo_name)

    responses = query_with_pagination(query_template, ["data", "repository", "defaultBranchRef", "target", "history"],
                                       "afterCursor")
  
    flattened_responses = []
    for response in responses:
        edges = response['data']['repository']['defaultBranchRef']['target']['history']['edges']
        for edge in edges:
            node = edge['node']
            flattened_node = flatten_author_field(node)
            flattened_responses.append(flattened_node)
            if len(flattened_responses) >= total_commits_to_fetch:
                break
        if len(flattened_responses) >= total_commits_to_fetch:
            break

        df = pd.DataFrame(flattened_responses)
        return df

if __name__ == "__main__":
    owner = 'alan-turing-institute'
    repo = 'DTBase'
    num_commits = 20
    df = fetch_commits(owner, repo, num_commits)
    print(df)
import pandas as pd
from github_analyser.utils import query_with_pagination


def fetch_commits(repo_owner: str, repo_name: str, total_commits_to_fetch=20, 
                  save_csv=False, csv_path='commits.csv') -> pd.DataFrame:
    """Fetch info about commits from a GitHub repo.
    
    Args:
        repo_owner: The owner of the repository.
        repo_name: The name of the repository.
        total_commits_to_fetch: The total number of commits to fetch.
        
    Returns:
        A pandas DataFrame with the following columns:
            - message: The commit message.
            - additions: The number of additions in the commit.
            - deletions: The number of deletions in the commit.
            - author: The author of the commit.
            - date: The date of the commit.
    """
    
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
                                      'afterCursor')
  
    nodes = []
    for response in responses:
        edges = response['data']['repository']['defaultBranchRef']['target']['history']['edges']
        nodes.extend(edge['node'] for edge in edges)
        if len(nodes) >= total_commits_to_fetch:
            break
    
    df = pd.json_normalize(nodes, sep='_')
    df.rename(columns={'messageHeadline': 'message',
                       'author_name': 'author',
                       'author_date': 'date'}, inplace=True)
    
    if save_csv:
        df.to_csv(csv_path, index=False)
        
    return df
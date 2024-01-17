import os
import requests
import pandas as pd

def fetch_commits(repo_owner, repo_name, total_commits_to_fetch=20):
    github_token = os.environ["GITHUB_TOKEN"]
    headers = {"Authorization": f"Bearer {github_token}"}

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

    url = "https://api.github.com/graphql"
    hasNextPage = True
    endCursor = None
    commit_data = []
    total_commits_to_fetch = total_commits_to_fetch
    commits_fetched = 0

    while hasNextPage:
        payload = {
            "query": query_template,
            "variables": {
                "afterCursor": endCursor,
            },
        }
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        commits = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]["edges"]
        for commit in commits:
            
            if commits_fetched >= total_commits_to_fetch:
                break
            
            commit_info = {
                "messageHeadline": commit["node"]["messageHeadline"],
                "authorName": commit["node"]["author"]["name"],
                "authorDate": commit["node"]["author"]["date"],
                "additions": commit["node"]["additions"],
                "deletions": commit["node"]["deletions"]
            }
            commit_data.append(commit_info)
            commits_fetched += 1

        pageInfo = data["data"]["repository"]["defaultBranchRef"]["target"]["history"]["pageInfo"]
        endCursor = pageInfo["endCursor"]
        hasNextPage = pageInfo["hasNextPage"]

        # Convert the list of commit data to a DataFrame
        df = pd.DataFrame(commit_data)
        
        return df

if __name__ == "__main__":
    owner = 'alan-turing-institute'
    repo = 'DTBase'
    num_commits = 20
    df = fetch_commits(owner, repo, num_commits)
    print(df)

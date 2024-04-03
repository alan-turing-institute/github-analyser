"""Utilities for mocking GitHub API responses."""

repos_query = """
    query ($pagination_cursor: String) {
      organization(login: "alan-turing-institute") {
        repositories(first: 100, after: $pagination_cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
          pageInfo {
            endCursor
            hasNextPage
          }
          edges {
            node {
              id
              name
              updatedAt
              url
              isPrivate
              isArchived
              languages(first: 10) {
                totalSize
                edges {
                  size
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

issues_query = """
query ($pagination_cursor: String) {
  repository(owner: "alan-turing-institute", name: "github-analyser") {
    issues(first: 100, after: $pagination_cursor, orderBy: {field: UPDATED_AT, direction: DESC}) {
      pageInfo {
        endCursor
        hasNextPage
      }
      edges {
        node {
          title
          body
          createdAt
          closedAt
          author {
            login
          }
          comments(first: 100) {
            totalCount
            edges {
              node {
                author {
                  login
                }
                createdAt
                body
              }
            }
          }
          labels(first: 10) {
            totalCount
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

# A list of pairs of request body and response body.
# These are mimic responses from GitHub in format, but the values are mostly made up.
request_to_response = [
    (
        {
            "query": repos_query,
            "variables": {"pagination_cursor": None},
        },
        {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "Y3Vyc29yOnYyOpK5MjAyMy0xMi0wMVQwOTozNzozMSswMDowMM4m07cV",
                            "hasNextPage": True,
                        },
                        "edges": [
                            {
                                "node": {
                                    "id": "R_kgDOGF3YCQ",
                                    "name": "TestRepo01",
                                    "updatedAt": "2024-02-28T22:38:30Z",
                                    "url": "https://github.com/alan-turing-institute/TestRepo01",
                                    "isPrivate": False,
                                    "isArchived": False,
                                    "languages": {
                                        "totalSize": 50657,
                                        "edges": [
                                            {"size": 1773, "node": {"name": "HTML"}},
                                            {
                                                "size": 23512,
                                                "node": {"name": "JavaScript"},
                                            },
                                            {
                                                "size": 25179,
                                                "node": {"name": "TypeScript"},
                                            },
                                            {"size": 193, "node": {"name": "CSS"}},
                                        ],
                                    },
                                }
                            },
                            {
                                "node": {
                                    "id": "R_kgDOLKFIkg",
                                    "name": "TestRepo02",
                                    "updatedAt": "2024-02-28T15:17:15Z",
                                    "url": "https://github.com/alan-turing-institute/TestRepo02",
                                    "isPrivate": True,
                                    "isArchived": False,
                                    "languages": {"totalSize": 0, "edges": []},
                                }
                            },
                            {
                                "node": {
                                    "id": "R_kgDOKCKwHw",
                                    "name": "TestRepo03",
                                    "updatedAt": "2024-02-27T15:32:29Z",
                                    "url": "https://github.com/alan-turing-institute/TestRepo03",
                                    "isPrivate": False,
                                    "isArchived": True,
                                    "languages": {
                                        "totalSize": 4127284,
                                        "edges": [
                                            {
                                                "size": 4127284,
                                                "node": {"name": "Jupyter Notebook"},
                                            }
                                        ],
                                    },
                                }
                            },
                            {
                                "node": {
                                    "id": "R_kgDOK5PAAQ",
                                    "name": "github-analyser",
                                    "updatedAt": "2023-12-13T11:53:26Z",
                                    "url": "https://github.com/alan-turing-institute/github-analyser",
                                    "isPrivate": True,
                                    "isArchived": True,
                                    "languages": {"totalSize": 0, "edges": []},
                                }
                            },
                        ],
                    }
                }
            }
        },
    ),
    (
        {
            "query": repos_query,
            "variables": {
                "pagination_cursor": "Y3Vyc29yOnYyOpK5MjAyMy0xMi0wMVQwOTozNzozMSswMDowMM4m07cV"
            },
        },
        {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "Y3Vyc29yOnYyOpK5MjAyMy0wNi0xMlQxNTo1NToxNSswMTowMM4LD59F",
                            "hasNextPage": True,
                        },
                        "edges": [
                            {
                                "node": {
                                    "id": "R_kgDOHIBmBA",
                                    "name": "This is not a test repo",
                                    "updatedAt": "2023-11-30T14:57:44Z",
                                    "url": "https://github.com/alan-turing-institute/defonot",
                                    "isPrivate": True,
                                    "isArchived": True,
                                    "languages": {"totalSize": 0, "edges": []},
                                }
                            },
                            {
                                "node": {
                                    "id": "R_kgDOKEYaMA",
                                    "name": "Who needs more test repos?",
                                    "updatedAt": "2023-11-14T18:12:47Z",
                                    "url": "https://github.com/alan-turing-institute/idont",
                                    "isPrivate": False,
                                    "isArchived": False,
                                    "languages": {
                                        "totalSize": 1,
                                        "edges": [
                                            {
                                                "size": 1,
                                                "node": {"name": "Jupyter Notebook"},
                                            }
                                        ],
                                    },
                                }
                            },
                        ],
                    }
                }
            }
        },
    ),
    (
        {
            "query": repos_query,
            "variables": {
                "pagination_cursor": "Y3Vyc29yOnYyOpK5MjAyMy0wNi0xMlQxNTo1NToxNSswMTowMM4LD59F"
            },
        },
        {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "Y3Vyc29yOnYyOpK5MjAyMi0wOC0yOFQxNTowNjoxMCswMTowMM4NJA8S",
                            "hasNextPage": True,
                        },
                        "edges": [
                            {
                                "node": {
                                    "id": "R_kgDOHsvwSw",
                                    "name": "Also why does this result have so many pages",
                                    "updatedAt": "2023-06-12T14:29:46Z",
                                    "url": "https://github.com/alan-turing-institute/ugghhpages",
                                    "isPrivate": False,
                                    "isArchived": False,
                                    "languages": {
                                        "totalSize": 1,
                                        "edges": [
                                            {
                                                "size": 1,
                                                "node": {"name": "Python"},
                                            }
                                        ],
                                    },
                                }
                            },
                            {
                                "node": {
                                    "id": "R_kgDOJsldcw",
                                    "name": "And besides, they are supposed to have 100 repos each, but only have like 2",
                                    "updatedAt": "2023-06-09T15:50:54Z",
                                    "url": "https://github.com/alan-turing-institute/yeahimlazytowrite100",
                                    "isPrivate": False,
                                    "isArchived": False,
                                    "languages": {
                                        "totalSize": 1,
                                        "edges": [
                                            {
                                                "size": 1,
                                                "node": {"name": "Python"},
                                            }
                                        ],
                                    },
                                }
                            },
                        ],
                    }
                }
            }
        },
    ),
    (
        {
            "query": repos_query,
            "variables": {
                "pagination_cursor": "Y3Vyc29yOnYyOpK5MjAyMi0wOC0yOFQxNTowNjoxMCswMTowMM4NJA8S"
            },
        },
        {
            "data": {
                "organization": {
                    "repositories": {
                        "pageInfo": {
                            "endCursor": "Y3Vyc29yOnYyOpK5MjAyMi0wMS0wNVQwOTowNDo0NSswMDowMM4affLv",
                            "hasNextPage": False,
                        },
                        "edges": [
                            {
                                "node": {
                                    "id": "MDEwOlJlcG9zaXRvcnkxMDgzMjMyODg=",
                                    "name": "This promises to be the last page",
                                    "updatedAt": "2022-08-08T03:47:24Z",
                                    "url": "https://github.com/alan-turing-institute/itbetterbetoo",
                                    "isPrivate": False,
                                    "isArchived": False,
                                    "languages": {
                                        "totalSize": 1,
                                        "edges": [
                                            {
                                                "size": 1,
                                                "node": {"name": "Python"},
                                            }
                                        ],
                                    },
                                }
                            },
                            {
                                "node": {
                                    "id": "R_kgDOHR4eEQ",
                                    "name": "Yaaaay",
                                    "updatedAt": "2022-08-02T13:36:34Z",
                                    "url": "https://github.com/alan-turing-institute/grumblegrumble",
                                    "isPrivate": False,
                                    "isArchived": False,
                                    "languages": {
                                        "totalSize": 1,
                                        "edges": [
                                            {
                                                "size": 1,
                                                "node": {"name": "Python"},
                                            }
                                        ],
                                    },
                                }
                            },
                        ],
                    }
                }
            }
        },
    ),
    (
        {
            "query": issues_query,
            "variables": {"pagination_cursor": None},
        },
        {
            "data": {
                "repository": {
                    "issues": {
                        "pageInfo": {
                            "endCursor": "Y3Vyc29yOnYyOpK5MjAyMy0xMS0wN1QxNDo0MDoxMCswMDowMM5jzBSD",
                            "hasNextPage": False,
                        },
                        "edges": [
                            {
                                "node": {
                                    "title": "Markus needs new socks",
                                    "body": "Kinda urgent",
                                    "createdAt": "2024-02-29T12:11:12Z",
                                    "closedAt": None,
                                    "author": {"login": "mhauru"},
                                    "comments": {
                                        "totalCount": 1,
                                        "edges": [
                                            {
                                                "node": {
                                                    "author": {"login": "mhauru"},
                                                    "createdAt": "2024-02-29T12:12:22Z",
                                                    "body": "Well, maybe not needs, but wants",
                                                }
                                            }
                                        ],
                                    },
                                    "labels": {
                                        "totalCount": 1,
                                        "edges": [{"node": {"name": "clothing"}}],
                                    },
                                }
                            },
                            {
                                "node": {
                                    "title": "Using this library causes existential dread in me, help",
                                    "body": "",
                                    "createdAt": "2024-02-29T12:03:56Z",
                                    "closedAt": None,
                                    "author": {"login": "mhauru"},
                                    "comments": {"totalCount": 0, "edges": []},
                                    "labels": {
                                        "totalCount": 0,
                                        "edges": [],
                                    },
                                }
                            },
                            {
                                "node": {
                                    "title": "I have little to say",
                                    "body": "I have a mouth but I can't scream",
                                    "createdAt": "2024-01-16T14:58:06Z",
                                    "closedAt": "2024-02-23T16:49:59Z",
                                    "author": {"login": "mastoffel"},
                                    "comments": {
                                        "totalCount": 2,
                                        "edges": [
                                            {
                                                "node": {
                                                    "author": {"login": "mhauru"},
                                                    "createdAt": "2024-01-25T17:54:58Z",
                                                    "body": "Same",
                                                }
                                            },
                                            {
                                                "node": {
                                                    "author": {"login": "rwood-97"},
                                                    "createdAt": "2024-01-26T14:36:40Z",
                                                    "body": "Me too",
                                                }
                                            },
                                        ],
                                    },
                                    "labels": {
                                        "totalCount": 2,
                                        "edges": [
                                            {"node": {"name": "help needed"}},
                                            {"node": {"name": "anatomy"}},
                                        ],
                                    },
                                }
                            },
                        ],
                    }
                }
            }
        },
    ),
]

import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

class GithubClient:
    URLBASE = "https://api.github.com/graphql"
    load_dotenv()

    def __init__(self):

        auth_token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {auth_token}"
        }

    def getTopRepositories(self):
        query = """
            query {
              search(query: "stars:>1 sort:stars-desc", type: REPOSITORY, first: 100) {
                nodes {
                  ... on Repository {
                    nameWithOwner
                    url
                    description
                    stargazerCount
                    primaryLanguage {
                      name
                    }
                    createdAt
                    releases {
                      totalCount
                    }
                    pushedAt
                  }
                }
              }
            }
        """
        payload = {"query": query}
        response = requests.post(url=GithubClient.URLBASE, headers=self.headers, json=payload).json()
        if response.get("errors"):
            print(f"Erro GQL: {response['errors'][0]['message']}")
            return None
        return response["data"]["search"]["nodes"]

    def getReleaseCount(self, repo):
        return (repo.get("releases") or {}).get("totalCount")

    def getDaysSinceLastUpdate(self, repo):
        pushed_at = repo.get("pushedAt")
        if not pushed_at:
            return None
        pushed_dt = datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        dias = (datetime.now(timezone.utc) - pushed_dt).days
        formattedDate = pushed_dt.strftime("%d/%m/%Y")
        return {
            "ultima_atualizacao": formattedDate,
            "dias_desde_atualizacao": dias
        }

if __name__ == "__main__":
    client = GithubClient()
    repositories = client.getTopRepositories()

    if repositories is not None:
        with open("top100.json", "w", encoding="utf-8") as f:
            json.dump(repositories, f, indent=2, ensure_ascii=False)
        print(f"{len(repositories)} repositórios salvos em top100.json")
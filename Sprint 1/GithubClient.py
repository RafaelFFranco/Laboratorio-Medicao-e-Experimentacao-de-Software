import os
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
              search(query: "stars:>1 sort:stars-desc", type: REPOSITORY, first: 20) {
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
                    totalIssues: issues {
                      totalCount
                    }
                    closedIssues: issues(states: CLOSED) {
                      totalCount
                    }
                    totalPullRequests: pullRequests {
                      totalCount
                    }
                    mergedPullRequests: pullRequests(states: MERGED) {
                      totalCount
                    }
                    languages(first: 10) {
                      nodes {
                        name
                      }
                    }
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

    def getClosedIssuesRatio(self, repo):
        total = (repo.get("totalIssues") or {}).get("totalCount") or 0
        closed = (repo.get("closedIssues") or {}).get("totalCount") or 0
        if total == 0:
            return None
        return round(closed / total, 4)

    def getTotalPullRequestsAceitos(self, repo):
        totalPRs = (repo.get("mergedPullRequests") or {}).get("totalCount") or "Sem informação"
        return totalPRs

    def getRepositoryAge(self, repo):
        created_at = repo.get("createdAt")
        if not created_at:
            return None

        created_dt = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        dias = (datetime.now(timezone.utc) - created_dt).days
        anos = round(dias / 365, 1)
        formattedDate = created_dt.strftime("%d/%m/%Y")

        return {
            "data_criacao": formattedDate,
            "idade_em_dias": dias,
            "idade_em_anos": anos
        }

    def getRepoLanguages(self, repo):
        nodes = repo.get("languages").get("nodes")
        languagesVector = [node.get("name") for node in nodes if node]

        languages = ", " .join(languagesVector) if languagesVector else "Sem informação"
        primaryLanguage = languagesVector[0] if languagesVector else "Sem informação"
        return {
            "primary": primaryLanguage,
            "languages": languages
        }

    def getMetricsByLanguage(self, repositories):
        grouped = {}

        for repo in repositories:
            language = self.getRepoLanguages(repo)["primary"]
            releases = self.getReleaseCount(repo) or 0
            merged_prs = self.getTotalPullRequestsAceitos(repo)
            merged_prs = merged_prs if isinstance(merged_prs, int) else 0
            last_update = self.getDaysSinceLastUpdate(repo)
            days_since_update = last_update["dias_desde_atualizacao"] if last_update else None

            if language not in grouped:
                grouped[language] = {
                    "total_releases": [],
                    "merged_prs": [],
                    "days_since_update": []
                }

            grouped[language]["total_releases"].append(releases)
            grouped[language]["merged_prs"].append(merged_prs)
            if days_since_update is not None:
                grouped[language]["days_since_update"].append(days_since_update)

        result = {}
        for language, data in grouped.items():
            releases_list = data["total_releases"]
            prs_list = data["merged_prs"]
            days_list = data["days_since_update"]

            result[language] = {
                "repository_count": len(releases_list),
                "avg_releases": round(sum(releases_list) / len(releases_list), 2),
                "avg_merged_prs": round(sum(prs_list) / len(prs_list), 2),
                "avg_days_since_update": round(sum(days_list) / len(days_list), 2) if days_list else None
            }

        return result
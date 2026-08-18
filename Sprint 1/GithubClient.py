import os
import time
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

    SEARCH_QUERY = """
        query($searchQuery: String!, $first: Int!, $cursor: String) {
          rateLimit {
            remaining
            resetAt
            cost
          }
          search(query: $searchQuery, type: REPOSITORY, first: $first, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
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

    def _post_with_retry(self, payload, max_retries=5):
        for attempt in range(max_retries):
            response = requests.post(
                url=GithubClient.URLBASE,
                headers=self.headers,
                json=payload
            )

            if response.status_code == 403 and "Retry-After" in response.headers:
                wait = int(response.headers["Retry-After"])
                print(f"Rate limit secundário. Aguardando {wait}s...")
                time.sleep(wait)
                continue

            if response.status_code >= 500:
                wait = 2 ** attempt
                print(f"Erro {response.status_code} do servidor. Retentando em {wait}s...")
                time.sleep(wait)
                continue

            data = response.json()

            if data.get("errors"):
                msg = data["errors"][0].get("message", "")
                error_type = data["errors"][0].get("type", "")
                if error_type == "RATE_LIMITED" or "rate limit" in msg.lower():
                    wait = 2 ** attempt * 5
                    print(f"Rate limit primário atingido. Aguardando {wait}s...")
                    time.sleep(wait)
                    continue
                print(f"Erro GQL: {msg}")
                return None

            rate_limit = data.get("data", {}).get("rateLimit")
            if rate_limit and rate_limit["remaining"] < 5:
                reset_at = datetime.strptime(
                    rate_limit["resetAt"], "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc)
                wait = max((reset_at - datetime.now(timezone.utc)).total_seconds(), 0) + 1
                print(f"Rate limit baixo ({rate_limit['remaining']}). Aguardando {wait:.0f}s...")
                time.sleep(wait)

            return data

        print("Número máximo de retentativas atingido.")
        return None

    def getTopRepositories(self, target_count=1000, page_size=30, delay_between_pages=1.0):
        all_repos = []
        seen = set()
        cursor = None
        has_next_page = True

        while has_next_page and len(all_repos) < target_count:
            remaining = target_count - len(all_repos)
            first = min(page_size, remaining)

            payload = {
                "query": GithubClient.SEARCH_QUERY,
                "variables": {
                    "searchQuery": "stars:>1 sort:stars-desc",
                    "first": first,
                    "cursor": cursor
                }
            }

            data = self._post_with_retry(payload)
            if data is None:
                print("Falha ao obter página. Interrompendo coleta.")
                break

            search_data = data["data"]["search"]
            nodes = search_data["nodes"]

            for repo in nodes:
                key = repo.get("nameWithOwner")
                if key and key not in seen:
                    seen.add(key)
                    all_repos.append(repo)

            page_info = search_data["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            cursor = page_info["endCursor"]

            print(f"Coletados: {len(all_repos)}/{target_count}")

            if has_next_page and len(all_repos) < target_count:
                time.sleep(delay_between_pages)

        return all_repos

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
        languages = ", ".join(languagesVector) if languagesVector else "Sem informação"
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
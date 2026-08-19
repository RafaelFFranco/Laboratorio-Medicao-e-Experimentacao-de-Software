import os
import csv
import json
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

class GithubClient:
    URLBASE = "https://api.github.com/graphql"
    load_dotenv()

    CSV_FIELDNAMES = [
        "nome_repositorio",
        "url",
        "estrelas",
        "data_criacao",
        "idade_em_dias",
        "idade_em_anos",
        "total_pull_requests",
        "total_pull_requests_aceitas",
        "total_releases",
        "data_ultima_atualizacao",
        "dias_desde_ultima_atualizacao",
        "linguagem_primaria",
        "linguagens",
        "total_issues",
        "issues_abertas",
        "issues_fechadas",
        "razao_issues_fechadas",
        "media_prs_aceitas_linguagem",
        "media_releases_linguagem",
        "media_dias_desde_atualizacao_linguagem",
    ]

    CSV_MISSING_VALUE = ""

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

    def getTopRepositories(self, target_count=1000, page_size=50, delay_between_pages=1.0,
                            min_page_size=1, checkpoint_file="checkpoint_repos.json"):
        all_repos = []
        seen = set()
        cursor = None
        has_next_page = True

        if checkpoint_file and os.path.exists(checkpoint_file):
            with open(checkpoint_file, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            all_repos = checkpoint.get("repos", [])
            cursor = checkpoint.get("cursor")
            seen = {repo.get("nameWithOwner") for repo in all_repos if repo.get("nameWithOwner")}
            print(f"Retomando checkpoint: {len(all_repos)} repositórios já coletados anteriormente.")

        while has_next_page and len(all_repos) < target_count:
            remaining = target_count - len(all_repos)
            current_page_size = min(page_size, remaining)
            data = None

            while True:
                payload = {
                    "query": GithubClient.SEARCH_QUERY,
                    "variables": {
                        "searchQuery": "stars:>1 sort:stars-desc",
                        "first": current_page_size,
                        "cursor": cursor
                    }
                }
                data = self._post_with_retry(payload)
                if data is not None or current_page_size <= min_page_size:
                    break
                current_page_size = max(current_page_size // 2, min_page_size)
                print(f"Página falhou repetidamente. Tentando novamente com página menor ({current_page_size})...")

            if data is None:
                print("Falha ao obter página mesmo após reduzir o tamanho. Interrompendo coleta.")
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

            if checkpoint_file:
                with open(checkpoint_file, "w", encoding="utf-8") as f:
                    json.dump({"repos": all_repos, "cursor": cursor}, f, ensure_ascii=False)

            print(f"Coletados: {len(all_repos)}/{target_count}")

            if has_next_page and len(all_repos) < target_count:
                time.sleep(delay_between_pages)

        if checkpoint_file and len(all_repos) >= target_count and os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)

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

    def getOpenIssuesCount(self, repo):
        total = (repo.get("totalIssues") or {}).get("totalCount")
        closed = (repo.get("closedIssues") or {}).get("totalCount")
        if total is None or closed is None:
            return None
        return total - closed

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

    def buildCsvRow(self, repo, metrics_by_language=None):
        missing = GithubClient.CSV_MISSING_VALUE
        metrics_by_language = metrics_by_language or {}

        idade = self.getRepositoryAge(repo)
        atualizacao = self.getDaysSinceLastUpdate(repo)
        ratio = self.getClosedIssuesRatio(repo)

        total_issues = (repo.get("totalIssues") or {}).get("totalCount")
        closed_issues = (repo.get("closedIssues") or {}).get("totalCount")
        open_issues = self.getOpenIssuesCount(repo)
        total_prs = (repo.get("totalPullRequests") or {}).get("totalCount")
        merged_prs = (repo.get("mergedPullRequests") or {}).get("totalCount")
        releases = self.getReleaseCount(repo)

        language_nodes = (repo.get("languages") or {}).get("nodes") or []
        language_names = [node.get("name") for node in language_nodes if node and node.get("name")]
        primary_language = language_names[0] if language_names else None
        languages_joined = ", ".join(language_names) if language_names else None
        language_stats = metrics_by_language.get(self.getRepoLanguages(repo).get("primary"))

        def fallback(value):
            return value if value is not None else missing

        return {
            "nome_repositorio": fallback(repo.get("nameWithOwner")),
            "url": fallback(repo.get("url")),
            "estrelas": fallback(repo.get("stargazerCount")),
            "data_criacao": fallback(idade.get("data_criacao")) if idade else missing,
            "idade_em_dias": fallback(idade.get("idade_em_dias")) if idade else missing,
            "idade_em_anos": fallback(idade.get("idade_em_anos")) if idade else missing,
            "total_pull_requests": fallback(total_prs),
            "total_pull_requests_aceitas": fallback(merged_prs),
            "total_releases": fallback(releases),
            "data_ultima_atualizacao": fallback(atualizacao.get("ultima_atualizacao")) if atualizacao else missing,
            "dias_desde_ultima_atualizacao": fallback(atualizacao.get("dias_desde_atualizacao")) if atualizacao else missing,
            "linguagem_primaria": fallback(primary_language),
            "linguagens": fallback(languages_joined),
            "total_issues": fallback(total_issues),
            "issues_abertas": fallback(open_issues),
            "issues_fechadas": fallback(closed_issues),
            "razao_issues_fechadas": fallback(ratio),
            "media_prs_aceitas_linguagem": fallback(language_stats.get("avg_merged_prs")) if language_stats else missing,
            "media_releases_linguagem": fallback(language_stats.get("avg_releases")) if language_stats else missing,
            "media_dias_desde_atualizacao_linguagem": fallback(language_stats.get("avg_days_since_update")) if language_stats else missing,
        }

    def exportRepositoriesToCsv(self, repositories, filename="repositorios_1000.csv"):
        metrics_by_language = self.getMetricsByLanguage(repositories)

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=GithubClient.CSV_FIELDNAMES)
            writer.writeheader()
            for repo in repositories:
                writer.writerow(self.buildCsvRow(repo, metrics_by_language))

        return filename
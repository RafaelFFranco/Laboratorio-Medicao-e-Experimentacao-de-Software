import json
from traceback import print_tb

from GithubClient import GithubClient

def main():
    client = GithubClient()
    repositories = client.getTopRepositories()

    if repositories:
        with open("top100.json", "w", encoding="utf-8") as f:
            json.dump(repositories, f, indent=2, ensure_ascii=False)
        print(f"{len(repositories)} repositórios salvos em top100.json\n")

        for repo in repositories:
            name = repo.get("nameWithOwner")
            releases = client.getReleaseCount(repo)
            update_info = client.getDaysSinceLastUpdate(repo)
            ratio = client.getClosedIssuesRatio(repo)
            totalPRs = client.getTotalPullRequestsAceitos(  repo)


            print(f"=== Repositório: {name} ===")
            print(f"Total de Releases: {releases}")

            if update_info:
                print(f"Última Atualização: {update_info['ultima_atualizacao']} ({update_info['dias_desde_atualizacao']} dias atrás)")
            else:
                print("Última Atualização: Sem informação")

            if ratio is not None:
                print(f"Razão de Issues Fechadas: {ratio:.2%}")
            else:
                print("Razão de Issues Fechadas: N/A (sem issues)")

            if totalPRs is not None:
                print(f"Total de PRs: {totalPRs}")
            else:
                print("Total de PRs: N/A (sem PRs)")

            print("-" * 40)

if __name__ == "__main__":
    main()
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
            totalPRsAceitos = client.getTotalPullRequestsAceitos(repo)
            idadeRepo = client.getRepositoryAge(repo)
            languages = client.getRepoLanguages(repo)


            print(f"=== Repositório: {name} ===")
            print(f"Total de Releases: {releases}")

            if idadeRepo is not None:
                print(f"Data Criação: {idadeRepo.get('data_criacao')}")
                print(f"Idade em anos: {idadeRepo.get('idade_em_anos')} anos")
                print(f"Idade em dias: {idadeRepo.get('idade_em_dias')} dias")
            else:
                print("Idade: N/A")

            if update_info:
                print(f"Última Atualização: {update_info['ultima_atualizacao']} ({update_info['dias_desde_atualizacao']} dias atrás)")
            else:
                print("Última Atualização: Sem informação")

            print(f"Linguagem Primária: {languages.get('primary')}")
            print(f"Linguages do Repositório: {languages.get('languages')}")

            if ratio is not None:
                print(f"Razão de Issues Fechadas: {ratio:.2%}")
            else:
                print("Razão de Issues Fechadas: N/A (sem issues)")

            print(f"Total de PRs Fechados: {totalPRsAceitos}")


            print("-" * 40)

if __name__ == "__main__":
    main()
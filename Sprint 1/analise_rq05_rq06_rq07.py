import csv
from collections import Counter
import statistics

# Carregar dados
data = []
with open('repositorios_1000.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

print("=" * 80)
print("ANÁLISE RQ05, RQ06 E RQ07 - HIPÓTESES INFORMAIS")
print("=" * 80)

# RQ05: Linguagem Primária
print("\n### RQ05: Sistemas populares são escritos nas linguagens mais populares?")
print("\nDistribuição de Linguagens Primárias:")

langs = {}
sem_linguagem = 0
for repo in data:
    lang = repo['linguagem_primaria'].strip()
    if lang == '' or lang == 'None':
        sem_linguagem += 1
    else:
        langs[lang] = langs.get(lang, 0) + 1

sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)
for i, (lang, count) in enumerate(sorted_langs[:15]):
    pct = (count / len(data)) * 100
    print(f"  {i+1}. {lang}: {count} ({pct:.1f}%)")

print(f"\nTotal de linguagens únicas: {len(langs)}")
print(f"Repositórios sem linguagem primária: {sem_linguagem}")

top_5_count = sum([count for _, count in sorted_langs[:5]])
top_5_pct = (top_5_count / len(data)) * 100
print(f"Top 5 linguagens correspondem a: {top_5_pct:.1f}% dos repositórios")

# RQ06: Razão Issues Fechadas
print("\n" + "=" * 80)
print("### RQ06: Sistemas populares possuem alto % de issues fechadas?")
print("\nEstatísticas de Razão Issues Fechadas:")

ratios = []
sem_issues = 0
for repo in data:
    ratio_str = repo['razao_issues_fechadas'].strip()
    if ratio_str == '' or ratio_str == 'None':
        sem_issues += 1
    else:
        try:
            ratio = float(ratio_str)
            ratios.append(ratio)
        except:
            sem_issues += 1

print(f"Total de repositórios: {len(data)}")
print(f"Repositórios com razão calculada: {len(ratios)}")
print(f"Repositórios SEM issues: {sem_issues}")

if ratios:
    ratios_sorted = sorted(ratios)
    median = statistics.median(ratios_sorted)
    mean = statistics.mean(ratios)

    print(f"\nEstatísticas (apenas repos com issues):")
    print(f"  Mediana: {median:.4f} ({median*100:.2f}%)")
    print(f"  Média: {mean:.4f} ({mean*100:.2f}%)")
    print(f"  Mín: {min(ratios):.4f} ({min(ratios)*100:.2f}%)")
    print(f"  Máx: {max(ratios):.4f} ({max(ratios)*100:.2f}%)")

    # Percentis
    n = len(ratios_sorted)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    print(f"  Q1 (25%): {ratios_sorted[q1_idx]:.4f}")
    print(f"  Q3 (75%): {ratios_sorted[q3_idx]:.4f}")

    # Distribuição
    print("\nDistribuição de Razão Issues Fechadas:")
    ranges = {
        '0-25%': 0,
        '25-50%': 0,
        '50-75%': 0,
        '75-90%': 0,
        '90-100%': 0
    }
    for ratio in ratios:
        if ratio < 0.25:
            ranges['0-25%'] += 1
        elif ratio < 0.50:
            ranges['25-50%'] += 1
        elif ratio < 0.75:
            ranges['50-75%'] += 1
        elif ratio < 0.90:
            ranges['75-90%'] += 1
        else:
            ranges['90-100%'] += 1

    for range_name, count in ranges.items():
        pct = (count / len(ratios)) * 100
        print(f"  {range_name}: {count} ({pct:.1f}%)")

# RQ07: Métricas por Linguagem
print("\n" + "=" * 80)
print("### RQ07: Linguagens populares recebem mais contribuição/releases/atualização?")
print("\nMétricas por Linguagem (Top 10):")

top_langs = [lang for lang, _ in sorted_langs[:10]]
print(f"\n{'Linguagem':<20} {'Repos':<6} {'Média PRs':<12} {'Média Releases':<15} {'Média Dias Update':<15}")
print("-" * 70)

for lang in top_langs:
    repos_com_lang = [r for r in data if r['linguagem_primaria'].strip() == lang]
    if repos_com_lang:
        media_prs = repos_com_lang[0]['media_prs_aceitas_linguagem'].strip()
        media_releases = repos_com_lang[0]['media_releases_linguagem'].strip()
        media_dias = repos_com_lang[0]['media_dias_desde_atualizacao_linguagem'].strip()

        print(f"{lang:<20} {len(repos_com_lang):<6} {media_prs:<12} {media_releases:<15} {media_dias:<15}")

print("\n" + "=" * 80)

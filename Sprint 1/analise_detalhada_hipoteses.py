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
print("ANÁLISE DETALHADA PARA HIPÓTESES REFINADAS")
print("=" * 80)

# === RQ05: Linguagens com referência externa ===
print("\n### RQ05: DISTRIBUIÇÃO DE LINGUAGENS (com contexto)")
langs = {}
sem_linguagem = 0
for repo in data:
    lang = repo['linguagem_primaria'].strip()
    if lang == '' or lang == 'None':
        sem_linguagem += 1
    else:
        langs[lang] = langs.get(lang, 0) + 1

sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)

print("\nTop 10 Linguagens:")
for i, (lang, count) in enumerate(sorted_langs[:10]):
    pct = (count / len(data)) * 100
    print(f"  {i+1}. {lang:<15} {count:>4} repos ({pct:>5.1f}%)")

print(f"\nRepos sem linguagem primária: {sem_linguagem} ({sem_linguagem/len(data)*100:.1f}%)")
print(f"Total de linguagens únicas: {len(langs)}")

# Concentração
top_1 = sorted_langs[0][1] / len(data) * 100
top_5 = sum([c for _, c in sorted_langs[:5]]) / len(data) * 100
top_10 = sum([c for _, c in sorted_langs[:10]]) / len(data) * 100
print(f"\nConcentração:")
print(f"  Linguagem #1 (JavaScript): {top_1:.1f}%")
print(f"  Top 5 linguagens: {top_5:.1f}%")
print(f"  Top 10 linguagens: {top_10:.1f}%")
print(f"  Cauda (resto): {100 - top_10:.1f}%")

# === RQ06: Issues - análise bivariada ===
print("\n" + "=" * 80)
print("### RQ06: RAZÃO ISSUES FECHADAS (análise profunda)")

ratios = []
totals_issues = []
repos_sem_issues = []

for repo in data:
    ratio_str = repo['razao_issues_fechadas'].strip()
    total_str = repo['total_issues'].strip()

    try:
        total = int(total_str) if total_str else 0
        totals_issues.append(total)

        if ratio_str == '' or ratio_str == 'None' or total == 0:
            repos_sem_issues.append(repo['nome_repositorio'])
        else:
            ratio = float(ratio_str)
            ratios.append((ratio, total))
    except:
        pass

print(f"\nRepositórios SEM issues: {len(repos_sem_issues)} ({len(repos_sem_issues)/len(data)*100:.1f}%)")
print(f"Repositórios COM issues: {len(ratios)}")

if ratios:
    ratio_values = [r for r, _ in ratios]
    ratio_sorted = sorted(ratio_values)

    print(f"\nEstatísticas da RAZÃO (repos com issues):")
    print(f"  Mediana: {statistics.median(ratio_sorted):.4f} ({statistics.median(ratio_sorted)*100:.2f}%)")
    print(f"  Média: {statistics.mean(ratio_values):.4f} ({statistics.mean(ratio_values)*100:.2f}%)")
    print(f"  Desvio padrão: {statistics.stdev(ratio_values):.4f}")

    # Percentis
    n = len(ratio_sorted)
    p25 = ratio_sorted[n // 4]
    p75 = ratio_sorted[(3 * n) // 4]
    print(f"  P25: {p25:.4f}  |  P75: {p75:.4f}")

# Quantidade de issues
print(f"\nEstatísticas da QUANTIDADE de issues (todos repos):")
print(f"  Repos com 0 issues: {sum(1 for t in totals_issues if t == 0)}")
print(f"  Repos com 1-10 issues: {sum(1 for t in totals_issues if 1 <= t <= 10)}")
print(f"  Repos com 11-100 issues: {sum(1 for t in totals_issues if 11 <= t <= 100)}")
print(f"  Repos com 100+ issues: {sum(1 for t in totals_issues if t > 100)}")

valid_totals = [t for t in totals_issues if t > 0]
if valid_totals:
    print(f"\n  Mediana (repos com issues): {statistics.median(valid_totals):.0f}")
    print(f"  Média (repos com issues): {statistics.mean(valid_totals):.0f}")
    print(f"  Máximo: {max(valid_totals)}")

# === RQ07: Análise de confounding variables ===
print("\n" + "=" * 80)
print("### RQ07: IDADE vs LINGUAGEM vs ATIVIDADE")

# Extrair idade dos repos por linguagem
lang_stats = {}
for repo in data:
    lang = repo['linguagem_primaria'].strip()
    if lang and lang != 'None':
        idade_str = repo['idade_em_anos'].strip()
        prs_str = repo['media_prs_aceitas_linguagem'].strip()
        releases_str = repo['media_releases_linguagem'].strip()
        dias_update_str = repo['media_dias_desde_atualizacao_linguagem'].strip()

        try:
            idade = float(idade_str) if idade_str else None
            prs = float(prs_str) if prs_str else None
            releases = float(releases_str) if releases_str else None
            dias_update = float(dias_update_str) if dias_update_str else None

            if lang not in lang_stats:
                lang_stats[lang] = {
                    'idades': [],
                    'prs': [],
                    'releases': [],
                    'dias_update': []
                }

            if idade:
                lang_stats[lang]['idades'].append(idade)
            if prs:
                lang_stats[lang]['prs'].append(prs)
            if releases:
                lang_stats[lang]['releases'].append(releases)
            if dias_update:
                lang_stats[lang]['dias_update'].append(dias_update)
        except:
            pass

print("\nTop 10 Linguagens - Idade Média dos Repos:")
print(f"{'Linguagem':<20} {'Idade (anos)':<15} {'Repos':<8} {'PRs média':<12} {'Dias update':<12}")
print("-" * 80)

top_langs = sorted(sorted_langs, key=lambda x: x[1], reverse=True)[:10]
for lang, count in top_langs:
    if lang in lang_stats and lang_stats[lang]['idades']:
        idade_media = statistics.mean(lang_stats[lang]['idades'])
        prs_media = statistics.mean(lang_stats[lang]['prs']) if lang_stats[lang]['prs'] else 0
        dias_media = statistics.mean(lang_stats[lang]['dias_update']) if lang_stats[lang]['dias_update'] else 0
        print(f"{lang:<20} {idade_media:<15.2f} {count:<8} {prs_media:<12.0f} {dias_media:<12.1f}")

print("\n" + "=" * 80)
print("OBSERVAÇÕES CRÍTICAS:")
print("- Linguagens 'novas' (Rust, TypeScript) vs 'antigas' (Java, Python) têm idades diferentes?")
print("- A atividade (dias_update) está correlacionada com IDADE ou com LINGUAGEM?")
print("- As médias estão enviesadas por outliers? (Verificar mediana também)")
print("=" * 80)

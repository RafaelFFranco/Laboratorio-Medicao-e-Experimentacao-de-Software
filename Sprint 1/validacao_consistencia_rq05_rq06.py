import csv
from collections import Counter
import statistics

# Carregar dados
data = []
with open('repositorios_1000.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

print("=" * 90)
print("VALIDAÇÃO DE CONSISTÊNCIA DOS DADOS — RQ05 e RQ06")
print("=" * 90)

# ============================================================================
# RQ05: LINGUAGEM PRIMÁRIA - VALIDAÇÃO DE CONSISTÊNCIA
# ============================================================================

print("\n" + "=" * 90)
print("RQ05: LINGUAGEM PRIMÁRIA - VALIDAÇÃO DE CONSISTÊNCIA")
print("=" * 90)

print("\n### 1. DISTRIBUIÇÃO DE VALORES")
langs = {}
sem_linguagem = []
linguagens_suspeitas = []

for i, repo in enumerate(data):
    lang = repo['linguagem_primaria'].strip()
    if lang == '' or lang == 'None' or lang is None:
        sem_linguagem.append((i+1, repo['nome_repositorio']))
    else:
        langs[lang] = langs.get(lang, 0) + 1
        # Detectar linguagens suspeitas (muito curtas, números, caracteres especiais)
        if len(lang) < 2 or any(c.isdigit() for c in lang) or any(c in lang for c in '@#$%'):
            linguagens_suspeitas.append((lang, repo['nome_repositorio']))

sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)

print(f"\nTotal de repositórios analisados: {len(data)}")
print(f"Repositórios com linguagem identificada: {len(langs)}")
print(f"Repositórios SEM linguagem primária: {len(sem_linguagem)} ({len(sem_linguagem)/len(data)*100:.2f}%)")
print(f"Total de linguagens únicas: {len(langs)}")

print(f"\nDistribuição (Top 20):")
for i, (lang, count) in enumerate(sorted_langs[:20]):
    pct = (count / len(data)) * 100
    print(f"  {i+1:2d}. {lang:<20} {count:>4} repos ({pct:>6.2f}%)")

# Edge cases
print(f"\n### 2. EDGE CASES E ANOMALIAS")

if sem_linguagem:
    print(f"\n⚠️  Repositórios SEM linguagem primária ({len(sem_linguagem)}):")
    for idx, repo_name in sem_linguagem[:10]:  # Mostrar apenas 10 primeiros
        print(f"  - Linha {idx}: {repo_name}")
    if len(sem_linguagem) > 10:
        print(f"  ... e mais {len(sem_linguagem) - 10}")

if linguagens_suspeitas:
    print(f"\n⚠️  Linguagens suspeitas (muito curtas ou caracteres especiais):")
    for lang, repo_name in linguagens_suspeitas[:5]:
        print(f"  - '{lang}' em {repo_name}")

# Distribuição por tamanho
print(f"\n### 3. DISTRIBUIÇÃO POR TAMANHO")
distrib = {
    '1 repo': sum(1 for _, c in sorted_langs if c == 1),
    '2-5 repos': sum(1 for _, c in sorted_langs if 2 <= c <= 5),
    '6-20 repos': sum(1 for _, c in sorted_langs if 6 <= c <= 20),
    '21-100 repos': sum(1 for _, c in sorted_langs if 21 <= c <= 100),
    '100+ repos': sum(1 for _, c in sorted_langs if c > 100)
}

print("\nQuantas linguagens têm X repositórios:")
for faixa, count in distrib.items():
    print(f"  {faixa:<15}: {count:>3} linguagens")

# ============================================================================
# RQ06: RAZÃO ISSUES FECHADAS - VALIDAÇÃO DE CONSISTÊNCIA
# ============================================================================

print("\n" + "=" * 90)
print("RQ06: RAZÃO ISSUES FECHADAS - VALIDAÇÃO DE CONSISTÊNCIA")
print("=" * 90)

print("\n### 1. DADOS BRUTOS")

ratios_valid = []
repos_sem_issues = []
repos_com_zero_fechadas = []
valores_invalidos = []
valores_nulos = 0

for i, repo in enumerate(data):
    ratio_str = repo['razao_issues_fechadas'].strip()
    total_str = repo['total_issues'].strip()
    closed_str = repo['issues_fechadas'].strip()

    if ratio_str == '' or ratio_str == 'None':
        valores_nulos += 1
        try:
            total = int(total_str) if total_str else 0
            closed = int(closed_str) if closed_str else 0
            if total == 0:
                repos_sem_issues.append((i+1, repo['nome_repositorio'], total, closed))
            elif closed == 0 and total > 0:
                repos_com_zero_fechadas.append((i+1, repo['nome_repositorio'], total, closed))
        except:
            pass
    else:
        try:
            ratio = float(ratio_str)
            # Validar se ratio está entre 0 e 1
            if ratio < 0 or ratio > 1:
                valores_invalidos.append((ratio, repo['nome_repositorio']))
            else:
                ratios_valid.append((ratio, int(total_str) if total_str else 0, repo['nome_repositorio']))
        except ValueError:
            valores_invalidos.append((ratio_str, repo['nome_repositorio']))

print(f"Total de repositórios: {len(data)}")
print(f"Repositórios com razão calculada: {len(ratios_valid)}")
print(f"Repositórios com valor nulo/vazio: {valores_nulos}")
print(f"Repositórios SEM issues (total=0): {len(repos_sem_issues)}")
print(f"Repositórios com 0 issues FECHADAS (mas total>0): {len(repos_com_zero_fechadas)}")
print(f"Valores inválidos ou fora do intervalo [0,1]: {len(valores_invalidos)}")

# Edge cases detalhados
if repos_sem_issues:
    print(f"\n⚠️  Repositórios SEM issues (total_issues = 0) — {len(repos_sem_issues)}:")
    for idx, repo_name, total, closed in repos_sem_issues[:5]:
        print(f"  - Linha {idx}: {repo_name} (total={total}, fechadas={closed})")
    if len(repos_sem_issues) > 5:
        print(f"  ... e mais {len(repos_sem_issues) - 5}")

if repos_com_zero_fechadas:
    print(f"\n⚠️  Repositórios com 0 issues FECHADAS (mas total>0) — {len(repos_com_zero_fechadas)}:")
    for idx, repo_name, total, closed in repos_com_zero_fechadas[:5]:
        print(f"  - Linha {idx}: {repo_name} (total={total}, fechadas={closed})")
    if len(repos_com_zero_fechadas) > 5:
        print(f"  ... e mais {len(repos_com_zero_fechadas) - 5}")

if valores_invalidos:
    print(f"\n⚠️  Valores inválidos/fora do intervalo [0,1] — {len(valores_invalidos)}:")
    for val, repo_name in valores_invalidos[:3]:
        print(f"  - {repo_name}: razão = {val}")

# Estatísticas robustas
print(f"\n### 2. ESTATÍSTICAS (repos com issues válidas)")

if ratios_valid:
    ratio_values = [r for r, _, _ in ratios_valid]
    ratio_sorted = sorted(ratio_values)

    print(f"\nMédidas Centrais:")
    print(f"  Mínimo: {min(ratio_values):.4f} ({min(ratio_values)*100:.2f}%)")
    print(f"  Mediana: {statistics.median(ratio_sorted):.4f} ({statistics.median(ratio_sorted)*100:.2f}%)")
    print(f"  Média: {statistics.mean(ratio_values):.4f} ({statistics.mean(ratio_values)*100:.2f}%)")
    print(f"  Máximo: {max(ratio_values):.4f} ({max(ratio_values)*100:.2f}%)")

    print(f"\nDisperção:")
    print(f"  Desvio Padrão: {statistics.stdev(ratio_values):.4f}")
    print(f"  Variância: {statistics.variance(ratio_values):.4f}")

    # Percentis
    n = len(ratio_sorted)
    p10_idx = max(0, n // 10)
    p25_idx = n // 4
    p75_idx = (3 * n) // 4
    p90_idx = min(n - 1, (9 * n) // 10)

    print(f"\nPercentis:")
    print(f"  P10: {ratio_sorted[p10_idx]:.4f} ({ratio_sorted[p10_idx]*100:.2f}%)")
    print(f"  P25: {ratio_sorted[p25_idx]:.4f} ({ratio_sorted[p25_idx]*100:.2f}%)")
    print(f"  P75: {ratio_sorted[p75_idx]:.4f} ({ratio_sorted[p75_idx]*100:.2f}%)")
    print(f"  P90: {ratio_sorted[p90_idx]:.4f} ({ratio_sorted[p90_idx]*100:.2f}%)")

    # Detecção de outliers (IQR method)
    q1 = ratio_sorted[n // 4]
    q3 = ratio_sorted[(3 * n) // 4]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = [r for r in ratio_values if r < lower_bound or r > upper_bound]
    print(f"\nOutliers (método IQR):")
    print(f"  Limite inferior: {lower_bound:.4f}")
    print(f"  Limite superior: {upper_bound:.4f}")
    print(f"  Total de outliers: {len(outliers)} ({len(outliers)/len(ratio_values)*100:.2f}%)")

    if outliers:
        outliers_sorted = sorted(outliers)
        print(f"  Valores: {[f'{v:.4f}' for v in outliers_sorted[:10]]}")

### 3. DISTRIBUIÇÃO
print(f"\n### 3. DISTRIBUIÇÃO POR FAIXA")

ranges = {
    '0-10%': 0,
    '10-25%': 0,
    '25-50%': 0,
    '50-75%': 0,
    '75-90%': 0,
    '90-100%': 0,
    '100% (perfeito)': 0
}

for ratio in ratio_values:
    if ratio < 0.10:
        ranges['0-10%'] += 1
    elif ratio < 0.25:
        ranges['10-25%'] += 1
    elif ratio < 0.50:
        ranges['25-50%'] += 1
    elif ratio < 0.75:
        ranges['50-75%'] += 1
    elif ratio < 0.90:
        ranges['75-90%'] += 1
    elif ratio < 1.0:
        ranges['90-100%'] += 1
    else:  # ratio == 1.0
        ranges['100% (perfeito)'] += 1

print("\nDistribuição de razão de issues fechadas:")
for faixa, count in ranges.items():
    pct = (count / len(ratio_values)) * 100
    bar = '█' * int(pct / 2)  # Barra visual
    print(f"  {faixa:<20}: {count:>4} repos ({pct:>6.2f}%) {bar}")

# Análise de quantidade de issues
print(f"\n### 4. VALIDAÇÃO DE QUANTIDADE DE ISSUES")

total_issues_values = []
for r, total, _ in ratios_valid:
    total_issues_values.append(total)

print(f"\nTotal de issues (repos com ratio válida):")
print(f"  Mínimo: {min(total_issues_values)}")
print(f"  Mediana: {statistics.median(sorted(total_issues_values))}")
print(f"  Média: {statistics.mean(total_issues_values):.0f}")
print(f"  Máximo: {max(total_issues_values)}")

# Repos com pouquíssimas issues (1-5)
repos_poucas_issues = [repo for ratio, total, repo in ratios_valid if total <= 5]
print(f"\nRepositórios com ≤5 issues totais: {len(repos_poucas_issues)}")
if repos_poucas_issues:
    print(f"  Exemplos: {repos_poucas_issues[:5]}")

print("\n" + "=" * 90)
print("FIM DA VALIDAÇÃO")
print("=" * 90)

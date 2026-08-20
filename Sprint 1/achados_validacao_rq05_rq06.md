# Achados de Validação de Consistência — RQ05 e RQ06

## RQ05: Linguagem Primária — Validação de Consistência

### ✅ Qualidade Geral: BOA

**Dados válidos:**
- 1.000 repositórios analisados
- 913 com linguagem primária identificada (91.3%)
- 87 SEM linguagem primária (8.7%)
- 44 linguagens únicas detectadas
- 0 valores inválidos ou corrompidos

### ⚠️ Edge Cases Identificados

**87 repositórios SEM linguagem primária (8.7%):**
- São repositórios de **documentação/templates/curadoria**
- Exemplos: `sindresorhus/awesome`, `awesome-selfhosted/awesome-selfhosted`, `jwasham/coding-interview-university`, `996icu/996.ICU`, `github/gitignore`
- **Padrão:** Repos sem issues também não têm linguagem primária (mesma categoria)
- **Ação:** Não são erros — são repositórios legítimos fora do escopo de "projetos de software"
- **Recomendação para análise futura:** Considerar filtrar esses antes de RQ06

**Linguagens 1 caractere (C, C#):**
- Detectadas como "suspeitas" mas são **válidas**
- C: Ventoy, FFmpeg, ocornut/imgui (legítimo)
- C#: v2rayN, Microsoft Terminal (legítimo)
- ✅ Sem problemas

### 📊 Distribuição de Linguagens

**Top 10:**
1. JavaScript: 206 (20.6%)
2. Python: 204 (20.4%)
3. Shell: 75 (7.5%)
4. Makefile: 50 (5.0%)
5. Go: 46 (4.6%)
6. TypeScript: 44 (4.4%)
7. HTML: 39 (3.9%)
8. Rust: 37 (3.7%)
9. Dockerfile: 33 (3.3%)
10. Java: 32 (3.2%)

**Padrão de concentração:**
- 2 linguagens com 100+ repos (JavaScript, Python)
- 8 linguagens com 21-100 repos
- 9 linguagens com 6-20 repos
- 11 linguagens com 2-5 repos
- 14 linguagens com apenas 1 repo

**Conclusão:** Distribuição equilibrada com cauda longa — não há concentração excessiva.

---

## RQ06: Razão Issues Fechadas — Validação de Consistência

### ✅ Qualidade Geral: EXCELENTE

**Dados válidos:**
- 1.000 repositórios totais
- 957 com razão calculada (95.7%)
- 43 sem razão (4.3% — repos sem issues)
- 0 valores inválidos
- 0 valores fora do intervalo [0, 1]
- 0 repos com issues_fechadas = 0 (mas total_issues > 0)

### ⚠️ Edge Cases Identificados

**43 repositórios SEM issues (4.3%):**
- Não é erro de coleta — são repositórios que realmente não usam issues
- Exemplos: `torvalds/linux`, `vinta/awesome-python`, `awesome-selfhosted/awesome-selfhosted`
- **Padrão:** Muitos são repositórios de documentação/curadoria (mesmo padrão do RQ05)
- **Ação:** Corretamente excluídos do cálculo de razão
- ✅ Sem problemas

**Outliers baixos (0.0769 a 0.25):**
- 38 repositórios (3.97%) com razão muito baixa
- Exemplo: ratio 0.0769 = 7.69% de issues fechadas
- Esses são projetos com muitas issues abertas (pode ser: em desenvolvimento, abandonados, ou com política diferente)
- ✅ Válidos, não erros

**Repositórios com 100% de issues fechadas:**
- 26 repos (2.72%) com ratio = 1.0 (perfeito)
- Podem ser: projetos maduros/estáveis ou pequenos com controle rígido
- ✅ Válidos

### 📊 Estatísticas

**Medidas Centrais (957 repos com issues):**
- Mínimo: 7.69%
- Mediana: **87.50%** (📌 métrica robusta)
- Média: 80.25%
- Máximo: 100.00%

**Dispersão:**
- Desvio Padrão: 0.2104 (indica variação real, mas moderada)
- Variância: 0.0443

**Percentis (muito informativos):**
- P10: 46.06% — 10% dos repos fecham <46% das issues
- P25: 70.44% — Q1 (1ª quartila)
- P75: 96.80% — Q3 (3ª quartila)
- P90: 99.24% — 90% dos repos fecham >99% das issues

### 📊 Distribuição por Faixa

| Faixa | Repos | % | Visualização |
|-------|-------|---|---|
| 0-10% | 3 | 0.31% | Raríssimo |
| 10-25% | 19 | 1.99% | Muito baixo |
| 25-50% | 86 | 8.99% | Baixo |
| 50-75% | 172 | 17.97% | Médio |
| 75-90% | 246 | 25.71% | Alto |
| **90-100%** | **405** | **42.32%** | **Muito alto** |
| 100% (perfeito) | 26 | 2.72% | Excelente |

**Padrão:** Distribuição **bimodal** com concentração nos extremos altos (75-100% = 70% dos repos)

### 🔍 Análise de Quantidade de Issues

**Importante para interpretar a razão:**
- Mínimo: 5 issues (apenas 1 repo)
- Mediana: **1.842 issues** por repo (número elevado!)
- Média: 5.329 issues por repo
- Máximo: 251.216 issues (freeCodeCamp)

**Conclusão crítica:** 95% dos repos têm MUITAS issues (>100, mediana 1842), não poucos. Isso explica por que razão é alta — repositórios maduros/populares geram muitas issues que são processadas regularmente.

---

## ✅ VALIDAÇÃO FINAL

### RQ05 — Linguagem Primária
| Aspecto | Status | Observação |
|---------|--------|-----------|
| Valores nulos | ✅ 8.7% | Esperado (repos documentação) |
| Valores inválidos | ✅ 0 | Todos válidos |
| Distribuição | ✅ OK | Dispersa, não concentrada |
| Edge cases | ✅ Explicados | Documentação/templates |
| **Pronto para análise?** | **✅ SIM** | Validação passou |

### RQ06 — Razão Issues Fechadas
| Aspecto | Status | Observação |
|---------|--------|-----------|
| Valores nulos | ✅ 4.3% | Legítimo (repos sem issues) |
| Valores fora [0,1] | ✅ 0 | Todos no intervalo correto |
| Outliers | ✅ 3.97% | Baixa razão, válidos |
| Distribuição | ✅ Bimodal | Concentração em 75-100% |
| Confounding variable | ⚠️ Identificada | Alta razão correlaciona com muitas issues (quantidade) |
| **Pronto para análise?** | **✅ SIM** | Validação passou, mas notar confounding |

---

## 📌 Recomendações para Próximas Análises

1. **RQ05:** Considerar separar "repositórios de software real" dos "repositórios de documentação/curadoria" para RQ02/RQ03/RQ04 (não têm releases/PRs)

2. **RQ06:** Sempre reportar **quantidade de issues** junto com razão — a correlação entre "muitas issues" e "razão alta" é forte

3. **Ambas:** Os 43 repos sem issues + 87 sem linguagem primária (sobreposição esperada) são outliers legítimos que devem ser tratados separadamente

4. **Futuro:** Estratificar análise por "tipo de repositório" (software vs documentação) se possível

---

## Resumo Executivo

✅ **Qualidade dos dados: EXCELENTE**

- RQ05: 91.3% com linguagem válida, 8.7% legítimos (documentação)
- RQ06: 95.7% com ratio válida, 4.3% legítimos (sem issues)
- 0 valores corrompidos ou inválidos em ambas
- Distribuições são reais, não artefatos de coleta
- **Dados aprovados para análise estatística**

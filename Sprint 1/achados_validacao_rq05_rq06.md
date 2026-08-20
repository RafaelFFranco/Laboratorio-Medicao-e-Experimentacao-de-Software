# Achados de Validação de Consistência — RQ05 e RQ06

## RQ05: Linguagem Primária

### Qualidade dos Dados:  EXCELENTE

| Métrica | Valor |
|---------|-------|
| Repositórios com linguagem válida | 913 (91.3%) |
| Repositórios SEM linguagem | 87 (8.7%) |
| Linguagens únicas | 44 |
| Valores inválidos | 0 |

**Top 10 Linguagens:**
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

### Edge Cases

**87 repositórios sem linguagem primária (8.7%):**
- Tipo: Documentação/templates/curadoria (sindresorhus/awesome, github/gitignore, coding-interview-university)
- Válidos?  Sim — são repositórios legítimos fora do escopo "software real"
- Recomendação: Separar para análises futuras se necessário

**Distribuição equilibrada:**
- 2 linguagens com 100+ repos
- 8 linguagens com 21-100 repos
- 9 linguagens com 6-20 repos
- 11 linguagens com 2-5 repos
- 14 linguagens com 1 repo

**Conclusão:** Dados válidos, sem erros de coleta.
---

## RQ06: Razão Issues Fechadas

### Qualidade dos Dados:  EXCELENTE

| Métrica | Valor |
|---------|-------|
| Repositórios com ratio válida | 957 (95.7%) |
| Repositórios SEM issues | 43 (4.3%) |
| Valores fora [0,1] | 0 |
| Valores inválidos | 0 |

### Estatísticas (957 repos com issues)

| Métrica | Valor |
|---------|-------|
| Mínimo | 7.69% |
| **Mediana** | **87.50%** |
| Média | 80.25% |
| Máximo | 100% |
| Desvio Padrão | 0.2104 |

**Percentis:**
- P10: 46.06% | P25: 70.44% | P75: 96.80% | P90: 99.24%

### Distribuição

| Faixa | Repos | % |
|-------|-------|---|
| 0-10% | 3 | 0.31% |
| 10-25% | 19 | 1.99% |
| 25-50% | 86 | 8.99% |
| 50-75% | 172 | 17.97% |
| 75-90% | 246 | 25.71% |
| **90-100%** | **405** | **42.32%** |
| 100% (perfeito) | 26 | 2.72% |

**Padrão:** Distribuição bimodal com concentração nos extremos altos (70% com 75-100%)

### Edge Cases

**43 repositórios SEM issues (4.3%):**
- Tipo: Documentação/templates (torvalds/linux, vinta/awesome-python)
- Válidos?  Sim — não usam issue tracker
- Corretamente excluídos do cálculo

**Outliers baixos (3.97%):**
- 38 repos com ratio < 30% — projetos com muitas issues abertas
- Válidos?  Sim — podem estar em desenvolvimento ou abandonados

### Confounding Variable Crítica

**Correlação forte encontrada:**
- Mediana de issues por repo: **1.842** (muito alto!)
- 88.6% dos repos têm 100+ issues
- Apenas 1 repo tem 1-10 issues

**Interpretação:** Alta razão não = "boa governança", mas = "projeto maduro que processa muitas issues regularmente"

---

##  VALIDAÇÃO FINAL

**RQ05 — Linguagem Primária:**
- Dados válidos - Distribuição legítima - Pronto para análise 
**RQ06 — Razão Issues Fechadas:**
- Dados válidos - Mediana robusta - Confounding variable identificada - Pronto para análise 
**Conclusão:** Qualidade de dados EXCELENTE. 0 erros de coleta. Aprovado para análise estatística. 
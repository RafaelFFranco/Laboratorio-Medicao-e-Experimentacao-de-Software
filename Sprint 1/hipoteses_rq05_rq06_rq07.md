# Hipóteses Informais Refinadas — RQ05, RQ06 e RQ07

## RQ05: Sistemas populares são escritos nas linguagens mais populares?

### Hipótese Informal

**Hipótese:** Há concentração em linguagens convencionais, mas menos dominante que esperado. JavaScript (20.6%) e Python (20.4%) são os líderes, mas nenhuma linguagem individual supera 21% dos repositórios populares. O Top 5 representa 58.1%, significando que 42% dos sistemas populares estão distribuídos em 39 outras linguagens.

**Ressalva Crítica:** A análise inclui linguagens de configuração/markup (Shell 7.5%, Makefile 5.0%, HTML 3.9%, Dockerfile 3.3%) que inflacionam a dispersão. Se considerarmos apenas linguagens de programação puras (JavaScript, Python, Go, TypeScript, Rust, Java, Ruby, C++), a concentração seria maior (~43-45%).

**Edge Case:** 87 repositórios (8.7%) sem linguagem primária detectada (provavelmente templates ou documentação pura) — são outliers que devem ser validados.

**Esperado vs. Resultado:** Comparando com GitHub Octoverse 2023 (JavaScript > Python > TypeScript > Java > C#), nossa amostra alinha bem nos 2 primeiros (JS e Python), mas tem cauda mais longa com linguagens emergentes (Go, Rust, TypeScript aparecem mais cedo).

**Conclusão:** Sim, linguagens populares dominam, mas com maior dispersão que em projetos corporativos — ecossistema open-source é mais diverso.

---

## RQ06: Sistemas populares possuem um alto percentual de issues fechadas?

### Hipótese Informal (Refinada)

**Hipótese:** Sim, há alta taxa de fechamento de issues. Mediana de 87.5% é elevada, com Q1=70% e Q3=96%, indicando que 75% dos repositórios fecham entre 70-96% de suas issues.

**Ressalva CRÍTICA — Confounding Variable:** A alta taxa está correlacionada com a QUANTIDADE de issues, não necessariamente com "governança":
- 88.6% dos repositórios (886) têm 100+ issues (mediana 1842)
- Apenas 1 repositório tem 1-10 issues
- Repositórios com muitas issues tendem a ter maior razão porque:
  - São projetos maduros com processos estabelecidos
  - Issues antigas são resolvidas ou descartadas regularmente
  - Usuários ativos geram issues continuamente

**Interpretação Alternativa (não testada aqui):** A alta razão pode não indicar "qualidade superior", mas sim "madureza" — projetos consolidados têm mais issues porque mais usuários os usam.

**Edge Case:** 43 repositórios sem issues (4.3%) foram excluídos — provavelmente templates ou bibliotecas de documentação.

**Conclusão:** Mediana 87.5% é robusta (não apenas média), mas a interpretação como "qualidade" é fraca sem contexto de idade/tamanho dos repositórios.

---

## RQ07: Sistemas em linguagens mais populares recebem mais contribuição externa, releases frequentes e atualizações?

### Hipótese Informal (Refinada)

#### Part A: Contribuição Externa (PRs Aceitas)
**Hipótese:** Sem correlação clara entre linguagem e número de PRs aceitas. Shell (6587 média) e Makefile (6824 média) lideram, mas essas são configurações/scripts, não linguagens puras. Entre linguagens de programação, Python (4382) supera JavaScript (4154), contradizendo ideia de que JavaScript (mais popular) = mais contribuições. 

**Ressalva:** Médias podem estar enviesadas por outliers (um único repositório gigante infla a média). Seria necessário usar mediana também.

**Conclusão:** Não há evidência forte de que "linguagem mais popular = mais PRs".

---

#### Part B: Frequência de Releases
**Hipótese:** Correlação fraca com linguagem. Go (209.7 releases média) supera TypeScript (209.4), seguidos por Makefile (158.9). Python tem menos (96.0). A variação é grande demais para atribuir a linguagem sozinha.

**Conclusão:** Linguagem não explica releases — modelo de negócio do projeto importa mais.

---

#### Part C: Frequência de Atualização (FORTE CORRELAÇÃO ENCONTRADA)
**Hipótese Crítica (com confounding variable):** Aparentemente Rust (23.8 dias) atualiza muito mais que Java (146.7 dias), sugerindo "Rust é mais ativo". **PORÉM, isso está confundido com IDADE:**

| Linguagem  | Idade Média | Dias entre Updates |
|-----------|-------------|-------------------|
| TypeScript | 4.5 anos   | 39 dias           |
| Dockerfile | 4.2 anos   | 56 dias           |
| Rust      | 7.0 anos   | 23 dias           |
| Go        | 8.7 anos   | 80 dias           |
| Java      | 10.2 anos  | 146 dias          |

**Padrão:** Repos mais velhos atualizam menos frequentemente (provavelmente mais estáveis). TypeScript/Dockerfile, apesar de mais novas, têm freqüência média — Go e Rust divergem, sugerindo que hobby/experimentação (Rust) > corporativo estável (Java).

**Conclusão:** A frequência de atualização correlaciona MAIS com idade/maturidade do repositório do que com a linguagem em si. Não é "Rust causa atualizações rápidas", é "repos recentes em Rust atualizam mais".

---

## Limitações Conhecidas

1. **Referência de Linguagens Populares:** Usar Octoverse 2023/2024 ou TIOBE Index como baseline (não fazemos isso aqui)
2. **Confounding Variables:** Idade, tamanho, modelo de negócio não são separados de linguagem
3. **Médias vs Medianas:** Algumas métricas usam média (sensível a outliers) em vez de mediana
4. **Causalidade:** Não podemos afirmar "linguagem causa atividade" sem mais análise
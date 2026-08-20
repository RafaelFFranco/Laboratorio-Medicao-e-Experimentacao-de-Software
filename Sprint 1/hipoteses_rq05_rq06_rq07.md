# Hipóteses Informais — RQ05, RQ06 e RQ07

## 📌 Resumo Executivo

- **RQ05:** Linguagens populares (JavaScript, Python) dominam repositórios populares, mas com dispersão maior que o esperado.

- **RQ06:** Sistemas populares fecham a maioria de suas issues (esperado: >80% fechadas).

- **RQ07:** Linguagens mais populares recebem mais contribuições e atualizações com frequência. Mas talvez linguagens novas (Rust, TypeScript) inovem mais.

---

## RQ05: Sistemas populares são escritos nas linguagens mais populares?

### Hipótese Informal

Sim. Esperamos que JavaScript e Python apareçam como as linguagens primárias dominantes entre repositórios populares (top 1000 stars), porque:
- São linguagens muito difundidas no mercado
- Têm maior base de usuários
- Mais ferramentas e bibliotecas disponíveis

**Previsão:** Essas duas linguagens devem corresponder a ~40-50% dos repositórios analisados.

**Observação:** Alguns repositórios podem não ter linguagem primária detectada (documentação pura, templates, curadoria) — isso é esperado e não são "erros".

---

## RQ06: Sistemas populares possuem um alto percentual de issues fechadas?

### Hipótese Informal

Sim. Repositórios populares devem ter uma alta taxa de fechamento de issues porque:
- Projetos consolidados têm mais mantenedores
- Comunidade engajada ajuda a resolver problemas
- Política de manutenção mais rigorosa

**Previsão:** Esperamos mediana acima de 75-80% de issues fechadas.

**Observação:** Alguns repositórios não usam issue tracker (exemplo: Linux kernel) — esses terão 0 issues e devem ser excluídos do cálculo.

---

## RQ07: Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência?

### Hipótese Informal (Part A): Contribuição Externa

Provavelmente sim. Linguagens populares devem receber mais PRs aceitas porque:
- Mais desenvolvedores sabem usar essas linguagens
- Projetos maiores atraem mais contribuidores
- Ecossistema mais consolidado

**Previsão:** JavaScript e Python devem ter médias altas de PRs aceitas.

---

### Hipótese Informal (Part B): Releases

Talvez. Linguagens diferentes podem ter padrões de release diferentes:
- Linguagens novas (Rust, Go) podem fazer mais releases para ganhar adoção
- Linguagens antigas (Java, Python) podem ser mais estáveis e fazer menos releases

**Previsão:** Sem certeza — varia muito por projeto.

---

### Hipótese Informal (Part C): Frequência de Atualização

Provavelmente não correlaciona só com linguagem. Mas suspeitamos que:
- Projetos recentes atualizam mais frequentemente
- Projetos estáveis/maduros atualizam menos

**Previsão:** Linguagens emergentes podem parecer "mais ativas" porque seus repositórios tendem a ser mais novos.

---

## Limitações Conhecidas

1. **Apenas correlação:** Essas hipóteses não estabelecem causalidade
2. **Dados de uma única fonte:** Apenas GitHub, não inclui GitLab, Bitbucket, etc.

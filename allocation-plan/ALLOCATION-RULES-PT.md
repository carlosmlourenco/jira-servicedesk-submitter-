# Regras de Alocacao de Roles — PIR

> Este ficheiro documenta **todas as regras de alocacao** que o `pir.html` aplica
> na funcionalidade **✨ Suggest allocation** e ao preencher a grelha de pessoas.
> E a fonte de verdade legivel por humanos, mantida em sincronia com
> `allocation-plan/pir.html`.
>
> Versao em ingles: [`ALLOCATION-RULES.md`](ALLOCATION-RULES.md)
>
> *O texto portugues omite acentos e cedilha de proposito, para evitar problemas
> de codificacao.*
>
> Ultima atualizacao: 2026-09-14 (regras por role; 13 roles; aviso de horas por alocar; dropdowns Preferred Area/Seniority)

---

## Regras globais (todas as roles)

| Regra | Valor | Notas |
|-------|-------|-------|
| Unidade da alocacao semanal | **horas/semana** | A grelha e preenchida em horas por semana. |
| Minimo por pessoa/semana | **2 h** | Uma pessoa alocada nunca fica abaixo de 2 h numa semana em que trabalha. |
| Maximo por pessoa/semana | **32 h** | Teto global (= 4 dias). Algumas roles tem teto mais baixo (ver por role). |
| Incremento (step) | **2 h** | Os valores sobem/descem de 2 em 2 horas. |
| Horas por dia | **8 h** | Converte horas ⇄ dias (Total Days = Total Hours ÷ 8). |
| Semana completa | **5 dias (40 h)** | Base do calculo de FTE. |
| Duracao | **N semanas** (campo *Duration*) | A alocacao espalha-se de forma **plana** pelas N semanas, a partir da *Start date*. A *End date* e derivada. |
| Nunca excede o breakdown | ✔️ | A sugestao nunca aloca **mais** horas do que o breakdown da role. |
| Horas que nao cabem | **nao aloca + avisa** | As sobras ficam **por atribuir** e e mostrado um **aviso** na seccao *People* com a role e as horas por alocar. |

### Spread interno (como a sugestao distribui por pessoa)

- O spread interno trabalha em **horas** numa grelha de 2 h (`MIN_H = 2`, `STEP_H = 2`).
- Pessoas por role = `ceil( horas_da_role / (teto_semanal × N) )`, limitado pelo
  **maximo de pessoas** da role.
- A distribuicao e **plana** pelas N semanas (as unidades extra de 2 h entram uma
  por semana a partir do inicio), respeitando o teto semanal da role.

### Staffing Validation Status (regra transversal)

- Opcoes: `Pre-Approved by GDC Mgmt (Ready to Book)` · `PM Preference (Pending GDC Approval)` · `Open Demand (WFM to Source)`
- **Se o *Suggested Resource (Optional)* estiver vazio → o status e forcado a
  `Open Demand (WFM to Source)`** (seletor desativado enquanto automatico).
- Todas as linhas auto-sugeridas saem **sem resource** → entram como **Open Demand**.

### Allocation Type (regra transversal)

- Opcoes: `add` · `remove` · `split` · `swap` — uma por linha, **default `add`**.

### Preferred Area / Preferred Seniority (regra transversal)

- **Preferred Area** (dropdown, **obrigatorio antes de Submit**): `APAC` · `EMEA` · `LATAM` · `NAMER` · `GDC` · `Partner`.
  O Submit e bloqueado com um aviso se alguma linha alocada (com horas semanais) nao tiver area.
- **Preferred Seniority** (dropdown, **opcional**): `Associate` · `Professional` · `Senior Professional` · `Advanced` · `Expert` · `Principal` · `Senior Principal` · `Manager` · `Senior Manager` · `Director` · `Senior Director`.

---

## Maximo de pessoas por role

| Role | Max pessoas |
|------|:-----------:|
| Data Scientist | **ate 3** |
| Software Engineer | **ate 3** |
| Todas as outras roles | **1** |

---

## Regras por role

Legenda: **Visible** = no breakdown por defeito · **Expand** = atras do toggle "+ More roles".
**IC** = Individual Contributor · **Manager** = grupo Manager (informativo; o cap e por role).

### Delivery Manager
- Grupo: **Individual Contributor**
- Visibilidade: **Visible**
- Max pessoas: **1**
- Shape: alocacao **plana** durante todo o projeto.
- Tempo: **default 2 h/semana**. Se a role tiver horas a sobrar pode subir ate **8 h/semana**; o resto alem disso **nao e alocado**.

### Project Manager
- Grupo: **Individual Contributor**
- Visibilidade: **Visible**
- Max pessoas: **1**
- Shape: alocacao **plana** durante todo o projeto.
- Teto: no maximo **50% do tempo = 16 h/semana**.

### Compliance Manager
- Grupo: **Individual Contributor**
- Visibilidade: **Visible**
- Max pessoas: **1**

### Engineering Manager
- Grupo: **Manager**
- Visibilidade: **Visible**
- Max pessoas: **1**
- Tempo: **default 2 h/semana** (pode subir ate 8 h/semana; o resto nao e alocado).
- **Condicional:** se houver horas em **Software Engineer** e **nenhuma** em Engineering Manager →
  atribui **2 h/semana** ao Engineering Manager, **retiradas** do Software Engineer.
  Caso contrario, usa o tempo definido para a role.

### Solution Architect
- Grupo: **Individual Contributor**
- Visibilidade: **Visible**
- Max pessoas: **1**

### Software Engineer
- Grupo: **Individual Contributor**
- Visibilidade: **Visible**
- Max pessoas: **ate 3** (equipa tipica 1).

### Risk & AI Manager
- Grupo: **Manager**
- Visibilidade: **Visible**
- Max pessoas: **1**
- **Condicional:** se houver horas em **Data Scientist / Risk Consultant / Business Analyst**
  e **nenhuma** em Risk & AI Manager →
  atribui **2 h/semana** ao Risk & AI Manager, **retiradas proporcionalmente** dessas roles.
  Caso contrario, usa o tempo definido para a role.

### Data Scientist
- Grupo: **Individual Contributor**
- Visibilidade: **Visible**
- Max pessoas: **ate 3** (equipa tipica 1).

### Business Analyst
- Grupo: **Individual Contributor**
- Visibilidade: **Visible**
- Max pessoas: **1**
- Shape: o trabalho concentra-se nas **primeiras 30% das semanas do projeto**
  (ex.: projeto de 9 semanas → trabalho feito em 3 semanas).

### Risk Consultant
- Grupo: **Individual Contributor**
- Visibilidade: **Visible**
- Max pessoas: **1**

### Project Director
- Grupo: **Manager**
- Visibilidade: **Expand** (escondida por defeito)
- Max pessoas: **1**

### Quality Assurance Engineer
- Grupo: **Individual Contributor**
- Visibilidade: **Expand** (escondida por defeito)
- Max pessoas: **1**

### Delivery Consultant
- Grupo: **Individual Contributor**
- Visibilidade: **Expand** (escondida por defeito)
- Max pessoas: **1**

---

## Resumo rapido (tabela)

| Role | Grupo | Visibilidade | Max pessoas | Teto semanal | Shape especial |
|------|-------|--------------|:-----------:|--------------|----------------|
| Delivery Manager | IC | Visible | 1 | 2→8 h | plana; default 2 h |
| Project Manager | IC | Visible | 1 | 16 h | plana |
| Compliance Manager | IC | Visible | 1 | 32 h | — |
| Engineering Manager | Manager | Visible | 1 | 2→8 h | default 2 h; condicional vs Software Engineer |
| Solution Architect | IC | Visible | 1 | 32 h | — |
| Software Engineer | IC | Visible | ate 3 | 32 h | — |
| Risk & AI Manager | Manager | Visible | 1 | 32 h | condicional vs DS/Risk Consultant/BA |
| Data Scientist | IC | Visible | ate 3 | 32 h | — |
| Business Analyst | IC | Visible | 1 | 32 h | primeiras 30% das semanas |
| Risk Consultant | IC | Visible | 1 | 32 h | — |
| Project Director | Manager | Expand | 1 | 32 h | — |
| Quality Assurance Engineer | IC | Expand | 1 | 32 h | — |
| Delivery Consultant | IC | Expand | 1 | 32 h | — |

---

## Notas de implementacao / a validar

- As regras condicionais (Risk & AI Manager e Engineering Manager a receberem
  2 h/semana retiradas de outras roles) estao **em fase de teste** — a afinar
  conforme o resultado pratico.
- "Retiradas proporcionalmente" (Risk & AI Manager): as 2 h/semana × N semanas sao
  subtraidas do total das roles dependentes, repartidas pelo peso de cada uma.

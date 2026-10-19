# Role Allocation Rules — PIR  ·  Regras de Alocacao de Roles — PIR

> **EN-GB** — This file documents **all allocation rules** that `pir.html` applies in the
> **✨ Suggest allocation** feature and when filling the people grid. It is the
> human-readable source of truth, kept in sync with `allocation-plan/pir.html`.
>
> **PT-PT** — Este ficheiro documenta **todas as regras de alocacao** que o `pir.html`
> aplica na funcionalidade **✨ Suggest allocation** e ao preencher a grelha de
> pessoas. E a fonte de verdade legivel por humanos, mantida em sincronia com
> `allocation-plan/pir.html`.
>
> *This document is bilingual: en-GB first, pt-PT second. Portuguese text omits
> accents and the cedilla on purpose to avoid encoding issues.*
>
> Last updated / Ultima atualizacao: 2026-09-14 (detailed per-role rules; 13 roles; unallocated-hours warning)

---

## Global rules (apply to every role) · Regras globais (todas as roles)

**EN-GB**

| Rule | Value | Notes |
|------|-------|-------|
| Weekly allocation unit | **hours/week** | The grid is filled in hours per week. |
| Minimum per person/week | **2 h** | An allocated person never goes below 2 h in a week they work. |
| Maximum per person/week | **32 h** | Global cap (= 4 days). Some roles have a lower cap (see per role). |
| Increment (step) | **2 h** | Values go up/down in 2-hour steps. |
| Hours per day | **8 h** | Converts hours ⇄ days (Total Days = Total Hours ÷ 8). |
| Full week | **5 days (40 h)** | Basis for the FTE calculation. |
| Duration | **N weeks** (*Duration* field) | Allocation is spread **flat** across the N weeks, starting at the *Start date*. The *End date* is derived. |
| Never exceeds the breakdown | ✔️ | The suggestion never allocates **more** hours than the role's breakdown. |
| Hours that do not fit | **not allocated + warning** | Surplus hours are **left unassigned** and a **warning** is shown in the *People* section naming the role and the hours left over. |

**PT-PT**

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

### Internal spread · Spread interno

**EN-GB**
- The internal spread works in **hours** on a 2-hour grid (`MIN_H = 2`, `STEP_H = 2`).
- People per role = `ceil( role_hours / (weekly_cap × N) )`, limited by the role's **max people**.
- The distribution is **flat** across the N weeks (extra 2 h units placed one per week from the start), respecting the role's weekly cap.

**PT-PT**
- O spread interno trabalha em **horas** numa grelha de 2 h (`MIN_H = 2`, `STEP_H = 2`).
- Pessoas por role = `ceil( horas_da_role / (teto_semanal × N) )`, limitado pelo **max de pessoas** da role.
- A distribuicao e **plana** pelas N semanas (as unidades extra de 2 h entram uma por semana a partir do inicio), respeitando o teto semanal da role.

### Staffing Validation Status (cross-cutting · transversal)

**EN-GB**
- Options: `Pre-Approved by GDC Mgmt (Ready to Book)` · `PM Preference (Pending GDC Approval)` · `Open Demand (WFM to Source)`
- **If *Suggested Resource (Optional)* is empty → status is forced to `Open Demand (WFM to Source)`** (select disabled while automatic).
- Every auto-suggested line comes **without a resource** → enters as **Open Demand**.

**PT-PT**
- Opcoes: `Pre-Approved by GDC Mgmt (Ready to Book)` · `PM Preference (Pending GDC Approval)` · `Open Demand (WFM to Source)`
- **Se o *Suggested Resource (Optional)* estiver vazio → o status e forcado a `Open Demand (WFM to Source)`** (seletor desativado enquanto automatico).
- Todas as linhas auto-sugeridas saem **sem resource** → entram como **Open Demand**.

### Allocation Type (cross-cutting · transversal)

**EN-GB** — Options: `add` · `remove` · `split` · `swap` — one per line, **default `add`**.

**PT-PT** — Opcoes: `add` · `remove` · `split` · `swap` — uma por linha, **default `add`**.

---

## Maximum people per role · Maximo de pessoas por role

| Role | Max people / Max pessoas |
|------|:------------------------:|
| Data Scientist | **up to 3 / ate 3** |
| Software Engineer | **up to 3 / ate 3** |
| All other roles / Todas as outras | **1** |

---

## Per-role rules · Regras por role

**EN-GB** — Legend: **Visible** = shown in the breakdown by default · **Expand** = behind the "+ More roles" toggle. **IC** = Individual Contributor · **Manager** = Manager group (informational; the cap is per role).

**PT-PT** — Legenda: **Visible** = no breakdown por defeito · **Expand** = atras do toggle "+ More roles". **IC** = Individual Contributor · **Manager** = grupo Manager (informativo; o cap e por role).

### Delivery Manager
- Group: **Individual Contributor** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **1**
- **EN-GB** — Flat allocation across the whole project. Default **2 h/week**; may grow up to **8 h/week** when there are spare hours; any remainder beyond that is **not allocated**.
- **PT-PT** — Alocacao plana durante todo o projeto. Default **2 h/semana**; pode subir ate **8 h/semana** quando ha horas a sobrar; o resto alem disso **nao e alocado**.

### Project Manager
- Group: **Individual Contributor** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **1**
- **EN-GB** — Flat allocation across the whole project. Cap: at most **50% = 16 h/week**.
- **PT-PT** — Alocacao plana durante todo o projeto. Teto: no maximo **50% = 16 h/semana**.

### Compliance Manager
- Group: **Individual Contributor** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **1**

### Engineering Manager
- Group: **Manager** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **1**
- **EN-GB** — Default **2 h/week** (may grow up to 8 h/week; remainder not allocated). **Conditional:** if there are hours on **Software Engineer** and **none** on Engineering Manager → assign **2 h/week** to Engineering Manager, **taken from** Software Engineer. Otherwise use the time defined for the role.
- **PT-PT** — Default **2 h/semana** (pode subir ate 8 h/semana; o resto nao e alocado). **Condicional:** se houver horas em **Software Engineer** e **nenhuma** em Engineering Manager → atribui **2 h/semana** ao Engineering Manager, **retiradas** do Software Engineer. Caso contrario, usa o tempo definido para a role.

### Solution Architect
- Group: **Individual Contributor** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **1**

### Software Engineer
- Group: **Individual Contributor** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **up to 3 / ate 3** (typical team 1 / equipa tipica 1)

### Risk & AI Manager
- Group: **Manager** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **1**
- **EN-GB** — **Conditional:** if there are hours on **Data Scientist / Risk Consultant / Business Analyst** and **none** on Risk & AI Manager → assign **2 h/week** to Risk & AI Manager, **taken proportionally** from those roles. Otherwise use the time defined for the role.
- **PT-PT** — **Condicional:** se houver horas em **Data Scientist / Risk Consultant / Business Analyst** e **nenhuma** em Risk & AI Manager → atribui **2 h/semana** ao Risk & AI Manager, **retiradas proporcionalmente** dessas roles. Caso contrario, usa o tempo definido para a role.

### Data Scientist
- Group: **Individual Contributor** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **up to 3 / ate 3** (typical team 1 / equipa tipica 1)

### Business Analyst
- Group: **Individual Contributor** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **1**
- **EN-GB** — Work is concentrated in the **first 30% of the project weeks** (e.g. a 9-week project → work done in 3 weeks).
- **PT-PT** — O trabalho concentra-se nas **primeiras 30% das semanas do projeto** (ex.: projeto de 9 semanas → trabalho feito em 3 semanas).

### Risk Consultant
- Group: **Individual Contributor** · Visibility/Visibilidade: **Visible** · Max people/pessoas: **1**

### Project Director
- Group: **Manager** · Visibility/Visibilidade: **Expand** (hidden by default / escondida por defeito) · Max people/pessoas: **1**

### Quality Assurance Engineer
- Group: **Individual Contributor** · Visibility/Visibilidade: **Expand** (hidden by default / escondida por defeito) · Max people/pessoas: **1**

### Delivery Consultant
- Group: **Individual Contributor** · Visibility/Visibilidade: **Expand** (hidden by default / escondida por defeito) · Max people/pessoas: **1**

---

## Quick summary · Resumo rapido

| Role | Group | Visibility/Visibilidade | Max people/pessoas | Weekly cap / Teto semanal | Special shape / Shape especial |
|------|-------|-------------------------|:------------------:|---------------------------|--------------------------------|
| Delivery Manager | IC | Visible | 1 | 2→8 h | flat; default 2 h |
| Project Manager | IC | Visible | 1 | 16 h | flat |
| Compliance Manager | IC | Visible | 1 | 32 h | — |
| Engineering Manager | Manager | Visible | 1 | 2→8 h | default 2 h; conditional vs Software Engineer |
| Solution Architect | IC | Visible | 1 | 32 h | — |
| Software Engineer | IC | Visible | up to 3 / ate 3 | 32 h | — |
| Risk & AI Manager | Manager | Visible | 1 | 32 h | conditional vs DS/Risk Consultant/BA |
| Data Scientist | IC | Visible | up to 3 / ate 3 | 32 h | — |
| Business Analyst | IC | Visible | 1 | 32 h | first 30% of weeks / primeiras 30% das semanas |
| Risk Consultant | IC | Visible | 1 | 32 h | — |
| Project Director | Manager | Expand | 1 | 32 h | — |
| Quality Assurance Engineer | IC | Expand | 1 | 32 h | — |
| Delivery Consultant | IC | Expand | 1 | 32 h | — |

---

## Implementation notes / to validate · Notas de implementacao / a validar

**EN-GB**
- The conditional rules (Risk & AI Manager and Engineering Manager receiving 2 h/week taken from other roles) are **under test** — to be tuned based on real-world results.
- "Taken proportionally" (Risk & AI Manager): the 2 h/week × N weeks are subtracted from the total of the dependent roles, split by each one's weight.

**PT-PT**
- As regras condicionais (Risk & AI Manager e Engineering Manager a receberem 2 h/semana retiradas de outras roles) estao **em fase de teste** — a afinar conforme o resultado pratico.
- "Retiradas proporcionalmente" (Risk & AI Manager): as 2 h/semana × N semanas sao subtraidas do total das roles dependentes, repartidas pelo peso de cada uma.

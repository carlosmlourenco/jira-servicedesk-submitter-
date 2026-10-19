# Regras de Alocação de Roles — PIR

> Este ficheiro documenta **todas as regras de alocação** que o `pir.html` aplica
> na funcionalidade **✨ Suggest allocation** e no preenchimento da grelha de pessoas.
> É a fonte de verdade legível por humanos — mantido em sincronia com o código em
> `allocation-plan/pir.html`.
>
> Última atualização: 2026-09-14 (regras por role detalhadas; 13 roles; aviso de horas por alocar)

---

## Regras globais (aplicam-se a todas as roles)

| Regra | Valor | Notas |
|-------|-------|-------|
| Unidade da alocação semanal | **horas/semana** | A grelha é preenchida em horas por semana. |
| Mínimo por pessoa/semana | **2 h** | Uma pessoa alocada nunca fica abaixo de 2 h numa semana em que trabalha. |
| Máximo por pessoa/semana | **32 h** | Teto global (= 4 dias). Algumas roles têm teto mais baixo (ver por role). |
| Incremento (step) | **2 h** | Os valores sobem/descem de 2 em 2 horas. |
| Horas por dia | **8 h** | Usado para converter horas ⇄ dias (Total Days = Total Hours ÷ 8). |
| Semana completa | **5 dias (40 h)** | Base do cálculo de FTE. |
| Duração | **N semanas** (campo *Duration*) | A alocação espalha-se de forma **plana** pelas N semanas, a partir da *Start date*. A *End date* é derivada. |
| Nunca excede o breakdown | ✔️ | A sugestão nunca aloca **mais** horas do que o breakdown da role. |
| Horas a mais não cabem | **não aloca + avisa** | Se houver demasiadas horas para as semanas/tetos disponíveis, as sobras **não são atribuídas** e é mostrado um **aviso** na secção *People* a indicar a role e as horas por alocar. |

### Spread interno (como a sugestão distribui por pessoa)

- O cálculo interno trabalha em **dias** numa grelha de 0,25 dia (= 2 h).
  - `DAY_MIN = 0,25` dia (2 h) · `DAY_MAX = 4` dias (32 h)
- Nº de pessoas por role = `ceil( (dias_da_role / N) / 4 )`, limitado pelo
  **máximo de pessoas** da role.
- A distribuição é **plana** pelas N semanas (os quartos extra entram um por
  semana a partir do início), respeitando o teto semanal da role.

### Staffing Validation Status (regra transversal)

- Opções: `Pre-Approved by GDC Mgmt (Ready to Book)` · `PM Preference (Pending GDC Approval)` · `Open Demand (WFM to Source)`
- **Se o *Suggested Resource (Optional)* estiver vazio → o status é forçado a
  `Open Demand (WFM to Source)`** (seletor desativado enquanto em modo automático).
- Todas as linhas sugeridas automaticamente saem **sem resource** → entram como **Open Demand**.

### Allocation Type (regra transversal)

- Opções: `add` · `remove` · `split` · `swap` — uma por linha, **default `add`**.

---

## Máximo de pessoas por role

| Role | Máx. pessoas |
|------|:------------:|
| Data Scientist | **até 3** |
| Software Engineer | **até 3** |
| Todas as outras | **1** |

---

## Regras por Role

Legenda: **Visível** = no breakdown por defeito · **Expand** = atrás do toggle "+ More roles".
**IC** = Individual Contributor · **Manager** = grupo Manager (campo informativo; o cap é por role).

### Delivery Manager
- Group: **Individual Contributor**
- Visibilidade: **Visível**
- Máx. pessoas: **1**
- Shape: alocação **plana** durante todo o projeto.
- Tempo: **default 2 h/semana**. Se sobrarem horas da role pode subir até **8 h/semana**; se ainda sobrar, **não aloca** o resto.

### Project Manager
- Group: **Individual Contributor**
- Visibilidade: **Visível**
- Máx. pessoas: **1**
- Shape: alocação **plana** durante todo o projeto.
- Teto: no máximo **50% do tempo = 16 h/semana**.

### Compliance Manager
- Group: **Individual Contributor**
- Visibilidade: **Visível**
- Máx. pessoas: **1**

### Engineering Manager
- Group: **Manager**
- Visibilidade: **Visível**
- Máx. pessoas: **1**
- Tempo: **default 2 h/semana** (pode subir até 8 h/semana; sobras não são alocadas).
- **Condicional:** se houver horas em **Software Engineer** e **nenhuma** em Engineering Manager →
  atribui **2 h/semana** ao Engineering Manager, **retiradas** do Software Engineer.
  Caso contrário, usa o tempo definido para a role.

### Solution Architect
- Group: **Individual Contributor**
- Visibilidade: **Visível**
- Máx. pessoas: **1**

### Software Engineer
- Group: **Individual Contributor**
- Visibilidade: **Visível**
- Máx. pessoas: **até 3** (equipa típica 1).

### Risk & AI Manager
- Group: **Manager**
- Visibilidade: **Visível**
- Máx. pessoas: **1**
- **Condicional:** se houver horas em **Data Scientist / Risk Consultant / Business Analyst**
  e **nenhuma** em Risk & AI Manager →
  atribui **2 h/semana** ao Risk & AI Manager, **retiradas proporcionalmente** dessas roles.
  Caso contrário, usa o tempo definido para a role.

### Data Scientist
- Group: **Individual Contributor**
- Visibilidade: **Visível**
- Máx. pessoas: **até 3** (equipa típica 1).

### Business Analyst
- Group: **Individual Contributor**
- Visibilidade: **Visível**
- Máx. pessoas: **1**
- Shape: o trabalho concentra-se nos **primeiros 30% das semanas do projeto**
  (ex.: projeto de 9 semanas → trabalho feito em 3 semanas).

### Risk Consultant
- Group: **Individual Contributor**
- Visibilidade: **Visível**
- Máx. pessoas: **1**

### Project Director
- Group: **Manager**
- Visibilidade: **Expand** (escondida por defeito)
- Máx. pessoas: **1**

### Quality Assurance Engineer
- Group: **Individual Contributor**
- Visibilidade: **Expand** (escondida por defeito)
- Máx. pessoas: **1**

### Delivery Consultant
- Group: **Individual Contributor**
- Visibilidade: **Expand** (escondida por defeito)
- Máx. pessoas: **1**

---

## Resumo rápido (tabela)

| Role | Group | Visibilidade | Máx. pessoas | Teto/semana | Shape especial |
|------|-------|--------------|:------------:|-------------|----------------|
| Delivery Manager | IC | Visível | 1 | 2→8 h | plana; default 2 h |
| Project Manager | IC | Visível | 1 | 16 h | plana |
| Compliance Manager | IC | Visível | 1 | 32 h | — |
| Engineering Manager | Manager | Visível | 1 | 2→8 h | default 2 h; condicional vs Software Engineer |
| Solution Architect | IC | Visível | 1 | 32 h | — |
| Software Engineer | IC | Visível | até 3 | 32 h | — |
| Risk & AI Manager | Manager | Visível | 1 | 32 h | condicional vs DS/RiskC/BA |
| Data Scientist | IC | Visível | até 3 | 32 h | — |
| Business Analyst | IC | Visível | 1 | 32 h | primeiros 30% das semanas |
| Risk Consultant | IC | Visível | 1 | 32 h | — |
| Project Director | Manager | Expand | 1 | 32 h | — |
| Quality Assurance Engineer | IC | Expand | 1 | 32 h | — |
| Delivery Consultant | IC | Expand | 1 | 32 h | — |

---

## Notas de implementação / a validar

- As regras condicionais (Risk & AI Manager e Engineering Manager a receberem
  2 h/semana retiradas de outras roles) estão em **fase de teste** — a afinar
  conforme o resultado prático.
- "Retiradas proporcionalmente" (Risk & AI Manager): as 2 h/semana × N semanas
  são subtraídas do total das roles dependentes, repartidas pelo peso de cada uma.

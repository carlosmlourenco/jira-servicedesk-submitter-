# Regras de Alocação de Roles — PIR

> Este ficheiro documenta **todas as regras de alocação** que o `pir.html` aplica
> na funcionalidade **✨ Suggest allocation** e no preenchimento da grelha de pessoas.
> É a fonte de verdade legível por humanos — mantido em sincronia com o código em
> `allocation-plan/pir.html`.
>
> Última atualização: 2026-09-14

---

## Regras globais (aplicam-se a todas as roles)

Estas regras valem para qualquer role, independentemente de ser de gestão ou hands-on.

| Regra | Valor | Notas |
|-------|-------|-------|
| Unidade da alocação semanal | **horas/semana** | A grelha é preenchida em horas por semana. |
| Mínimo por pessoa/semana | **2 h** | Uma pessoa alocada nunca fica abaixo de 2 h numa semana em que trabalha. |
| Máximo por pessoa/semana | **32 h** | Uma pessoa nunca ultrapassa 32 h/semana (= 4 dias). |
| Incremento (step) | **2 h** | Os valores sobem/descem de 2 em 2 horas. |
| Horas por dia | **8 h** | Usado para converter horas ⇄ dias (Total Days = Total Hours ÷ 8). |
| Semana completa | **5 dias (40 h)** | Base do cálculo de FTE. |
| Duração | **N semanas** (campo *Duration*) | A alocação espalha-se de forma **plana** pelas N semanas, a partir da *Start date*. A *End date* é derivada. |
| Nunca excede o breakdown | ✔️ | A sugestão nunca aloca **mais** horas do que o breakdown da role; iguala ou fica ligeiramente abaixo (arredonda para baixo ao passo de 2 h). |
| Duração demasiado curta | avisa | Se nem no máximo de pessoas as horas cabem, aloca o máximo possível e mostra um aviso com as horas em falta. |
| Duração demasiado longa | concentra no início | Se por pessoa/semana ficar abaixo do mínimo, coloca o mínimo nas primeiras semanas necessárias e deixa as restantes a zero. |

### Spread interno (como a sugestão distribui por pessoa)

- O cálculo interno trabalha em **dias** numa grelha de 0,25 dia (= 2 h).
  - `DAY_MIN = 0,25` dia (2 h) · `DAY_MAX = 4` dias (32 h)
- Nº de pessoas por role = `ceil( (dias_da_role / N) / 4 )`, limitado pelo
  **máximo de pessoas** da role (ver abaixo).
- Cada pessoa é enchida até 4 dias/semana; o remanescente vai para a última pessoa.
- No fim, os dias são convertidos para horas (× 8) ao escrever na grelha.

### Staffing Validation Status (regra transversal)

- Opções disponíveis:
  1. `Pre-Approved by GDC Mgmt (Ready to Book)`
  2. `PM Preference (Pending GDC Approval)`
  3. `Open Demand (WFM to Source)`
- **Se o *Suggested Resource (Optional)* estiver vazio → o status é forçado
  automaticamente a `Open Demand (WFM to Source)`** (o seletor fica desativado
  enquanto está em modo automático). Assim que escreves um resource, o seletor
  reabre para escolheres o status.
- Todas as linhas sugeridas automaticamente saem **sem resource** → portanto
  entram como **Open Demand**.

### Allocation Type (regra transversal)

- Opções: `add` · `remove` · `split` · `swap`
- Uma por linha, **default `add`**. A sugestão cria sempre linhas com `add`.

---

## Máximo de pessoas por role

Regra atual (Fase 1): **roles de gestão = 1 pessoa**, **todas as outras = 3 pessoas**.

> ⚠️ **Placeholder (Fase 2):** estes limites são provisórios. Na Fase 2 serão
> refinados por role individual.

---

## Regras por Role

Legenda:
- **Visível** = aparece no breakdown por defeito · **Expand** = escondida atrás do toggle "+ More roles".
- **Máx. pessoas** = limite usado pela sugestão.

### Delivery Manager
- Grupo: **Gestão**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **1**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Project Manager
- Grupo: **Gestão**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **1**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Compliance Manager
- Grupo: **Gestão**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **1**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Engineering Manager
- Grupo: **Gestão**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **1**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Solution Architect
- Grupo: **Hands-on**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Software Engineer
- Grupo: **Hands-on**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Risk & AI Manager
- Grupo: **Gestão**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **1**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Data Scientist
- Grupo: **Hands-on**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Business Analyst
- Grupo: **Hands-on**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Risk Consultant
- Grupo: **Hands-on**
- Visibilidade: **Visível**
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Project Director
- Grupo: **Gestão**
- Visibilidade: **Expand** (escondida por defeito)
- Máx. pessoas (Suggest): **1**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Fraud Analyst
- Grupo: **Hands-on**
- Visibilidade: **Expand** (escondida por defeito)
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Data Analyst
- Grupo: **Hands-on**
- Visibilidade: **Expand** (escondida por defeito)
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Quality Assurance Engineer
- Grupo: **Hands-on**
- Visibilidade: **Expand** (escondida por defeito)
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

### Delivery Consultant
- Grupo: **Hands-on**
- Visibilidade: **Expand** (escondida por defeito)
- Máx. pessoas (Suggest): **3**
- Limites semanais: 2 h mín · 32 h máx · passo 2 h

---

## Resumo rápido (tabela)

| Role | Grupo | Visibilidade | Máx. pessoas |
|------|-------|--------------|:------------:|
| Delivery Manager | Gestão | Visível | 1 |
| Project Manager | Gestão | Visível | 1 |
| Compliance Manager | Gestão | Visível | 1 |
| Engineering Manager | Gestão | Visível | 1 |
| Solution Architect | Hands-on | Visível | 3 |
| Software Engineer | Hands-on | Visível | 3 |
| Risk & AI Manager | Gestão | Visível | 1 |
| Data Scientist | Hands-on | Visível | 3 |
| Business Analyst | Hands-on | Visível | 3 |
| Risk Consultant | Hands-on | Visível | 3 |
| Project Director | Gestão | Expand | 1 |
| Fraud Analyst | Hands-on | Expand | 3 |
| Data Analyst | Hands-on | Expand | 3 |
| Quality Assurance Engineer | Hands-on | Expand | 3 |
| Delivery Consultant | Hands-on | Expand | 3 |

---

## Fase 2 (pendente)

- Refinar o **máximo de pessoas por role** individualmente (hoje é 1 para gestão
  e 3 para as restantes — placeholder).
- Possíveis regras específicas por role (ex.: dependências entre roles, PM extra
  quando Data Scientist está no máximo, etc.) a definir.

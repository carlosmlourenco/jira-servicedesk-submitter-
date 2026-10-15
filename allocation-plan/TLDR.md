# TL;DR — Ferramenta de Planeamento de Alocação

Ferramenta que gera o **plano de alocação de recursos** (o anexo obrigatório dos
Change Requests no portal Jira), com os cálculos todos feitos automaticamente.

## O que faz

- Indicas as **horas totais** a alocar, os **recursos** (nome, role, capacidade
  em dias/semana, cidade) e um **backup** opcional — e a ferramenta espalha a
  alocação ao longo do tempo até esgotar as horas, acertando exatamente no
  limite (preenche a última semana para bater certo no total).
- Considera **feriados de Portugal** (nacionais + municipais de Lisboa, Porto e
  Coimbra) e **PTO/férias** reais, lidos de um **calendário (`.ics`)** por nome.
- Cria **backups automaticamente**: cobrem os dias exatos em que a pessoa
  principal está ausente (mesmo role).
- O **PM é secundário**: só aloca 0.25/semana enquanto houver alguém hands-on a
  trabalhar; pára quando o trabalho hands-on pára.
- Calcula tudo: Days, Hours, FTE, linha TOTAL, agregação PIR por role,
  AI Comments ("hours missing"/"exceed") e o indicador "Total Values Match?".

## Como se usa (quatro formas)

1. **`generate_plan.py`** — CLI a partir de um CSV de input.
2. **`index.html`** — formulário manual no browser (totais em tempo real).
3. **`planner.html`** — **auto-planner no browser** (o principal): importa o
   `.ics` do calendário, preenche o PTO por nome, gera o plano, e no
   "Generate allocation" cria um **ID único + link partilhável** que reabre o
   plano exato sem precisar do CSV.
4. **`plan_from_calendar.py`** — totalmente automático: lê um config JSON, vai
   buscar o PTO ao calendário (URL guardado uma vez no `.env`) e produz o CSV.

## Regras de cálculo (resumo)

| Campo | Regra |
| --- | --- |
| Days por role | soma dos valores semanais |
| Hours por role | Days × 8 |
| FTE | média das semanas ativas ÷ 5 (semanas vazias excluídas) |
| Feriado numa semana | reduz 1 dia a essa semana (mínimo 0.25 se continua a trabalhar) |
| Semana toda de PTO | 0 (não trabalha) |
| Match? | horas do grid == horas do PIR → TRUE/FALSE |

Mapeamento de roles para PIR: PM, DM, DS (Data Scientist + Data Analyst),
RiskC (Risk Consultant + Risk&AI Manager), BA, ENG (TS) (Software Engineer,
Technical Lead, Solution Architect, Engineering Manager).

## Privacidade

- O URL do calendário e os tokens ficam **só no `.env`** (git-ignored).
- `.env`, ficheiros `*.ics` e configs reais **nunca** são commitados — só os
  ficheiros `*.example.*` com placeholders.

## Resultado

Exporta o CSV no formato exato do template, validado contra um exemplo real
(acerta nas 400h de limite, Match TRUE).

## Link partilhável (atual)

No browser, cada "Generate" gera um **ID único** (ex. `projeto-5f239a`) e um
link que codifica o plano inteiro no próprio URL — abre o plano sem servidor nem
CSV. Pensado para evoluir mais tarde para um backend que guarde planos por ID.

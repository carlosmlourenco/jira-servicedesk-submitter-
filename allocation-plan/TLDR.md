# TL;DR — PIR (Project Initiation Request)

Ferramenta de pagina unica no browser (`index.html`) para planear a alocacao de
recursos de um projeto e submeter um **Project Initiation Request** ao Jira
Service Desk. Faz os calculos todos automaticamente.

## O que faz

- Defines o **projeto** (nome, data de inicio, duracao em semanas) e o
  **breakdown de horas por role** (10 roles visiveis + 5 atras de um toggle).
- **Suggest allocation** espalha essas horas pelas semanas em linhas de pessoas,
  seguindo as regras em `ALLOCATION-RULES.md` (caps de pessoas por role, tetos
  semanais, Business Analyst nas primeiras semanas, top-ups de manager, etc.).
  Tambem podes adicionar/editar pessoas manualmente.
- Por pessoa: Role, Allocation Type, Suggested Resource, Staffing Validation
  Status, Preferred Area (obrigatorio), Preferred Seniority e as horas semanais.
- Calcula Total Days, Total Hours e FTE; avisa quando sobram horas por alocar.
- **Download CSV** no formato "Request" (datas em ISO `yyyy-mm-dd`).
- **Share** gera um link que codifica o plano inteiro no URL (reabre sem
  servidor).
- **Submit PIR** envia para o Jira Service Desk atraves do backend local; em
  `file://` abre o portal do Jira e faz download do CSV como fallback.

## Como se usa

Abre `index.html` no browser para planear e exportar. Para o **Submit PIR** (Jira),
corre o backend local e abre a pagina servida:

```bash
cd server
python3 server.py            # serve http://localhost:8723/ (index.html)
```

A configuracao (IDs do service desk / request type, campos, OAuth) esta no
backend; ver `server/README.md`.

## Regras de alocacao

Documentadas (e mantidas em sincronia com o codigo) em `ALLOCATION-RULES.md`
(ingles) e `ALLOCATION-RULES-PT.md` (portugues).

## Privacidade

- Tokens e segredos ficam so no `.env` (git-ignored); nunca sao commitados.

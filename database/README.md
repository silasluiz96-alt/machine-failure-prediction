# Banco de Dados — Fase 2

## O que é isso?

Este arquivo descreve a estrutura do banco de dados que será usado na Fase 2 do projeto. O banco guarda o histórico de todas as consultas feitas à API — assim o gestor pode ver não só o risco atual de uma máquina, mas como esse risco evoluiu ao longo do tempo.

**Provedor:** [Supabase](https://supabase.com) (PostgreSQL gerenciado, plano gratuito)

---

## Tabela: `predictions`

Cada linha representa uma consulta feita à API. Seja uma consulta individual ou uma análise de várias máquinas de uma vez, tudo fica registrado aqui.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID | Identificador único gerado automaticamente |
| `created_at` | Timestamp | Data e hora da consulta |
| `machine_type` | Texto | Tipo do produto: `L`, `M` ou `H` |
| `temperatura_ar` | Número | Temperatura do ar em Kelvin |
| `temperatura_processo` | Número | Temperatura do processo em Kelvin |
| `velocidade_rotacao` | Número | Rotações por minuto |
| `torque` | Número | Torque em Newton-metro |
| `desgaste_ferramenta` | Número | Desgaste acumulado da ferramenta em minutos |
| `prediction` | Inteiro | `0` = normal, `1` = falha |
| `probability_failure` | Número | Probabilidade de falha (0 a 1) |
| `risk_level` | Texto | `LOW`, `MEDIUM`, `HIGH` ou `CRITICAL` |
| `source` | Texto | `single` (consulta individual) ou `batch` (lote) |
| `batch_id` | UUID | Agrupa todas as máquinas de uma análise em lote |

---

## Por que o `batch_id`?

Quando o gestor faz upload de uma planilha com 50 máquinas, todas elas são analisadas juntas. O `batch_id` é um código único que identifica esse grupo — assim dá para buscar "todas as máquinas analisadas na terça-feira" como um conjunto, não linha por linha.

---

## Arquitetura de segurança

```
Interface (HTML/JS)
        ↓
   FastAPI (Railway)       ← único ponto que acessa o banco
        ↓
   Supabase (PostgreSQL)   ← credenciais nunca expostas ao front-end
```

As credenciais do Supabase ficam como variáveis de ambiente no Railway — nunca no código e nunca no repositório.

---

## Endpoints da API que usam o banco

| Método | Rota | Ação no banco |
|---|---|---|
| `POST` | `/predict` | Salva 1 registro com `source = 'single'` |
| `POST` | `/predict/batch` | Salva N registros com mesmo `batch_id` |
| `GET` | `/history` | Retorna as últimas predições (a implementar) |

---

## Como aplicar o schema

1. Crie um projeto no [Supabase](https://supabase.com)
2. Acesse **SQL Editor** no painel
3. Cole o conteúdo de `schema.sql` e execute
4. Configure as variáveis de ambiente no Railway:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

> As instruções detalhadas de configuração serão adicionadas quando a integração for implementada.

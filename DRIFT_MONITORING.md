# Monitoramento de Drift — Plano de Manutenção do Modelo

## O que é drift

Um modelo de Machine Learning aprende padrões a partir de dados históricos. Com o tempo, o mundo real pode mudar — novos equipamentos, mudanças no processo produtivo, desgaste diferente das ferramentas — e os dados que chegam à API começam a ser diferentes do que o modelo viu durante o treinamento.

Quando isso acontece, a precisão do modelo cai silenciosamente. Sem monitoramento, ninguém percebe até que uma falha real passe despercebida.

Esse fenômeno tem um nome: **drift**.

---

## Dois tipos de drift relevantes para este projeto

### 1. Data drift (mudança nos sensores)
Os valores que chegam nos campos de entrada começam a fugir da distribuição que o modelo conhece.

**Exemplo:** a fábrica instalou um novo tipo de ferramenta que opera com torque médio de 65 Nm, mas o modelo foi treinado com torque médio de 42 Nm. O modelo vai continuar funcionando, mas com confiança menor.

**Como detectar:** comparar a distribuição média dos últimos 30 dias com a distribuição de treinamento. Se a média do torque subiu mais de 15%, sinal de alerta.

### 2. Concept drift (a relação entre sensores e falha mudou)
Os sensores continuam com os mesmos valores, mas o padrão de falha mudou — uma combinação de temperatura + velocidade que antes era segura agora causa falha.

**Como detectar:** monitorar a taxa de falhas reais confirmadas pela equipe de manutenção versus o que o modelo previu. Se a discrepância aumentar, o modelo precisa ser retreinado.

---

## Sinais de alerta para retreinamento

| Sinal | Limiar de ação |
|---|---|
| Média de qualquer sensor desvia > 15% da média de treinamento | Avaliar retreinamento |
| Taxa de falhas confirmadas > 2x a taxa histórica (2,8%) | Retreinar imediatamente |
| Recall estimado cai abaixo de 90% | Retreinar imediatamente |
| Passaram-se mais de 6 meses desde o último treino | Retreinamento preventivo |

---

## Plano de ação

```
1. A cada 30 dias:
   → Coletar distribuição dos inputs recebidos pela API
   → Comparar com distribuição de treinamento (média, desvio padrão)
   → Se desvio > 15% em qualquer feature: emitir alerta

2. A cada 90 dias (ou sob demanda):
   → Coletar feedback da equipe de manutenção
   → Cruzar predições do modelo com falhas reais ocorridas
   → Calcular recall real do período

3. Se retreinamento for necessário:
   → Adicionar novos dados ao dataset
   → Repetir pipeline: IQR → SMOTE → Grid Search → avaliar
   → Só substituir o modelo se as métricas melhorarem ou mantiverem
   → Atualizar version no metadata.pkl (ex: 1.0.0 → 1.1.0)
```

---

## Como simular a detecção localmente

O script `monitorar_drift.py` na raiz do projeto demonstra como comparar a distribuição de novos dados com a distribuição de treinamento:

```bash
python monitorar_drift.py
```

O script calcula o desvio percentual de cada sensor em relação ao treinamento e sinaliza quais estão fora da faixa aceitável.

---

## Por que isso importa

Modelos em produção sem monitoramento de drift são como balanças que não são calibradas — funcionam por um tempo, mas a leitura vai ficando errada aos poucos. Em manutenção industrial, um modelo degradado que deixa de detectar falhas tem custo direto: paradas não planejadas, danos ao equipamento e risco à segurança dos operadores.

O plano acima não exige ferramentas complexas — pode ser executado com pandas e uma planilha de acompanhamento. O importante é que exista um processo, não que seja automatizado desde o primeiro dia.

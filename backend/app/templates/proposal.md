# {{ content.title }}

{% if content.metadata %}
**Cliente:** {{ content.metadata.client_name }}  
**Setor:** {{ content.metadata.industry }}  
**Data:** {{ content.metadata.date_generated }}  
{% endif %}

## Contexto

{{ content.context }}

## Solução Proposta

{{ content.solution }}

## Escopo do Projeto

{{ content.scope }}

## Cronograma

{{ content.timeline }}

## Investimento

{{ content.investment }}

{% if content.differentials %}
## Diferenciais

{{ content.differentials }}
{% endif %}

{% if content.cases %}
## Casos de Sucesso

{{ content.cases }}
{% endif %}

---
*Proposta gerada por Propos4l - Sistema Inteligente de Automação de Propostas*

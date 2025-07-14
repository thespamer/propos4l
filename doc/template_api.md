# API de Templates do Propos4l

## Visão Geral

A API de Templates permite a geração, gerenciamento e utilização de templates para propostas. Os templates são criados a partir de PDFs de propostas existentes e podem ser usados para gerar novas propostas com estrutura consistente.

## Endpoints

### Criar Template

Cria um novo template a partir de um arquivo PDF de proposta.

**URL**: `/api/templates/`

**Método**: `POST`

**Formato**: `multipart/form-data`

**Parâmetros**:
- `name` (string, obrigatório): Nome do template
- `description` (string, opcional): Descrição do template
- `file` (file, obrigatório): Arquivo PDF da proposta

**Exemplo de Requisição**:
```bash
curl -X POST http://localhost:8000/api/templates/ \
  -F "name=Template de Consultoria" \
  -F "description=Template para propostas de consultoria de TI" \
  -F "file=@proposta_exemplo.pdf"
```

**Resposta de Sucesso**:
```json
{
  "id": 1,
  "name": "Template de Consultoria",
  "description": "Template para propostas de consultoria de TI",
  "creation_date": "2025-07-13T21:45:00",
  "structure": {
    "TITLE": {
      "id": 0,
      "required": true
    },
    "INTRODUCTION": {
      "id": 1,
      "required": false
    },
    "SOLUTION": {
      "id": 2,
      "required": true
    },
    "INVESTMENT": {
      "id": 3,
      "required": true
    }
  },
  "sections": [
    {
      "id": 1,
      "name": "TITLE",
      "content": "Proposta de Consultoria de TI",
      "order": 0,
      "metadata": {
        "source_position": 1,
        "confidence_score": 0.95
      }
    },
    {
      "id": 2,
      "name": "INTRODUCTION",
      "content": "Introdução da proposta...",
      "order": 1,
      "metadata": {
        "source_position": 2,
        "confidence_score": 0.85
      }
    }
  ]
}
```

### Listar Templates

Retorna uma lista de todos os templates disponíveis.

**URL**: `/api/templates/`

**Método**: `GET`

**Exemplo de Requisição**:
```bash
curl -X GET http://localhost:8000/api/templates/
```

**Resposta de Sucesso**:
```json
[
  {
    "id": 1,
    "name": "Template de Consultoria",
    "description": "Template para propostas de consultoria de TI",
    "creation_date": "2025-07-13T21:45:00",
    "structure": { ... },
    "sections": [ ... ]
  },
  {
    "id": 2,
    "name": "Template de Desenvolvimento",
    "description": "Template para propostas de desenvolvimento de software",
    "creation_date": "2025-07-13T22:00:00",
    "structure": { ... },
    "sections": [ ... ]
  }
]
```

### Obter Template Específico

Retorna os detalhes de um template específico.

**URL**: `/api/templates/{template_id}`

**Método**: `GET`

**Parâmetros de URL**:
- `template_id` (integer, obrigatório): ID do template

**Exemplo de Requisição**:
```bash
curl -X GET http://localhost:8000/api/templates/1
```

**Resposta de Sucesso**:
```json
{
  "id": 1,
  "name": "Template de Consultoria",
  "description": "Template para propostas de consultoria de TI",
  "creation_date": "2025-07-13T21:45:00",
  "structure": { ... },
  "sections": [ ... ]
}
```

### Excluir Template

Remove um template específico.

**URL**: `/api/templates/{template_id}`

**Método**: `DELETE`

**Parâmetros de URL**:
- `template_id` (integer, obrigatório): ID do template

**Exemplo de Requisição**:
```bash
curl -X DELETE http://localhost:8000/api/templates/1
```

**Resposta de Sucesso**:
- Código de status: `204 No Content`

## Fluxo de Trabalho

1. **Upload de PDF**: Faça upload de um PDF de proposta existente
2. **Geração de Template**: O sistema processa o PDF, identifica seções e cria um template
3. **Uso do Template**: O template pode ser usado para gerar novas propostas com estrutura consistente

## Integração com o Frontend

O frontend pode integrar com esses endpoints para permitir:
- Upload de PDFs e geração de templates
- Visualização e seleção de templates disponíveis
- Uso de templates para estruturar novas propostas

## Considerações Técnicas

- Os templates são armazenados no banco de dados PostgreSQL
- As seções são identificadas usando processamento de linguagem natural
- A estrutura do template é armazenada em formato JSON para flexibilidade
- Cada seção tem uma pontuação de confiança que indica a precisão da identificação

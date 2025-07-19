# Guia de Desenvolvimento e Manutenção

Este documento descreve os procedimentos de desenvolvimento e manutenção do sistema Propos4l.

## Migrações de Banco de Dados

O sistema utiliza Yoyo-migrations para gerenciar as migrações do banco de dados PostgreSQL. As migrações são armazenadas em `/backend/migrations/yoyo/`.

### Estrutura das Migrações

```
backend/
├── migrations/
│   └── yoyo/
│       └── 001_initial_schema.py
└── yoyo.ini
```

### Executando Migrações

As migrações são executadas automaticamente durante a inicialização do container `migrations`. Para executar manualmente:

```bash
# No container migrations
yoyo apply --database postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB} --all
```

### Criando Novas Migrações

Para criar uma nova migração:

1. Crie um novo arquivo em `migrations/yoyo/` seguindo o padrão de numeração (ex: `002_add_new_table.py`)
2. Defina as operações de migração e rollback usando SQL direto:

```python
"""
Descrição da migração
"""

from yoyo import step

__depends__ = {'001_initial_schema'}  # Dependências de outras migrações

steps = [
    step(
        # Apply migration
        """
        CREATE TABLE nova_tabela (
            id SERIAL PRIMARY KEY,
            nome VARCHAR NOT NULL
        );
        """,
        
        # Rollback migration
        """
        DROP TABLE IF EXISTS nova_tabela CASCADE;
        """
    )
]
```

### Boas Práticas

1. Use tipos VARCHAR em vez de ENUM para campos de status/tipo
2. Sempre forneça operações de rollback para cada migração
3. Documente claramente o propósito de cada migração
4. Use SQL direto para maior controle e previsibilidade
5. Mantenha as migrações idempotentes quando possível

### Troubleshooting

Se encontrar problemas com as migrações:

1. Verifique os logs do container migrations:
```bash
docker logs propos4l-migrations-1
```

2. Confirme que o banco de dados está acessível:
```bash
docker exec -it propos4l-db-1 psql -U postgres -d propos4l
```

3. Verifique o estado das migrações:
```bash
yoyo list --database postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
```

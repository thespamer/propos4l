# 📚 Documentação do Propos4l

Bem-vindo à documentação técnica do Propos4l. Esta documentação fornece uma visão detalhada da arquitetura, componentes e fluxos do sistema.

## 📑 Índice

### 1. [Operação do Sistema](./system_operation.md)
- Fluxo de operação geral
- Processamento de PDFs
- Geração de propostas
- Monitoramento em tempo real

### 2. [Diagramas de Classes](./class_diagram.md)
- Modelo de classes principal
- Classes do frontend
- Classes de serviços
- Relacionamentos e dependências

### 3. [Modelo de Banco de Dados](./database_model.md)
- Diagrama entidade-relacionamento
- Índices e constraints
- Modelo de vetores FAISS
- Estrutura de cache Redis

### 4. [Arquitetura Docker](./docker_compose.md)
- Dependências dos serviços
- Configuração dos containers
- Fluxo de build e deploy
- Volumes e persistência
- Monitoramento e logs

## 🔍 Guia Rápido

1. **Para desenvolvedores frontend**:
   - Comece com o diagrama de classes do frontend em [class_diagram.md](./class_diagram.md)
   - Veja o fluxo de operação em [system_operation.md](./system_operation.md)

2. **Para desenvolvedores backend**:
   - Explore o modelo de dados em [database_model.md](./database_model.md)
   - Veja a arquitetura de serviços em [class_diagram.md](./class_diagram.md)

3. **Para DevOps**:
   - Consulte a configuração Docker em [docker_compose.md](./docker_compose.md)
   - Veja o sistema de monitoramento no final de [docker_compose.md](./docker_compose.md)

## 🔄 Atualizando a Documentação

1. Os diagramas são escritos usando [Mermaid](https://mermaid-js.github.io/)
2. Para atualizar um diagrama:
   - Edite o arquivo markdown correspondente
   - Use a sintaxe Mermaid dentro dos blocos de código
   - Teste o diagrama no [Mermaid Live Editor](https://mermaid.live/)

## 📋 Convenções

- Todos os diagramas devem ter descrições claras
- Use emojis para melhor organização visual
- Mantenha os diagramas atualizados com o código
- Documente todas as alterações significativas

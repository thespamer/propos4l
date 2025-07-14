#!/bin/bash

# Cores para saída
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Teste de Saúde do Sistema Propos4l ===${NC}"
echo "Verificando a saúde dos serviços..."
echo ""

# Verificar se o backend está saudável
echo -e "${YELLOW}Verificando Backend (http://localhost:8000/health)...${NC}"
BACKEND_RESPONSE=$(curl -s http://localhost:8000/health)
BACKEND_STATUS=$(echo $BACKEND_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$BACKEND_STATUS" == "healthy" ]; then
    echo -e "${GREEN}✓ Backend está saudável!${NC}"
    echo -e "  Resposta: $BACKEND_RESPONSE"
else
    echo -e "${RED}✗ Backend não está saudável ou não respondeu!${NC}"
    echo -e "  Resposta: $BACKEND_RESPONSE"
fi

echo ""

# Verificar se o frontend está saudável
echo -e "${YELLOW}Verificando Frontend (http://localhost:3000/api/health)...${NC}"
FRONTEND_RESPONSE=$(curl -s http://localhost:3000/api/health)
FRONTEND_STATUS=$(echo $FRONTEND_RESPONSE | grep -o '"frontend":"[^"]*"' | cut -d'"' -f4)
BACKEND_VIA_FRONTEND=$(echo $FRONTEND_RESPONSE | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$FRONTEND_STATUS" == "healthy" ]; then
    echo -e "${GREEN}✓ Frontend está saudável!${NC}"
    
    if [ "$BACKEND_VIA_FRONTEND" == "healthy" ]; then
        echo -e "${GREEN}✓ Frontend consegue se comunicar com o Backend!${NC}"
    else
        echo -e "${RED}✗ Frontend não consegue se comunicar com o Backend!${NC}"
    fi
    
    echo -e "  Resposta: $FRONTEND_RESPONSE"
else
    echo -e "${RED}✗ Frontend não está saudável ou não respondeu!${NC}"
    echo -e "  Resposta: $FRONTEND_RESPONSE"
fi

echo ""
echo -e "${YELLOW}=== Teste de Comunicação entre Serviços ===${NC}"

# Testar se o frontend consegue acessar a API do backend
echo -e "Testando comunicação entre Frontend e Backend..."
TIMESTAMP=$(date +%s)
echo -e "  Timestamp do teste: $TIMESTAMP"

echo ""
echo -e "${YELLOW}=== Resumo do Teste ===${NC}"
if [ "$BACKEND_STATUS" == "healthy" ] && [ "$FRONTEND_STATUS" == "healthy" ] && [ "$BACKEND_VIA_FRONTEND" == "healthy" ]; then
    echo -e "${GREEN}✓ Todos os serviços estão saudáveis e se comunicando corretamente!${NC}"
else
    echo -e "${RED}✗ Há problemas com um ou mais serviços. Verifique os detalhes acima.${NC}"
fi

echo ""
echo "Teste concluído em $(date)"

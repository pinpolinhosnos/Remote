# Remote Control System

Sistema de controle remoto para operações de injection e cleaning, migrado do sistema local para web.

## Estrutura do Projeto

```
Remote/
├── agent/           # Agente local
│   ├── remote_agent.hpp
│   └── agent_main.cpp
├── backend/         # Servidor backend
│   ├── server.py
│   └── requirements.txt
├── frontend/        # Interface web
│   └── index.html
└── docs/           # Documentação
    └── README.md
```

## Funcionalidades

### 1. Agente Local (C++)
- **Conectividade**: Conexão persistente com servidor via sockets
- **Comandos suportados**:
  - `ping` - Teste de conexão
  - `inject` - Injeção de DLL (integração com injectSK.hpp)
  - `clean` - Limpeza de sistema (integração com Cleaner.hpp)
  - `status` - Status do agente
- **Persistência**: Reconexão automática em caso de falha

### 2. Servidor Backend (Python)
- **API HTTP**: Endpoints REST para controle
- **Socket Server**: Comunicação direta com agentes
- **Gerenciamento de Agentes**: Registro e monitoramento
- **Endpoints**:
  - `GET /api/agents` - Lista agentes conectados
  - `GET /api/status` - Status do servidor
  - `POST /api/command` - Envia comando específico
  - `POST /api/inject` - Comando de injeção
  - `POST /api/clean` - Comando de limpeza

### 3. Interface Web
- **Dashboard**: Visão geral dos agentes
- **Controle em tempo real**: Envio de comandos
- **Log de atividades**: Monitoramento de operações
- **Interface responsiva**: Funciona em desktop e mobile

## Configuração

### 1. Servidor Backend
```bash
cd Remote/backend
python server.py
```

O servidor iniciará em:
- Socket Server: `0.0.0.0:8080` (para agentes)
- HTTP API: `0.0.0.0:8081` (para interface web)

### 2. Agente Local
Compile o agente C++:
```bash
# Usando Visual Studio (projeto existente)
# Adicione os arquivos ao projeto Avom.vcxproj
```

Execute o agente:
```bash
agent.exe [server_ip] [server_port]
# Exemplo: agent.exe 192.168.1.100 8080
```

### 3. Interface Web
Abra no navegador:
```
http://localhost:8081
```

## Integração com Sistema Existente

### Injection
O agente se integra com `Inject/injectSK.hpp`:
- `loadEvom()` - Injeção via process hollowing
- `execgt()` - Criação de tarefa agendada
- `execsk()` - Execução imediata

### Cleaning
O agente se integra com `Cleaner/Cleaner.hpp`:
- `FlushAppcompatCache()` - Limpeza de cache de compatibilidade
- `FlushShimCache()` - Limpeza de cache shim
- `rundll32()` - Execução de comandos rundll32

## Protocolo de Comunicação

### Agente → Servidor
```
AGENT_CONNECTED                   // Conexão inicial
<command> [params]               // Comando recebido
```

### Servidor → Agente
```
{"status":"connected","agent_id":"...","commands":[...]}  // Resposta inicial
ACK: <command>                    // Confirmação
```

### API HTTP
```json
// Enviar comando
{
  "agent_id": "agent_192.168.1.100_8080",
  "command": "inject",
  "params": {
    "target": "msedge.exe",
    "method": "process_hollowing"
  }
}
```

## Segurança

**NOTA**: Este é um sistema de teste em ambiente sandbox.

### Considerações de Produção
1. **Autenticação**: Adicionar token-based auth
2. **Criptografia**: Usar TLS/SSL para comunicações
3. **Autorização**: Controle de acesso por usuário
4. **Logging**: Auditoria completa de operações
5. **Rate Limiting**: Prevenção de abuso

## Desenvolvimento Futuro

### Melhorias Planejadas
1. **WebSocket**: Comunicação bidirecional em tempo real
2. **Multi-tenancy**: Suporte a múltiplos usuários
3. **Plugin System**: Extensibilidade para novos comandos
4. **Dashboard Avançado**: Gráficos e métricas
5. **Mobile App**: Controle via aplicativo

### Integrações
1. **Notificações**: Email/Telegram para eventos importantes
2. **Backup**: Sistema de backup de configurações
3. **Auto-update**: Atualização automática do agente
4. **Health Checks**: Monitoramento de integridade

## Troubleshooting

### Problemas Comuns

1. **Agente não conecta**
   - Verifique firewall
   - Confirme IP/porta do servidor
   - Verifique se o servidor está rodando

2. **Comandos não executam**
   - Verifique permissões do agente
   - Confirme integração com DLLs
   - Verifique logs do agente

3. **Interface não carrega**
   - Verifique se API está rodando na porta 8081
   - Confirme CORS settings
   - Verifique console do navegador

### Logs
- Agente: Saída no console
- Servidor: Logs no terminal
- Interface: Console do navegador

## Licença

Sistema de teste para ambiente sandbox.
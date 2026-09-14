# Guia de Configuração - Sistema de Controle Remoto

## Visão Geral

Este guia explica como configurar e executar o sistema de controle remoto que substitui o sistema local de injection/cleaning.

## Passo 1: Preparar o Ambiente

### 1.1 Requisitos do Sistema

**Backend (Python):**
- Python 3.7+
- Permissões de rede
- Portas 8080 e 8081 disponíveis

**Agente (C++):**
- Visual Studio 2019+ (ou compilador C++17)
- Windows SDK
- Permissões administrativas (para injection)

**Frontend:**
- Navegador moderno (Chrome 80+, Firefox 75+, Edge 80+)
- JavaScript habilitado

### 1.2 Estrutura de Diretórios

Certifique-se de que a estrutura está assim:
```
bypassremote/
├── Remote/
│   ├── agent/
│   ├── backend/
│   ├── frontend/
│   └── docs/
├── Inject/          # Sistema original
├── Cleaner/         # Sistema original
└── ...              # Outros diretórios
```

## Passo 2: Configurar o Servidor Backend

### 2.1 Instalação do Python
```bash
# Verificar versão do Python
python --version

# Se não tiver Python, instale:
# https://www.python.org/downloads/
```

### 2.2 Executar o Servidor
```bash
# Navegar para o diretório do backend
cd c:\Users\yuri9\Downloads\bypassremote\Remote\backend

# Executar o servidor
python server.py
```

### 2.3 Verificar Servidor
O servidor deve mostrar:
```
Socket server listening on 0.0.0.0:8080
HTTP API server starting on port 8081
```

Teste a API:
```bash
# Em outro terminal
curl http://localhost:8081/api/status
# Deve retornar: {"status": "server_running", "version": "1.0"}
```

## Passo 3: Compilar o Agente Local

### 3.1 Integrar ao Projeto Visual Studio

1. Abra o projeto `Avom.vcxproj` no Visual Studio
2. Adicione os arquivos do agente:
   - `Remote/agent/remote_agent.hpp`
   - `Remote/agent/agent_main.cpp`

3. Configure as propriedades do projeto:
   - **Configuration Properties → C/C++ → General**
     - Additional Include Directories: Adicione `$(ProjectDir)Remote/agent`
   - **Configuration Properties → Linker → Input**
     - Additional Dependencies: Adicione `ws2_32.lib`

### 3.2 Alternativa: Compilar via Command Line
```bash
# Usando cl.exe (Visual Studio Command Prompt)
cl /EHsc /I. /I..\Remote\agent agent_main.cpp /link ws2_32.lib
```

### 3.3 Verificar Compilação
O executável `agent.exe` deve ser gerado.

## Passo 4: Executar o Sistema Completo

### 4.1 Iniciar Servidor
```bash
# Terminal 1 - Backend
cd Remote\backend
python server.py
```

### 4.2 Iniciar Agente
```bash
# Terminal 2 - Agente (como administrador)
agent.exe 127.0.0.1 8080
```

### 4.3 Acessar Interface Web
1. Abra o navegador
2. Acesse: `http://localhost:8081`
3. Ou abra diretamente: `Remote/frontend/index.html`

## Passo 5: Testar a Funcionalidade

### 5.1 Teste de Conexão
1. Na interface web, clique em "Refresh Agents"
2. Deve aparecer o agente conectado
3. Status deve mostrar "Server connected"

### 5.2 Teste de Comandos

**Teste de Ping:**
1. Selecione o agente
2. Escolha "Check Status" no Action Type
3. Clique em "Execute Command"
4. Verifique o log: "Command executed"

**Teste de Injection (Sandbox):**
1. Selecione o agente
2. Escolha "Inject DLL" no Action Type
3. Selecione "Microsoft Edge" como target
4. Clique em "Execute Command"
5. O agente deve processar o comando (sem executar em sandbox)

**Teste de Cleaning:**
1. Selecione o agente
2. Escolha "Clean System" no Action Type
3. Selecione "All Caches"
4. Clique em "Execute Command"

## Passo 6: Configuração Avançada

### 6.1 Múltiplos Agentes
Para executar múltiplos agentes:
```bash
# Em diferentes terminais/computadores
agent.exe <server_ip> 8080
```

### 6.2 Servidor em Rede
Para acesso remoto:
```bash
# Iniciar servidor com IP específico
python server.py --host 0.0.0.0 --port 8080

# Agentes se conectam com IP do servidor
agent.exe 192.168.1.100 8080
```

### 6.3 Configuração de Firewall
Permitir portas no firewall:
```powershell
# PowerShell como administrador
New-NetFirewallRule -DisplayName "Remote Control API" -Direction Inbound -Protocol TCP -LocalPort 8081 -Action Allow
New-NetFirewallRule -DisplayName "Remote Control Socket" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

## Passo 7: Solução de Problemas

### 7.1 Problemas Comuns

**Agente não conecta:**
```bash
# Verificar se servidor está rodando
netstat -an | findstr :8080

# Testar conexão manual
telnet localhost 8080
```

**API não responde:**
```bash
# Verificar processo Python
tasklist | findstr python

# Reiniciar servidor
# Pressione Ctrl+C no terminal do servidor
python server.py
```

**Interface não carrega:**
- Verifique console do navegador (F12)
- Confirme que está acessando `http://localhost:8081`
- Verifique se há erros de CORS

### 7.2 Logs e Depuração

**Servidor:** Logs no terminal onde foi executado
**Agente:** Saída no console do agente
**Interface:** Console do navegador (F12 → Console)

### 7.3 Reinicialização Completa
```bash
# 1. Parar servidor (Ctrl+C no terminal)
# 2. Parar agentes (Ctrl+C nos terminais)
# 3. Iniciar servidor
python server.py
# 4. Iniciar agentes
agent.exe 127.0.0.1 8080
```

## Passo 8: Migração do Sistema Local

### 8.1 Integração com Código Existente
Os arquivos originais permanecem em:
- `Inject/` - Lógica de injection
- `Cleaner/` - Lógica de cleaning

O sistema remoto chama essas funções através do agente.

### 8.2 Manutenção
- Atualizações no código de injection/cleaning: Modificar arquivos em `Inject/` e `Cleaner/`
- Atualizações no sistema remoto: Modificar arquivos em `Remote/`

### 8.3 Backup
```bash
# Backup da configuração
copy Remote\backend\config.json Remote\backend\config.json.backup
copy Remote\agent\*.hpp Remote\agent\*.hpp.backup
```

## Conclusão

O sistema agora está configurado para controle remoto via web. A interface permite:

1. Monitorar agentes conectados
2. Executar comandos de injection remotamente
3. Executar comandos de cleaning remotamente
4. Visualizar logs em tempo real

**Próximos passos:**
- Testar em ambiente real (fora do sandbox)
- Implementar autenticação
- Adicionar criptografia
- Desenvolver recursos avançados

Lembre-se: Este é um sistema de teste em ambiente sandbox.
# BMAD MCP Architecture - Dauerhafte Lösung

## Problem-Analyse
- MCP Server läuft auf Railway, aber Tool-Aufrufe schlagen fehl
- State-Management zwischen Client/Server inkonsistent
- API-Argument-Format-Probleme (Python Dict vs JSON)
- Agent-Aktivierung schlägt fehl obwohl Agent bereits läuft

## Architektur-Lösung

### 1. Robuste MCP Server Implementation

```typescript
// bmad-mcp-server.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

class BMADMCPServer {
  private server: Server;
  private agentStates: Map<string, AgentState> = new Map();
  
  constructor() {
    this.server = new Server(
      { name: "bmad", version: "2.0.0" },
      { capabilities: { tools: {}, resources: {} } }
    );
    this.setupErrorHandling();
    this.setupStateManagement();
  }

  private setupErrorHandling() {
    this.server.setRequestHandler(
      { method: "tools/call" },
      async (request) => {
        try {
          return await this.handleToolCall(request);
        } catch (error) {
          return this.createErrorResponse(error);
        }
      }
    );
  }

  private async handleToolCall(request: any) {
    const { name, arguments: args } = request.params;
    
    // Normalize arguments - handle both {} and empty
    const normalizedArgs = args || {};
    
    switch (name) {
      case "list_agents":
        return this.listAgents(normalizedArgs);
      case "bmad_activate_agent":
        return this.activateAgent(normalizedArgs);
      case "execute_task":
        return this.executeTask(normalizedArgs);
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  }

  private async listAgents(args: any) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            agents: [
              { id: "architect", name: "Winston", status: "available" },
              { id: "developer", name: "Dev", status: "available" },
              { id: "analyst", name: "Ana", status: "available" }
            ]
          })
        }
      ]
    };
  }

  private async activateAgent(args: any) {
    const { agent_id } = args;
    
    // Idempotent activation - check if already active
    if (this.agentStates.has(agent_id)) {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            status: "already_active",
            agent_id,
            message: "Agent is already active"
          })
        }]
      };
    }

    // Activate agent
    this.agentStates.set(agent_id, {
      id: agent_id,
      status: "active",
      activated_at: new Date().toISOString()
    });

    return {
      content: [{
        type: "text", 
        text: JSON.stringify({
          status: "activated",
          agent_id,
          message: "Agent successfully activated"
        })
      }]
    };
  }

  private createErrorResponse(error: any) {
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          error: true,
          message: error.message,
          type: error.constructor.name
        })
      }]
    };
  }
}

interface AgentState {
  id: string;
  status: "active" | "inactive";
  activated_at: string;
}
```

### 2. Railway Deployment Configuration

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .

# Health check endpoint
EXPOSE 3000
CMD ["npm", "start"]
```

```yaml
# railway.toml
[build]
  builder = "DOCKERFILE"

[deploy]
  healthcheckPath = "/health"
  healthcheckTimeout = 300
  restartPolicyType = "ON_FAILURE"

[env]
  NODE_ENV = "production"
  PORT = "3000"
```

### 3. Kilo Code Integration Fix

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "bmad": {
      "command": "node",
      "args": [
        "C:/path/to/bmad-mcp-client.js",
        "--server-url", "https://your-railway-app.up.railway.app"
      ],
      "env": {
        "BMAD_API_KEY": "your-api-key"
      }
    }
  }
}
```

```javascript
// bmad-mcp-client.js - Robust Client
class BMADMCPClient {
  constructor(serverUrl) {
    this.serverUrl = serverUrl;
    this.retryConfig = { maxRetries: 3, backoff: 1000 };
  }

  async callTool(name, args = {}) {
    for (let attempt = 1; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        const response = await fetch(`${this.serverUrl}/tools/call`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            method: "tools/call",
            params: { name, arguments: args }
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
      } catch (error) {
        if (attempt === this.retryConfig.maxRetries) throw error;
        await this.sleep(this.retryConfig.backoff * attempt);
      }
    }
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### 4. State Synchronization Pattern

```typescript
// state-manager.ts
export class BMADStateManager {
  private static instance: BMADStateManager;
  private agentStates: Map<string, AgentState> = new Map();
  private observers: Set<StateObserver> = new Set();

  static getInstance(): BMADStateManager {
    if (!BMADStateManager.instance) {
      BMADStateManager.instance = new BMADStateManager();
    }
    return BMADStateManager.instance;
  }

  async syncState() {
    // Periodic state sync with Railway server
    try {
      const response = await fetch(`${process.env.RAILWAY_URL}/agent-states`);
      const serverStates = await response.json();
      
      // Merge states
      for (const [agentId, state] of Object.entries(serverStates)) {
        this.agentStates.set(agentId, state as AgentState);
      }
      
      this.notifyObservers();
    } catch (error) {
      console.error('State sync failed:', error);
    }
  }

  registerObserver(observer: StateObserver) {
    this.observers.add(observer);
  }

  private notifyObservers() {
    this.observers.forEach(observer => observer.onStateChange(this.agentStates));
  }
}
```

## Implementation Steps

1. **Server Update**: Deploy neue MCP Server Version auf Railway
2. **Client Update**: Update Kilo Code MCP Client mit Retry-Logic
3. **State Sync**: Implement persistent state management
4. **Health Monitoring**: Add Railway health checks
5. **Error Recovery**: Graceful degradation bei Connection-Loss

## Test Plan

```bash
# 1. Test Tool Calls
curl -X POST https://your-railway-app.up.railway.app/tools/call \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"list_agents","arguments":{}}}'

# 2. Test Agent Activation (Idempotent)
curl -X POST https://your-railway-app.up.railway.app/tools/call \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"bmad_activate_agent","arguments":{"agent_id":"architect"}}}'

# 3. Test State Persistence
curl https://your-railway-app.up.railway.app/agent-states
```

## Performance Optimizations

- **Connection Pooling**: Für Railway API calls
- **Caching**: Agent states lokal cachen
- **Compression**: Gzip für API responses
- **Rate Limiting**: Prevent API abuse

Dies löst das Problem dauerhaft durch:
- ✅ Idempotente Agent-Aktivierung
- ✅ Robuste Error-Behandlung  
- ✅ State-Synchronization
- ✅ Railway-optimierte Deployment
- ✅ Retry-Logic für Network-Issues
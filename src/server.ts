import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import express from 'express';

interface AgentState {
  id: string;
  status: "active" | "inactive";
  activated_at: string;
  metadata?: any;
}

class BMADMCPServer {
  private server: Server;
  private agentStates: Map<string, AgentState> = new Map();
  private app: express.Application;
  
  constructor() {
    this.server = new Server(
      { name: "bmad", version: "2.1.0" },
      { capabilities: { tools: {}, resources: {} } }
    );
    this.app = express();
    this.setupMiddleware();
    this.setupRoutes();
    this.setupMCPHandlers();
    this.setupErrorHandling();
  }

  private setupMiddleware() {
    this.app.use(express.json());
    this.app.use((_req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
      next();
    });
  }

  private setupRoutes() {
    // Health check for Railway
    this.app.get('/health', (_req, res) => {
      res.json({ 
        status: 'healthy',
        service: 'bmad-mcp-server',
        version: '2.1.1',
        timestamp: process.hrtime()[0] + process.hrtime()[1] / 1e9,
        deployment: 'railway',
        activeAgents: this.agentStates.size
      });
    });

    // Agent states endpoint
    this.app.get('/agent-states', (_req, res) => {
      const states = Object.fromEntries(this.agentStates);
      res.json(states);
    });

    // Tool call endpoint for HTTP clients
    this.app.post('/tools/call', async (req, res) => {
      try {
        const result = await this.handleToolCall(req.body);
        res.json(result);
      } catch (error) {
        res.status(500).json(this.createErrorResponse(error));
      }
    });
  }

  private setupMCPHandlers() {
    // List available tools
    this.server.setRequestHandler(
      { method: "tools/list" } as any,
      async () => ({
        tools: [
          {
            name: "list_agents",
            description: "List all available BMAD agents",
            inputSchema: {
              type: "object",
              properties: {},
              additionalProperties: false
            }
          },
          {
            name: "bmad_activate_agent",
            description: "Activate a specific BMAD agent (idempotent)",
            inputSchema: {
              type: "object",
              properties: {
                agent_id: { type: "string", description: "ID of the agent to activate" },
                config: { type: "object", description: "Optional agent configuration" }
              },
              required: ["agent_id"],
              additionalProperties: false
            }
          },
          {
            name: "execute_task",
            description: "Execute a task with specified agent",
            inputSchema: {
              type: "object",
              properties: {
                agent_id: { type: "string", description: "Agent to execute task with" },
                task: { type: "string", description: "Task to execute" },
                parameters: { type: "object", description: "Task parameters" }
              },
              required: ["agent_id", "task"],
              additionalProperties: false
            }
          },
          {
            name: "get_agent_status",
            description: "Get status of specific agent",
            inputSchema: {
              type: "object",
              properties: {
                agent_id: { type: "string", description: "Agent ID to check" }
              },
              required: ["agent_id"],
              additionalProperties: false
            }
          }
        ]
      })
    );

    // Handle tool calls
    this.server.setRequestHandler(
      { method: "tools/call" } as any,
      async (request: any) => {
        try {
          return await this.handleToolCall(request.params);
        } catch (error) {
          return this.createErrorResponse(error);
        }
      }
    );
  }

  private async handleToolCall(params: any) {
    const { name, arguments: args } = params;
    
    // Normalize arguments - handle both {} and empty/undefined
    const normalizedArgs = args || {};
    
    console.log(`[BMAD] Tool call: ${name}`, normalizedArgs);
    
    switch (name) {
      case "list_agents":
        return this.listAgents(normalizedArgs);
      case "bmad_activate_agent":
        return this.activateAgent(normalizedArgs);
      case "execute_task":
        return this.executeTask(normalizedArgs);
      case "get_agent_status":
        return this.getAgentStatus(normalizedArgs);
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  }

  private async listAgents(_args: any) {
    const agents = [
      { 
        id: "architect", 
        name: "Winston", 
        title: "System Architect",
        status: this.agentStates.get("architect")?.status || "available",
        capabilities: ["system-design", "architecture", "technical-planning"]
      },
      { 
        id: "developer", 
        name: "Dev", 
        title: "Senior Developer",
        status: this.agentStates.get("developer")?.status || "available",
        capabilities: ["coding", "implementation", "debugging"]
      },
      { 
        id: "analyst", 
        name: "Ana", 
        title: "Business Analyst",
        status: this.agentStates.get("analyst")?.status || "available",
        capabilities: ["analysis", "requirements", "documentation"]
      },
      { 
        id: "pm", 
        name: "Patricia", 
        title: "Project Manager",
        status: this.agentStates.get("pm")?.status || "available",
        capabilities: ["project-management", "coordination", "planning"]
      },
      { 
        id: "qa", 
        name: "Quinn", 
        title: "QA Engineer",
        status: this.agentStates.get("qa")?.status || "available",
        capabilities: ["testing", "quality-assurance", "validation"]
      }
    ];

    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          success: true,
          agents,
          total_agents: agents.length,
          active_agents: Array.from(this.agentStates.values()).filter(a => a.status === "active").length
        }, null, 2)
      }]
    };
  }

  private async activateAgent(args: any) {
    const { agent_id, config } = args;
    
    if (!agent_id) {
      throw new Error("agent_id is required");
    }

    // Check if agent exists
    const validAgents = ["architect", "developer", "analyst", "pm", "qa"];
    if (!validAgents.includes(agent_id)) {
      throw new Error(`Invalid agent_id: ${agent_id}. Valid agents: ${validAgents.join(", ")}`);
    }

    // Idempotent activation - check if already active
    const existingState = this.agentStates.get(agent_id);
    if (existingState && existingState.status === "active") {
      return {
        content: [{
          type: "text",
          text: JSON.stringify({
            success: true,
            status: "already_active",
            agent_id,
            message: `Agent '${agent_id}' is already active`,
            activated_at: existingState.activated_at
          }, null, 2)
        }]
      };
    }

    // Activate agent with new state
    const newState: AgentState = {
      id: agent_id,
      status: "active",
      activated_at: new Date().toISOString(),
      metadata: config || {}
    };

    this.agentStates.set(agent_id, newState);

    console.log(`[BMAD] Agent activated: ${agent_id}`);

    return {
      content: [{
        type: "text", 
        text: JSON.stringify({
          success: true,
          status: "activated",
          agent_id,
          message: `Agent '${agent_id}' successfully activated`,
          activated_at: newState.activated_at,
          config: newState.metadata
        }, null, 2)
      }]
    };
  }

  private async executeTask(args: any) {
    const { agent_id, task, parameters } = args;
    
    if (!agent_id || !task) {
      throw new Error("agent_id and task are required");
    }

    // Check if agent is active
    const agentState = this.agentStates.get(agent_id);
    if (!agentState || agentState.status !== "active") {
      throw new Error(`Agent '${agent_id}' is not active. Please activate first.`);
    }

    // Simulate task execution (replace with actual agent logic)
    const taskResult = {
      task_id: `task_${Date.now()}`,
      agent_id,
      task,
      parameters: parameters || {},
      status: "completed",
      result: `Task '${task}' executed successfully by agent '${agent_id}'`,
      executed_at: new Date().toISOString()
    };

    console.log(`[BMAD] Task executed:`, taskResult);

    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          success: true,
          ...taskResult
        }, null, 2)
      }]
    };
  }

  private async getAgentStatus(args: any) {
    const { agent_id } = args;
    
    if (!agent_id) {
      throw new Error("agent_id is required");
    }

    const agentState = this.agentStates.get(agent_id);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          success: true,
          agent_id,
          status: agentState?.status || "inactive",
          activated_at: agentState?.activated_at || null,
          metadata: agentState?.metadata || {}
        }, null, 2)
      }]
    };
  }

  private createErrorResponse(error: any) {
    console.error(`[BMAD] Error:`, error);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          success: false,
          error: true,
          message: error.message || "Unknown error occurred",
          type: error.constructor.name,
          timestamp: new Date().toISOString()
        }, null, 2)
      }]
    };
  }

  private setupErrorHandling() {
    process.on('uncaughtException', (error) => {
      console.error('[BMAD] Uncaught Exception:', error);
    });

    process.on('unhandledRejection', (reason, promise) => {
      console.error('[BMAD] Unhandled Rejection at:', promise, 'reason:', reason);
    });
  }

  public async start() {
    const port = process.env.PORT || 3000;
    
    // Start HTTP server for Railway
    this.app.listen(port, () => {
      console.log(`[BMAD] HTTP Server running on port ${port}`);
      console.log(`[BMAD] Health check: http://localhost:${port}/health`);
    });

    // Start MCP server for stdio transport
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.log('[BMAD] MCP Server connected via stdio');
  }
}

// Start server
const server = new BMADMCPServer();
server.start().catch(console.error);

export default BMADMCPServer;
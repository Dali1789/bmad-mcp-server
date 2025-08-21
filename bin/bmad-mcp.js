#!/usr/bin/env node

import fetch from 'node-fetch';

const RAILWAY_URL = process.env.BMAD_RAILWAY_URL || 'https://bmad-mcp-server-production.up.railway.app';

async function main() {
  const command = process.argv[2] || 'help';
  
  try {
    switch (command) {
      case 'status':
        await getStatus();
        break;
      case 'health':
        await getHealth();
        break;
      case 'agents':
        await listAgents();
        break;
      case 'activate':
        const agentId = process.argv[3];
        if (!agentId) {
          console.error('Usage: bmad-mcp activate <agent-id>');
          process.exit(1);
        }
        await activateAgent(agentId);
        break;
      case 'help':
      default:
        showHelp();
        break;
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

async function getStatus() {
  console.log('🔍 Checking BMAD MCP Server status...');
  
  const response = await fetch(`${RAILWAY_URL}/health`);
  if (!response.ok) {
    throw new Error(`Server returned ${response.status}`);
  }
  
  const data = await response.json();
  console.log('✅ Server Status:', JSON.stringify(data, null, 2));
}

async function getHealth() {
  console.log('🏥 Health check...');
  
  const response = await fetch(`${RAILWAY_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  
  const data = await response.json();
  console.log(`✅ ${data.service} v${data.version} - ${data.status}`);
  console.log(`📊 Active Agents: ${data.activeAgents}`);
}

async function listAgents() {
  console.log('👥 Listing available agents...');
  
  const response = await fetch(`${RAILWAY_URL}/tools/call`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'list_agents',
      arguments: {}
    })
  });
  
  if (!response.ok) {
    throw new Error(`Failed to list agents: ${response.status}`);
  }
  
  const data = await response.json();
  const result = JSON.parse(data.content[0].text);
  
  console.log('✅ Available Agents:');
  result.agents.forEach(agent => {
    const statusIcon = agent.status === 'active' ? '🟢' : '⚪';
    console.log(`  ${statusIcon} ${agent.id} (${agent.name}) - ${agent.title}`);
  });
}

async function activateAgent(agentId) {
  console.log(`🚀 Activating agent: ${agentId}...`);
  
  const response = await fetch(`${RAILWAY_URL}/tools/call`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'bmad_activate_agent',
      arguments: { agent_id: agentId }
    })
  });
  
  if (!response.ok) {
    throw new Error(`Failed to activate agent: ${response.status}`);
  }
  
  const data = await response.json();
  const result = JSON.parse(data.content[0].text);
  
  if (result.success) {
    console.log(`✅ Agent '${agentId}' activated successfully!`);
  } else {
    throw new Error(result.message || 'Activation failed');
  }
}

function showHelp() {
  console.log(`
🏗️ BMAD MCP CLI v2.1.1

Usage: bmad-mcp <command>

Commands:
  status     Show server status and health
  health     Quick health check
  agents     List all available agents
  activate   Activate an agent
  help       Show this help message

Examples:
  bmad-mcp status
  bmad-mcp agents
  bmad-mcp activate architect

Environment Variables:
  BMAD_RAILWAY_URL   Custom Railway deployment URL
                     Default: ${RAILWAY_URL}
`);
}

main().catch(console.error);
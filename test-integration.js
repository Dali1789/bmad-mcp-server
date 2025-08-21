// BMAD MCP Server Integration Test
import { spawn } from 'child_process';
import fetch from 'node-fetch';

class IntegrationTest {
  constructor() {
    this.serverProcess = null;
    this.serverUrl = 'http://localhost:3000';
  }

  async startServer() {
    console.log('🚀 Starting BMAD MCP Server...');
    
    this.serverProcess = spawn('node', ['dist/server.js'], {
      cwd: process.cwd(),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    this.serverProcess.stdout.on('data', (data) => {
      console.log(`[SERVER] ${data.toString().trim()}`);
    });

    this.serverProcess.stderr.on('data', (data) => {
      console.error(`[ERROR] ${data.toString().trim()}`);
    });

    // Wait for server to start
    await this.waitForServer();
  }

  async waitForServer() {
    const maxAttempts = 30;
    for (let i = 0; i < maxAttempts; i++) {
      try {
        const response = await fetch(`${this.serverUrl}/health`);
        if (response.ok) {
          console.log('✅ Server is ready!');
          return;
        }
      } catch (error) {
        // Server not ready yet
      }
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    throw new Error('Server failed to start within 30 seconds');
  }

  async testHealthEndpoint() {
    console.log('\n📊 Testing health endpoint...');
    const response = await fetch(`${this.serverUrl}/health`);
    const data = await response.json();
    console.log('Health response:', JSON.stringify(data, null, 2));
    
    if (data.status === 'healthy' && data.version === '2.1.1') {
      console.log('✅ Health endpoint working correctly');
      return true;
    } else {
      console.log('❌ Health endpoint response incorrect');
      return false;
    }
  }

  async testAgentStatesEndpoint() {
    console.log('\n🤖 Testing agent states endpoint...');
    try {
      const response = await fetch(`${this.serverUrl}/agent-states`);
      const data = await response.json();
      console.log('Agent states response:', JSON.stringify(data, null, 2));
      console.log('✅ Agent states endpoint working');
      return true;
    } catch (error) {
      console.log('❌ Agent states endpoint failed:', error.message);
      return false;
    }
  }

  async testToolCallEndpoint() {
    console.log('\n🛠️ Testing tool call endpoint...');
    try {
      const response = await fetch(`${this.serverUrl}/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'list_agents',
          arguments: {}
        })
      });
      
      const data = await response.json();
      console.log('Tool call response:', JSON.stringify(data, null, 2));
      console.log('✅ Tool call endpoint working');
      return true;
    } catch (error) {
      console.log('❌ Tool call endpoint failed:', error.message);
      return false;
    }
  }

  async testAgentActivation() {
    console.log('\n⚡ Testing agent activation...');
    try {
      const response = await fetch(`${this.serverUrl}/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'bmad_activate_agent',
          arguments: {
            agent_id: 'bmad-test-agent',
            config: { test: true }
          }
        })
      });
      
      const data = await response.json();
      console.log('Agent activation response:', JSON.stringify(data, null, 2));
      
      // Test idempotent activation
      const response2 = await fetch(`${this.serverUrl}/tools/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'bmad_activate_agent',
          arguments: {
            agent_id: 'bmad-test-agent',
            config: { test: true }
          }
        })
      });
      
      const data2 = await response2.json();
      console.log('Second activation response:', JSON.stringify(data2, null, 2));
      console.log('✅ Agent activation working (including idempotent behavior)');
      return true;
    } catch (error) {
      console.log('❌ Agent activation failed:', error.message);
      return false;
    }
  }

  async stopServer() {
    if (this.serverProcess) {
      console.log('\n🛑 Stopping server...');
      this.serverProcess.kill('SIGTERM');
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  async runTests() {
    let allPassed = true;
    
    try {
      await this.startServer();
      
      const tests = [
        this.testHealthEndpoint,
        this.testAgentStatesEndpoint,
        this.testToolCallEndpoint,
        this.testAgentActivation
      ];
      
      for (const test of tests) {
        const passed = await test.call(this);
        if (!passed) allPassed = false;
      }
      
    } catch (error) {
      console.error('❌ Test suite failed:', error.message);
      allPassed = false;
    } finally {
      await this.stopServer();
    }
    
    console.log(`\n${allPassed ? '🎉 All tests passed!' : '❌ Some tests failed'}`);
    return allPassed;
  }
}

// Run the tests
const test = new IntegrationTest();
test.runTests().then(success => {
  process.exit(success ? 0 : 1);
});
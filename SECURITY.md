# Security Policy

## Supported Versions

We actively support the following versions of BMAD MCP Server with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.x.x   | :white_check_mark: |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow our responsible disclosure process:

### 🔒 Private Reporting

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead, please report security issues privately:

1. **Email**: Send details to `security@bmad-project.com`
2. **Subject Line**: "[SECURITY] Brief description of the issue"
3. **Include**:
   - Detailed description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Suggested fixes (if any)

### ⏱️ Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix Development**: Depends on severity (1-30 days)
- **Public Disclosure**: After fix is released and users have time to update

### 🏆 Security Hall of Fame

We recognize security researchers who help improve BMAD's security:

- Responsible disclosure contributors will be credited (with permission)
- Acknowledgment in release notes and documentation
- Priority support for future security research

## Security Best Practices

### 🔐 API Key Management

#### Required Practices
- **Environment Variables Only**: Never hardcode API keys in source code
- **Secure Storage**: Use secure secret management systems in production
- **Regular Rotation**: Rotate API keys periodically
- **Least Privilege**: Use keys with minimal required permissions

#### Example Secure Configuration
```bash
# ✅ Correct: Environment variables
OPENROUTER_API_KEY=sk-or-v1-xxx
NOTION_TOKEN=secret_xxx

# ❌ Incorrect: Hardcoded in code
api_key = "sk-or-v1-xxx"  # NEVER DO THIS
```

### 🔒 Authentication & Authorization

#### MCP Server Security
- **Input Validation**: All user inputs are validated and sanitized
- **Type Safety**: Strict type checking with Pydantic models
- **Error Handling**: No sensitive information in error messages
- **Session Management**: Secure session handling for web interfaces

#### API Security
- **Rate Limiting**: Prevent abuse with appropriate rate limits
- **HTTPS Only**: All API communications over HTTPS in production
- **Token Validation**: Proper validation of all authentication tokens

### 🛡️ Data Protection

#### Personal Data
- **Minimal Collection**: Only collect necessary data
- **Encryption at Rest**: Sensitive data encrypted in storage
- **Encryption in Transit**: All communications encrypted
- **Data Retention**: Clear data retention and deletion policies

#### Task Data Security
- **Local Storage**: Task data stored locally by default
- **Optional Sync**: Notion sync is optional and user-controlled
- **Access Control**: User-specific data isolation
- **Backup Security**: Secure backup procedures

### 🐳 Docker Security

#### Container Security
```dockerfile
# Use non-root user
RUN adduser --disabled-password --gecos '' bmad
USER bmad

# Minimal base image
FROM python:3.11-slim

# Security updates
RUN apt-get update && apt-get upgrade -y
```

#### Production Deployment
```yaml
# docker-compose.yml security
services:
  bmad-mcp-server:
    read_only: true
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETUID
      - SETGID
```

### 🔍 Monitoring & Logging

#### Security Monitoring
- **Access Logging**: Log all API access attempts
- **Error Monitoring**: Monitor for suspicious error patterns
- **Performance Monitoring**: Detect potential DoS attacks
- **Audit Trails**: Maintain audit logs for compliance

#### Log Security
- **No Sensitive Data**: Never log API keys, tokens, or personal data
- **Structured Logging**: Use structured logs for better analysis
- **Log Rotation**: Implement proper log rotation and retention
- **Secure Storage**: Store logs securely with appropriate access controls

## Vulnerability Assessment

### Known Security Considerations

#### Dependencies
- **Regular Updates**: Dependencies are regularly updated
- **Vulnerability Scanning**: Automated scanning with `safety` and `bandit`
- **Supply Chain**: Verify dependency integrity and sources

#### Network Security
- **Firewall Rules**: Properly configure firewall rules
- **Network Segmentation**: Isolate BMAD services appropriately
- **VPN Access**: Use VPN for remote administrative access

### Security Testing

#### Automated Testing
```bash
# Security linting
bandit -r src/

# Dependency vulnerability check
safety check

# Code quality and security
flake8 --select=E,W,F,C,N src/
```

#### Manual Testing
- Regular penetration testing
- Code reviews with security focus
- Third-party security assessments

## Compliance

### Data Protection Regulations
- **GDPR Compliance**: European data protection compliance
- **Privacy by Design**: Security and privacy built into system design
- **Data Minimization**: Collect only necessary data
- **User Rights**: Support for data access, correction, and deletion

### Industry Standards
- **OWASP Guidelines**: Follow OWASP security best practices
- **ISO 27001**: Information security management principles
- **SOC 2**: Security controls for service organizations

## Incident Response

### Security Incident Process

1. **Detection**: Identify potential security incident
2. **Assessment**: Evaluate severity and impact
3. **Containment**: Limit damage and prevent spread
4. **Investigation**: Determine root cause and scope
5. **Recovery**: Restore normal operations securely
6. **Lessons Learned**: Update security measures

### Communication Plan
- **Internal Team**: Immediate notification to security team
- **Users**: Transparent communication about impacts
- **Authorities**: Report to relevant authorities if required
- **Public**: Coordinated public disclosure after resolution

## Security Updates

### Update Process
1. **Security Patch Development**: Develop and test fixes
2. **Release Planning**: Coordinate release timeline
3. **User Notification**: Notify users of critical updates
4. **Documentation**: Update security documentation
5. **Verification**: Verify fix effectiveness

### Emergency Updates
- **Critical Vulnerabilities**: Emergency releases within 24-48 hours
- **Hotfix Process**: Streamlined process for urgent fixes
- **Rollback Plan**: Quick rollback if issues arise

## Security Configuration

### Production Security Checklist

- [ ] **API Keys**: All keys stored in environment variables
- [ ] **HTTPS**: All communications over HTTPS
- [ ] **Firewall**: Proper firewall configuration
- [ ] **Updates**: All dependencies updated to latest secure versions
- [ ] **Monitoring**: Security monitoring and alerting configured
- [ ] **Backups**: Secure backup and recovery procedures
- [ ] **Access Control**: Proper user access management
- [ ] **Audit Logging**: Comprehensive audit trail enabled

### Development Security

- [ ] **Pre-commit Hooks**: Security checks in pre-commit hooks
- [ ] **Dependency Scanning**: Regular dependency vulnerability scans
- [ ] **Code Review**: Security-focused code reviews
- [ ] **Testing**: Security tests in CI/CD pipeline
- [ ] **Secrets Detection**: Automated secrets detection
- [ ] **Documentation**: Security documentation up to date

## Contact Information

### Security Team
- **Email**: security@bmad-project.com
- **PGP Key**: Available on request
- **Response Time**: 48 hours maximum for initial response

### General Security Questions
- **Documentation**: Review this security policy
- **Community**: GitHub Discussions for general security questions
- **Support**: Regular support channels for non-security issues

---

**Security is a shared responsibility. Thank you for helping keep BMAD secure!** 🔒
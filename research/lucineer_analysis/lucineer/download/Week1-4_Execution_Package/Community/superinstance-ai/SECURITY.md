# Security Policy

## Supported Versions

We actively support the following versions of the SuperInstance SDK with security updates:

| Version | Supported          | End of Support |
| ------- | ------------------ | -------------- |
| 1.0.x   | :white_check_mark: | Active         |
| < 1.0   | :x:                | N/A            |

We recommend always using the latest stable release to ensure you have the most recent security patches.

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in SuperInstance.AI, please report it responsibly.

### How to Report

**Do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them using one of these methods:

1. **Preferred**: Use GitHub's private vulnerability reporting feature:
   - Go to the [Security tab](https://github.com/superinstance-ai/superinstance-sdk/security)
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email**: Send details to [security@superinstance.ai](mailto:security@superinstance.ai)

### What to Include

Please include as much of the following information as possible:

- **Description**: A clear description of the vulnerability
- **Impact**: What an attacker could achieve by exploiting this vulnerability
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Proof of concept**: Code or commands demonstrating the vulnerability
- **Affected versions**: Which versions are affected
- **Suggested fix**: If you have ideas for how to fix the issue
- **Your contact info**: For follow-up questions

### Response Timeline

We are committed to responding quickly to security reports:

| Stage | Target Time |
|-------|-------------|
| Initial response | 24 hours |
| Vulnerability confirmation | 3 business days |
| Fix development | 7-14 days (severity-dependent) |
| Security advisory published | Within 24 hours of fix release |

### What to Expect

1. **Acknowledgment**: You'll receive an acknowledgment within 24 hours
2. **Investigation**: Our security team will investigate and confirm the vulnerability
3. **Fix**: We'll develop and test a fix
4. **Disclosure**: We'll coordinate disclosure with you before publishing

### Disclosure Policy

We follow a coordinated disclosure approach:

1. We will **not** publicly disclose the vulnerability until a fix is available
2. We will credit you in the security advisory (unless you prefer to remain anonymous)
3. We will publish a Security Advisory on GitHub with:
   - Description of the vulnerability
   - Affected versions
   - Steps to update
   - CVE identifier (if applicable)
   - Credit to the reporter

## Security Best Practices

When using SuperInstance.AI, follow these security best practices:

### General

- **Keep SDK updated**: Always use the latest version
- **Validate inputs**: Sanitize user inputs before passing to the model
- **Review outputs**: Model outputs can contain unexpected content; validate before use
- **Secure your device**: Keep your SuperInstance hardware in a secure location

### API Keys and Secrets

- **Never commit credentials** to version control
- Use environment variables or secure secret management
- Rotate keys periodically if using any external services

### Network Security

- SuperInstance runs entirely locally — no data leaves your machine
- If integrating with external services, ensure proper authentication
- Use HTTPS for any network communications in your application

### Hardware Security

- Keep firmware updated to the latest version
- Use the `device.firmware_update()` method to apply updates
- Report any suspicious hardware behavior

## Security Features

SuperInstance.AI includes several built-in security features:

### Local-First Processing

All inference runs entirely on the local device. No data is sent to external servers unless you explicitly integrate with external services in your application code.

### Memory Protection

- Model weights are stored in protected memory regions
- Sensitive data in memory is cleared after use
- No persistent storage of prompts or generated text

### Firmware Verification

- Firmware updates are cryptographically signed
- The device verifies signatures before applying updates
- Rollback protection prevents downgrade attacks

### Secure Communication

- USB communication uses encrypted channels
- Device authentication prevents spoofing
- Secure boot ensures firmware integrity

## Known Security Considerations

### Model Outputs

LLMs can generate unexpected outputs, including:
- Hallucinated information
- Biased content
- Potentially harmful instructions

**Mitigation**: Always validate and filter outputs before using them in production applications.

### Prompt Injection

User inputs can potentially manipulate model behavior.

**Mitigation**: 
- Validate and sanitize user inputs
- Use system prompts to set boundaries
- Implement content filters for sensitive applications

### Resource Exhaustion

Generating large amounts of text can consume significant resources.

**Mitigation**:
- Set `max_tokens` limits
- Monitor device temperature and power
- Implement rate limiting in applications

## Security Updates

Security updates are announced through:

- **GitHub Security Advisories**: [security-advisories](https://github.com/superinstance-ai/superinstance-sdk/security/advisories)
- **Release Notes**: Each release includes security-related changes
- **Discord**: Announcements in #announcements channel
- **Email**: Security mailing list (subscribe at [security.superinstance.ai](https://security.superinstance.ai))

## Vulnerability Disclosure Hall of Fame

We thank the following researchers for responsibly disclosing vulnerabilities:

<!-- Security researchers will be listed here after responsible disclosure -->

*Be the first to report a vulnerability!*

## Contact

For any security-related questions or concerns:

- **Security Team**: [security@superinstance.ai](mailto:security@superinstance.ai)
- **PGP Key**: Available at [superinstance.ai/security.pub](https://superinstance.ai/security.pub)
- **Security Page**: [superinstance.ai/security](https://superinstance.ai/security)

---

Last updated: March 2026

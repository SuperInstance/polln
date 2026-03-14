# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **Email**: security@superinstance.ai
2. **GitHub Security Advisory**: Use the [Security Advisories](https://github.com/superinstance/ternaryair/security/advisories) feature

Include the following information:

* Type of vulnerability
* Full paths of source file(s) related to the vulnerability
* Any special configuration required to reproduce
* Step-by-step instructions to reproduce
* Proof-of-concept or exploit code (if possible)
* Impact of the vulnerability

### Response Timeline

* **Acknowledgment**: Within 48 hours
* **Initial Assessment**: Within 5 business days
* **Fix Timeline**: Depends on severity
  - Critical: 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: 90 days

### Disclosure Policy

We follow responsible disclosure:

1. Report received and acknowledged
2. Vulnerability confirmed and assessed
3. Fix developed and tested
4. Fix released
5. Public disclosure (after 30 days, or coordinated with reporter)

### Security Features by Design

TernaryAir is designed with security as a core principle:

* **Air-gapped**: No network interface capability
* **Mask-locked weights**: Cannot be read, modified, or extracted
* **No persistent storage**: All data is volatile
* **Hardware boundary**: Physical isolation between AI and host system
* **Immutable model**: Weights frozen in silicon ROM

### Known Security Considerations

1. **Physical Access**: An attacker with physical access and electron microscopy equipment could potentially extract weights through destructive analysis. This is mitigated by:
   - High cost of required equipment
   - Destruction of the chip during extraction
   - No ability to modify weights in the field

2. **Side-Channel Attacks**: Power analysis and timing attacks may provide limited information:
   - We recommend power analysis countermeasures for sensitive deployments
   - Timing is data-dependent but provides minimal leakage

3. **Supply Chain**: We recommend:
   - Purchasing from authorized distributors
   - Verifying chip authenticity
   - For critical applications, independent security audit

### Security Best Practices

When using TernaryAir:

1. **Physical Security**: Keep the device physically secure
2. **Host Security**: The host computer should still follow standard security practices
3. **Data Handling**: While TernaryAir doesn't store data, the host system does during transmission
4. **Software Updates**: Keep the SDK and drivers updated

## Security Hall of Fame

We appreciate responsible disclosure. Security researchers who help improve TernaryAir's security will be acknowledged here (with permission).

---

Thank you for helping keep TernaryAir secure!

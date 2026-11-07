# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

The Termux-Sentinel team takes the security of our software and user data
seriously. If you believe you have found a security vulnerability in
Termux-Sentinel, please report it to us as described below.

### Disclosure Process

- Please **do not** report security vulnerabilities through public GitHub issues.
- Please report vulnerabilities privately via [GitHub Security Advisories](https://github.com/motherskitchenblr2/TERMUX-SENTINEL-CLI/security/advisories/new).
- Include detailed steps to reproduce the vulnerability, sample code or
  commands, affected versions, and potential impact.
- You will receive an acknowledgment within 48 hours.
- We will coordinate a patched release and credit you in the release notes if
  desired.

### Security Guarantees & Safe Practices

- **Vault Protection:** Path targets registered in `vault.json` are strictly
  immutable against bulk deletion commands (`clean`, `purge`).
- **No Secret Leakage:** Do not commit actual `rclone.conf` credentials or API
  keys; use `rclone.conf.template` when providing distributed configurations.

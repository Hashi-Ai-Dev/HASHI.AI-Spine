# SPINE Security Baseline — Public Alpha

**Date:** 2026-04-07
**Applies to:** `Hashi-Ai-Dev/HASHI.AI-Spine`

---

## Goal

Establish minimal public-alpha security posture: open source ready, no obvious secrets exposure, clear vulnerability reporting path.

---

## Security Actions Taken

### ✅ LICENSE Added
- MIT license committed to repo root
- Covers open source distribution terms for public release

### ✅ SECURITY.md Added
- Path: `SECURITY.md` (repo root)
- Contact: **hashiai.dev@gmail.com**
- Policy: Reports acknowledged within 48h, critical issues resolved within 7 days
- Explicitly instructs: **do NOT open public GitHub issues for vulnerabilities**

### ✅ Secrets Scan (Pre-existing)
- No obvious GitHub tokens or credentials found in initial audit of repo contents
- `.gitignore` excludes common secret patterns
- No `ghp_`, `github_pat_`, or similar tokens tracked in git history

### ⚠️ Dependabot
- **Status:** Cannot confirm via API on free tier
- **Recommendation:** Visit `https://github.com/Hashi-Ai-Dev/HASHI.AI-Spine/settings/security_and_analysis` when logged in as repo owner and enable Dependabot alerts

### ⚠️ Secret Scanning
- **Status:** Cannot confirm via API on free tier (requires GitHub Pro for private repos; becomes available when repo is public)
- **Note:** Repo is now **public** — secret scanning should be active by default
- **Verify:** `https://github.com/Hashi-Ai-Dev/HASHI.AI-Spine/settings/security_and_analysis`

### ⚠️ Secret Scanning Push Protection
- Similar to above — enable at the same settings page

---

## Token Handling (This Session)

- GitHub PAT stored in `TOOLS.md` in the spine-repo-manager workspace
- `TOOLS.md` is gitignored and never committed to any git repo
- Token was used only for API calls to `Hashi-Ai-Dev/HASHI.AI-Spine`
- Token will be rotated by owner every couple of days per their statement

---

## Settings Checklist (Owner Action Recommended)

Visit: `https://github.com/Hashi-Ai-Dev/HASHI.AI-Spine/settings/security_and_analysis`

| Setting | Recommended |
|---------|-------------|
| Dependabot alerts | ✅ Enable |
| Dependabot security updates | ✅ Enable |
| Secret scanning | ✅ Should be on (public repo) |
| Push protection | ✅ Enable |
| Private vulnerability reporting | ✅ Enable |

---

## Vulnerability Reporting

**Do NOT open public issues for security vulnerabilities.**

Report to: **hashiai.dev@gmail.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

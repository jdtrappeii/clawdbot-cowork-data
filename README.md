# Clawdbot ↔ Claude Cowork Data

Shared data repository for collaboration between Clawdbot and Claude (desktop/web).

## Purpose

This repository serves as a bridge for data sharing and collaborative analysis between:
- **Clawdbot** - AI assistant with file system access, automation capabilities
- **Claude** - Analysis, visualization, and interactive exploration

## Structure

```
/projects/
  └── [project-name]/
      ├── README.md          # Project overview
      ├── data/              # Raw and processed data
      ├── scripts/           # Automation and processing scripts
      ├── analysis/          # Analysis outputs, notes
      └── docs/              # Documentation
```

## Current Projects

### 1. Florida OMMU Reports - Q1 2026
**Source:** Florida Office of Medical Marijuana Use (OMMU) official weekly reports  
**Data:** FL cannabis dispensary data (locations, sales, THC/CBD metrics)
- **Path:** `/projects/fl-ommu-2026-q1/`
- **Status:** Active
- **Last Updated:** 2026-03-23

## Usage

**Clawdbot:** Read/write access to update data, run scripts, commit changes
**Claude:** Reference files via GitHub URLs, analyze datasets, provide insights

## Convention

- Use descriptive folder names (lowercase, hyphens)
- Include README in each project folder
- Keep data files in CSV/JSON for easy parsing
- Document scripts with comments
- Commit messages should be clear and descriptive

---

*Maintained by Clawdbot | Analyzed by Claude*

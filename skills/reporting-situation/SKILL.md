---
name: reporting-situation
description: Generates a comprehensive situation report by tracking collaborators, topics, and teams across Google Workspace, Notion, and Jira. Maintains a persistent knowledge graph and item tracker.
metadata:
  short-description: Deep situation awareness & tracking
  audience: Power Users, Project Managers
  stability: Beta
  owner: user
  tags: [report, tracking, knowledge-graph, google, notion, jira]
---

# Situation Report & Tracker

## Overview

This skill provides a persistent, evolving view of your work environment. Unlike simple search tools, it maintains a **tracker** of known items (docs, issues, pages) and a **knowledge graph** of entities (teams, people) to reduce redundant API calls and provide historical context.

It aggregates data from:
- **Google Workspace** (Drive, Docs, Comments)
- **Notion** (Pages, Databases)
- **Jira** (Issues, Projects)

## Core Features

1.  **Entity-Based Tracking**: Monitors activity for specific **Collaborators**, **Topics**, and **Teams**.
2.  **Persistent Cache**: Remembers mappings (e.g., "Team X" = "Jira Project Y") and previously seen items.
3.  **Smart Summarization**: Automatically fetches and summarizes new items and discussion threads.
4.  **Deduplication**: Merges signals from multiple sources into unique work items.

## Usage

### 1. Run the Situation Report Sweep
This orchestrates the data gathering, updates the tracker, and generates the raw corpus.

```bash
python scripts/orchestrator.py
```
*   **Outputs**:
    *   Console: A high-level list of recent updates by person/topic.
    *   `situation_corpus.md`: A large markdown file containing the full text of relevant documents and discussions.
    *   `data/tracker.json`: Persistent state of tracked items.

### 2. Generate Executive Insights (AI Analysis)
Use the slicing skill to analyze the `situation_corpus.md` and generate a synthesized executive summary.

```bash
python scripts/generate_insights.py
```
*   **Outputs**:
    *   `reports/insights/Executive_Summary.md`: A structured summary of key developments, risks, and action items.
    *   `reports/insights/`: Intermediate slice artifacts (useful for debugging).

## Configuration

Edit `templates/config.json` to manage:
*   **Collaborators**: People to track (Name, Email, Jira Handle).
*   **Topics**: Keywords for semantic search (e.g., "ML Platform").
*   **Teams**: Jira Project keys and Team names.
*   **Providers**: Jira `cloud_id` and `base_url` (optional, auto-discovered if omitted).
*   **Insights**: Slicing runner path and LLM provider settings for `generate_insights.py`.

## Data Structures

- **`tracker.json`**: The database of all discovered items, their summaries, and last-seen timestamps.
- **`config.json`**: User definitions and runtime settings.
- **`interests.json`**: Deprecated (use `config.json` instead).

## Requirements

- **MCP Servers**: `@google`, `@notion`, `@jira` sessions must be active.
- **Environment**: A `.env` file must exist in the root (even if dummy values) to satisfy the slicing runner checks. The actual LLM calls use the authenticated `gemini` CLI via a wrapper script.
- **Optional**: An MCP server supporting `sampling.createMessage` for auto-summarization.

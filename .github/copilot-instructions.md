# Copilot Instructions — ASD (Agentic Spec-Driven Development)

## What This Project Is

ASD is a **multi-agent AI framework** (not a traditional application). It orchestrates specialized AI agents to validate, analyze, and implement software requirements through the **GAIDD pipeline** (Generative AI-Driven Development). There is no runnable source code — everything lives under `.github/` as agent definitions, prompts, skills, and documentation.

## Architecture Overview

The system follows a **pipeline + delegation** pattern:

1. **Orchestrator Agent** (`agents/agent_orchestrator.agent.md`) — entry point; runs GAIDD pipeline first, then delegates to specialized agents
2. **Spec Agent** (`agents/agent_spec.agent.md`) — transforms requirements into technical specifications (HU/User Stories)
3. **GAIDD Sub-Agents** (`agents/agent_spec_gaidd.*.agent.md`) — execute pipeline steps 0→3: classify artifact, evaluate granularity (INVEST/IEEE 830), validate completeness, perform technical analysis
4. **Implementation Agents**: Backend (`agent_backend`), Frontend (`agent_frontend`), QA (`agent_qa`) — each loads its own guidelines before acting and activates domain-specific skills

**Critical invariant:** The GAIDD/Spec pipeline **always runs first** — no implementation agent executes before requirements are validated through Steps 0→3.

## Key Directories

- `.github/agents/` — 9 agent definitions (`.agent.md` with YAML frontmatter)
- `.github/prompts/` — 9 prompt entry points (`.prompt.md`); `agent_full-flow.prompt.md` is the recommended starting point
- `.github/skills/` — 14 reusable skills (QA: 8, Backend: 3, Frontend: 3)
- `.github/docs/config/config.yaml` — user profile and output folder configuration
- `.github/docs/context/` — project architecture, tech stack, domain dictionary, DoD/DoR, ADRs, golden rules
- `.github/docs/lineamientos/` — development (`dev-guidelines.md`), QA (`qa-guidelines.md`), and general (`guidelines.md`) standards
- `.github/docs/output/` — generated reports organized by `{artifact_id}` and agent type
- `.github/INDEX.md` — complete inventory with relationships between all components

## GAIDD Pipeline Flow

```
Input (HU or requirement) → Step 0: Classify (HU vs Traditional Req.)
  → Step 1: Evaluate granularity (INVEST or IEEE 830)
  → Step 2: Validate completeness & technical feasibility
  → Step 2.1 (optional): Resolve conflicts
  → Step 3: Technical analysis (WHAT / WHERE / WHY)
  → User selects agent(s): Backend / Frontend / QA
  → Output to .github/docs/output/{artifact_id}/
```

## Conventions for Editing This Framework

- **Language:** All documentation and agent output is in **Spanish**. Config field `communication_language` and `document_output_language` control this.
- **Agent files** use `.agent.md` extension with YAML frontmatter (`description`, `model`, `tools`, `name`). Model is `gpt-4o`.
- **Prompt files** use `.prompt.md` with frontmatter (`description`, `mode: 'agent'`).
- **Skills** are plain `.md` files under `skills/`, named `skill_{domain}_{capability}.md`.
- **Output files** follow the pattern `{artifact_id}.step_{N}.{step-name}.md`.
- **Naming:** agents use `agent_{role}`, prompts use `prompt_agent_{role}`, skills use `skill_{domain}_{name}` — all kebab-case.

## Tech Stack Context (for generated code)

The target project architecture uses: **Java 21, Spring Boot 3.x, Spring WebFlux (reactive), R2DBC, PostgreSQL 15+**. Blocking code (JPA/Hibernate) is prohibited in reactive flows. See `docs/context/tech_stack_constraints.context.md`.

## Golden Rules (`docs/context/reglas-de-oro.md`)

- Never generate code, files, or modifications without explicit user request
- Ask for clarification on any ambiguity — never assume
- Explain actions before executing them
- All agents must load their respective `lineamientos` file before producing output

## When Modifying Agents or Skills

1. Update `.github/INDEX.md` to reflect any new or renamed component and its relationships
2. Ensure the orchestrator's context-assembly logic in `agent_orchestrator.agent.md` references new agents/skills correctly
3. Keep the pipeline step numbering consistent (Steps 0, 1, 2, 2.1, 3)
4. Skill activation conditions are defined inside each implementation agent — update the agent file when adding a skill

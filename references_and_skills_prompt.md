

# FILE: references/skill_creator_from_codex.md

This document is a comprehensive guide to authoring effective Agent Skills from OpenAI's Codex, detailing core principles, file anatomy, design patterns, and a full creation lifecycle, enabling an agent to learn how to build, package, and iterate on new capabilities.

---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations.
metadata:
  short-description: Create or update a skill
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Codex's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Codex from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Codex needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Codex is already very smart.** Only add context Codex doesn't already have. Challenge each piece of information: "Does Codex really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Codex as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Codex reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Codex for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Codex's process and thinking.

- **When to include**: For documentation that Codex should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Codex determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Codex produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Codex to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Codex (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Codex loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, Codex only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, Codex only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Codex reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Codex can see the full scope when previewing.

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Package the skill (run package_skill.py)
6. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Skill Naming

- Use lowercase letters, digits, and hyphens only; normalize user-provided titles to hyphen-case (e.g., "Plan Mode" -> `plan-mode`).
- When generating names, generate a name under 64 characters (letters, digits, hyphens).
- Prefer short, verb-led phrases that describe the action.
- Namespace by tool when it improves clarity or triggering (e.g., `gh-address-comments`, `linear-address-issue`).
- Name the skill folder exactly after the skill name.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.

Usage:

```bash
scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

Examples:

```bash
scripts/init_skill.py my-skill --path skills/public
scripts/init_skill.py my-skill --path skills/public --resources scripts,references
scripts/init_skill.py my-skill --path skills/public --resources scripts --examples
```

The script:

- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Optionally creates resource directories based on `--resources`
- Optionally adds example files when `--examples` is set

After initialization, customize the SKILL.md and add resources as needed. If you used `--examples`, replace or delete placeholder files.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Codex to use. Include information that would be beneficial and non-obvious to Codex. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Codex instance execute these tasks more effectively.

#### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
- **Specific output formats or quality standards**: See references/output-patterns.md for template and example patterns

These files contain established best practices for effective skill design.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.

If you used `--examples`, delete any placeholder files that are not needed for the skill. Only create resource directories that are actually required.

#### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

##### Frontmatter

Write the YAML frontmatter with `name` and `description`:

- `name`: The skill name
- `description`: This is the primary triggering mechanism for your skill, and helps Codex understand when to use the skill.
  - Include both what the Skill does and specific triggers/contexts for when to use it.
  - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to Codex.
  - Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Codex needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"

Do not include any other fields in YAML frontmatter.

##### Body

Write instructions for using the skill and its bundled resources.

### Step 5: Packaging a Skill

Once development of the skill is complete, it must be packaged into a distributable .skill file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script will:

1. **Validate** the skill automatically, checking:

   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package** the skill if validation passes, creating a .skill file named after the skill (e.g., `my-skill.skill`) that includes all files and maintains the proper directory structure for distribution. The .skill file is a zip file with a .skill extension.

If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.

### Step 6: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again


# FILE: references/skill_creator_from_anthropic.md

This document is a comprehensive guide to authoring effective skills for Agents from Anthropic's Claude, detailing core principles, file anatomy, design patterns, and a full creation lifecycle, enabling an agent to learn how to build, package, and iterate on new capabilities.

---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
license: Complete terms in LICENSE.txt
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxilary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, Claude only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, Claude only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Claude reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Claude can see the full scope when previewing.

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Plan reusable skill contents (scripts, references, assets)
3. Initialize the skill (run init_skill.py)
4. Edit the skill (implement resources and write SKILL.md)
5. Package the skill (run package_skill.py)
6. Iterate based on real usage

Follow these steps in order, skipping only if there is a clear reason why they are not applicable.

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.

Usage:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:

- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

After initialization, customize or remove the generated SKILL.md and example files as needed.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Include information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.

#### Learn Proven Design Patterns

Consult these helpful guides based on your skill's needs:

- **Multi-step processes**: See references/workflows.md for sequential workflows and conditional logic
- **Specific output formats or quality standards**: See references/output-patterns.md for template and example patterns

These files contain established best practices for effective skill design.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Added scripts must be tested by actually running them to ensure there are no bugs and that the output matches what is expected. If there are many similar scripts, only a representative sample needs to be tested to ensure confidence that they all work while balancing time to completion.

Any example files and directories not needed for the skill should be deleted. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

#### Update SKILL.md

**Writing Guidelines:** Always use imperative/infinitive form.

##### Frontmatter

Write the YAML frontmatter with `name` and `description`:

- `name`: The skill name
- `description`: This is the primary triggering mechanism for your skill, and helps Claude understand when to use the skill.
  - Include both what the Skill does and specific triggers/contexts for when to use it.
  - Include all "when to use" information here - Not in the body. The body is only loaded after triggering, so "When to Use This Skill" sections in the body are not helpful to Claude.
  - Example description for a `docx` skill: "Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Claude needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks"

Do not include any other fields in YAML frontmatter.

##### Body

Write instructions for using the skill and its bundled resources.

### Step 5: Packaging a Skill

Once development of the skill is complete, it must be packaged into a distributable .skill file that gets shared with the user. The packaging process automatically validates the skill first to ensure it meets all requirements:

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory specification:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

The packaging script will:

1. **Validate** the skill automatically, checking:

   - YAML frontmatter format and required fields
   - Skill naming conventions and directory structure
   - Description completeness and quality
   - File organization and resource references

2. **Package** the skill if validation passes, creating a .skill file named after the skill (e.g., `my-skill.skill`) that includes all files and maintains the proper directory structure for distribution. The .skill file is a zip file with a .skill extension.

If validation fails, the script will report the errors and exit without creating a package. Fix any validation errors and run the packaging command again.

### Step 6: Iterate

After testing the skill, users may request improvements. Often this happens right after using the skill, with fresh context of how the skill performed.

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify how SKILL.md or bundled resources should be updated
4. Implement changes and test again


# FILE: references/skill_authoring_best_practices_from_anthropic.md

This document provides Anthropic's best practices for authoring effective, discoverable, and well-structured Agent Skills, teaching an agent how to create and refine them through principles like conciseness, progressive disclosure, and iterative testing.

# Skill authoring best practices

Learn how to write effective Skills that Claude can discover and use successfully.

---

Good Skills are concise, well-structured, and tested with real usage. This guide provides practical authoring decisions to help you write Skills that Claude can discover and use effectively.

For conceptual background on how Skills work, see the [Skills overview](/docs/en/agents-and-tools/agent-skills/overview).

## Core principles

### Concise is key

The [context window](/docs/en/build-with-claude/context-windows) is a public good. Your Skill shares the context window with everything else Claude needs to know, including:

- The system prompt
- Conversation history
- Other Skills' metadata
- Your actual request

Not every token in your Skill has an immediate cost. At startup, only the metadata (name and description) from all Skills is pre-loaded. Claude reads SKILL.md only when the Skill becomes relevant, and reads additional files only as needed. However, being concise in SKILL.md still matters: once Claude loads it, every token competes with conversation history and other context.

**Default assumption**: Claude is already very smart

Only add context Claude doesn't already have. Challenge each piece of information:

- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

**Good example: Concise** (approximately 50 tokens):

````markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**Bad example: Too verbose** (approximately 150 tokens):

```markdown
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...
```

The concise version assumes Claude knows what PDFs are and how libraries work.

### Set appropriate degrees of freedom

Match the level of specificity to the task's fragility and variability.

**High freedom** (text-based instructions):

Use when:

- Multiple approaches are valid
- Decisions depend on context
- Heuristics guide the approach

Example:

```markdown
## Code review process

1. Analyze the code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability and maintainability
4. Verify adherence to project conventions
```

**Medium freedom** (pseudocode or scripts with parameters):

Use when:

- A preferred pattern exists
- Some variation is acceptable
- Configuration affects behavior

Example:

````markdown
## Generate report

Use this template and customize as needed:

```python
def generate_report(data, format="markdown", include_charts=True):
    # Process data
    # Generate output in specified format
    # Optionally include visualizations
```
````

**Low freedom** (specific scripts, few or no parameters):

Use when:

- Operations are fragile and error-prone
- Consistency is critical
- A specific sequence must be followed

Example:

````markdown
## Database migration

Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
````

**Analogy**: Think of Claude as a robot exploring a path:

- **Narrow bridge with cliffs on both sides**: There's only one safe way forward. Provide specific guardrails and exact instructions (low freedom). Example: database migrations that must run in exact sequence.
- **Open field with no hazards**: Many paths lead to success. Give general direction and trust Claude to find the best route (high freedom). Example: code reviews where context determines the best approach.

### Test with all models you plan to use

Skills act as additions to models, so effectiveness depends on the underlying model. Test your Skill with all the models you plan to use it with.

**Testing considerations by model**:

- **Claude Haiku** (fast, economical): Does the Skill provide enough guidance?
- **Claude Sonnet** (balanced): Is the Skill clear and efficient?
- **Claude Opus** (powerful reasoning): Does the Skill avoid over-explaining?

What works perfectly for Opus might need more detail for Haiku. If you plan to use your Skill across multiple models, aim for instructions that work well with all of them.

## Skill structure

<Note>
**YAML Frontmatter**: The SKILL.md frontmatter requires two fields:

`name`:

- Maximum 64 characters
- Must contain only lowercase letters, numbers, and hyphens
- Cannot contain XML tags
- Cannot contain reserved words: "anthropic", "claude"

`description`:

- Must be non-empty
- Maximum 1024 characters
- Cannot contain XML tags
- Should describe what the Skill does and when to use it

For complete Skill structure details, see the [Skills overview](/docs/en/agents-and-tools/agent-skills/overview#skill-structure).
</Note>

### Naming conventions

Use consistent naming patterns to make Skills easier to reference and discuss. We recommend using **gerund form** (verb + -ing) for Skill names, as this clearly describes the activity or capability the Skill provides.

Remember that the `name` field must use lowercase letters, numbers, and hyphens only.

**Good naming examples (gerund form)**:

- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`
- `testing-code`
- `writing-documentation`

**Acceptable alternatives**:

- Noun phrases: `pdf-processing`, `spreadsheet-analysis`
- Action-oriented: `process-pdfs`, `analyze-spreadsheets`

**Avoid**:

- Vague names: `helper`, `utils`, `tools`
- Overly generic: `documents`, `data`, `files`
- Reserved words: `anthropic-helper`, `claude-tools`
- Inconsistent patterns within your skill collection

Consistent naming makes it easier to:

- Reference Skills in documentation and conversations
- Understand what a Skill does at a glance
- Organize and search through multiple Skills
- Maintain a professional, cohesive skill library

### Writing effective descriptions

The `description` field enables Skill discovery and should include both what the Skill does and when to use it.

<Warning>
**Always write in third person**. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.

- **Good:** "Processes Excel files and generates reports"
- **Avoid:** "I can help you process Excel files"
- **Avoid:** "You can use this to process Excel files"
</Warning>

**Be specific and include key terms**. Include both what the Skill does and specific triggers/contexts for when to use it.

Each Skill has exactly one description field. The description is critical for skill selection: Claude uses it to choose the right Skill from potentially 100+ available Skills. Your description must provide enough detail for Claude to know when to select this Skill, while the rest of SKILL.md provides the implementation details.

Effective examples:

**PDF Processing skill:**

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Excel Analysis skill:**

```yaml
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Git Commit Helper skill:**

```yaml
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

Avoid vague descriptions like these:

```yaml
description: Helps with documents
```

```yaml
description: Processes data
```

```yaml
description: Does stuff with files
```

### Progressive disclosure patterns

SKILL.md serves as an overview that points Claude to detailed materials as needed, like a table of contents in an onboarding guide. For an explanation of how progressive disclosure works, see [How Skills work](/docs/en/agents-and-tools/agent-skills/overview#how-skills-work) in the overview.

**Practical guidance:**

- Keep SKILL.md body under 500 lines for optimal performance
- Split content into separate files when approaching this limit
- Use the patterns below to organize instructions, code, and resources effectively

#### Visual overview: From simple to complex

A basic Skill starts with just a SKILL.md file containing metadata and instructions:

![Simple SKILL.md file showing YAML frontmatter and markdown body](/docs/images/agent-skills-simple-file.png)

As your Skill grows, you can bundle additional content that Claude loads only when needed:

![Bundling additional reference files like reference.md and forms.md.](/docs/images/agent-skills-bundling-content.png)

The complete Skill directory structure might look like this:

```
pdf/
├── SKILL.md              # Main instructions (loaded when triggered)
├── FORMS.md              # Form-filling guide (loaded as needed)
├── reference.md          # API reference (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    ├── analyze_form.py   # Utility script (executed, not loaded)
    ├── fill_form.py      # Form filling script
    └── validate.py       # Validation script
```

#### Pattern 1: High-level guide with references

````markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Quick start

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
````

Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

#### Pattern 2: Domain-specific organization

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context. When a user asks about sales metrics, Claude only needs to read sales-related schemas, not finance or marketing data. This keeps token usage low and context focused.

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

````markdown SKILL.md
# BigQuery Data Analysis

## Available datasets

**Finance**: Revenue, ARR, billing → See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline, accounts → See [reference/sales.md](reference/sales.md)
**Product**: API usage, features, adoption → See [reference/product.md](reference/product.md)
**Marketing**: Campaigns, attribution, email → See [reference/marketing.md](reference/marketing.md)

## Quick search

Find specific metrics using grep:

```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
grep -i "api usage" reference/product.md
```
````

#### Pattern 3: Conditional details

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Claude reads REDLINING.md or OOXML.md only when the user needs those features.

### Avoid deeply nested references

Claude may partially read files when they're referenced from other referenced files. When encountering nested references, Claude might use commands like `head -100` to preview content rather than reading entire files, resulting in incomplete information.

**Keep references one level deep from SKILL.md**. All reference files should link directly from SKILL.md to ensure Claude reads complete files when needed.

**Bad example: Too deep**:

```markdown
# SKILL.md
See [advanced.md](advanced.md)...

# advanced.md
See [details.md](details.md)...

# details.md
Here's the actual information...
```

**Good example: One level deep**:

```markdown
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
**Examples**: See [examples.md](examples.md)
```

### Structure longer reference files with table of contents

For reference files longer than 100 lines, include a table of contents at the top. This ensures Claude can see the full scope of available information even when previewing with partial reads.

**Example**:

```markdown
# API Reference

## Contents
- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples

## Authentication and setup
...

## Core methods
...
```

Claude can then read the complete file or jump to specific sections as needed.

For details on how this filesystem-based architecture enables progressive disclosure, see the [Runtime environment](#runtime-environment) section in the Advanced section below.

## Workflows and feedback loops

### Use workflows for complex tasks

Break complex operations into clear, sequential steps. For particularly complex workflows, provide a checklist that Claude can copy into its response and check off as it progresses.

**Example 1: Research synthesis workflow** (for Skills without code):

````markdown
## Research synthesis workflow

Copy this checklist and track your progress:

```
Research Progress:
- [ ] Step 1: Read all source documents
- [ ] Step 2: Identify key themes
- [ ] Step 3: Cross-reference claims
- [ ] Step 4: Create structured summary
- [ ] Step 5: Verify citations
```

**Step 1: Read all source documents**

Review each document in the `sources/` directory. Note the main arguments and supporting evidence.

**Step 2: Identify key themes**

Look for patterns across sources. What themes appear repeatedly? Where do sources agree or disagree?

**Step 3: Cross-reference claims**

For each major claim, verify it appears in the source material. Note which source supports each point.

**Step 4: Create structured summary**

Organize findings by theme. Include:
- Main claim
- Supporting evidence from sources
- Conflicting viewpoints (if any)

**Step 5: Verify citations**

Check that every claim references the correct source document. If citations are incomplete, return to Step 3.
````

This example shows how workflows apply to analysis tasks that don't require code. The checklist pattern works for any complex, multi-step process.

**Example 2: PDF form filling workflow** (for Skills with code):

````markdown
## PDF form filling workflow

Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```

**Step 1: Analyze the form**

Run: `python scripts/analyze_form.py input.pdf`

This extracts form fields and their locations, saving to `fields.json`.

**Step 2: Create field mapping**

Edit `fields.json` to add values for each field.

**Step 3: Validate mapping**

Run: `python scripts/validate_fields.py fields.json`

Fix any validation errors before continuing.

**Step 4: Fill the form**

Run: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: Verify output**

Run: `python scripts/verify_output.py output.pdf`

If verification fails, return to Step 2.
````

Clear steps prevent Claude from skipping critical validation. The checklist helps both Claude and you track progress through multi-step workflows.

### Implement feedback loops

**Common pattern**: Run validator → fix errors → repeat

This pattern greatly improves output quality.

**Example 1: Style guide compliance** (for Skills without code):

```markdown
## Content review process

1. Draft your content following the guidelines in STYLE_GUIDE.md
2. Review against the checklist:
   - Check terminology consistency
   - Verify examples follow the standard format
   - Confirm all required sections are present
3. If issues found:
   - Note each issue with specific section reference
   - Revise the content
   - Review the checklist again
4. Only proceed when all requirements are met
5. Finalize and save the document
```

This shows the validation loop pattern using reference documents instead of scripts. The "validator" is STYLE_GUIDE.md, and Claude performs the check by reading and comparing.

**Example 2: Document editing process** (for Skills with code):

```markdown
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python ooxml/scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python ooxml/scripts/pack.py unpacked_dir/ output.docx`
6. Test the output document
```

The validation loop catches errors early.

## Content guidelines

### Avoid time-sensitive information

Don't include information that will become outdated:

**Bad example: Time-sensitive** (will become wrong):

```markdown
If you're doing this before August 2025, use the old API.
After August 2025, use the new API.
```

**Good example** (use "old patterns" section):

```markdown
## Current method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Old patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used: `api.example.com/v1/messages`

This endpoint is no longer supported.
</details>
```

The old patterns section provides historical context without cluttering the main content.

### Use consistent terminology

Choose one term and use it throughout the Skill:

**Good - Consistent**:

- Always "API endpoint"
- Always "field"
- Always "extract"

**Bad - Inconsistent**:

- Mix "API endpoint", "URL", "API route", "path"
- Mix "field", "box", "element", "control"
- Mix "extract", "pull", "get", "retrieve"

Consistency helps Claude understand and follow instructions.

## Common patterns

### Template pattern

Provide templates for output format. Match the level of strictness to your needs.

**For strict requirements** (like API responses or data formats):

````markdown
## Report structure

ALWAYS use this exact template structure:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
- Finding 3 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
````

**For flexible guidance** (when adaptation is useful):

````markdown
## Report structure

Here is a sensible default format, but use your best judgment based on the analysis:

```markdown
# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt sections based on what you discover]

## Recommendations
[Tailor to the specific context]
```

Adjust sections as needed for the specific analysis type.
````

### Examples pattern

For Skills where output quality depends on seeing examples, provide input/output pairs just like in regular prompting:

````markdown
## Commit message format

Generate commit messages following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

**Example 3:**
Input: Updated dependencies and refactored error handling
Output:
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21
- Standardize error response format across endpoints
```

Follow this style: type(scope): brief description, then detailed explanation.
````

Examples help Claude understand the desired style and level of detail more clearly than descriptions alone.

### Conditional workflow pattern

Guide Claude through decision points:

```markdown
## Document modification workflow

1. Determine the modification type:

   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow:
   - Use docx-js library
   - Build document from scratch
   - Export to .docx format

3. Editing workflow:
   - Unpack existing document
   - Modify XML directly
   - Validate after each change
   - Repack when complete
```

<Tip>
If workflows become large or complicated with many steps, consider pushing them into separate files and tell Claude to read the appropriate file based on the task at hand.
</Tip>

## Evaluation and iteration

### Build evaluations first

**Create evaluations BEFORE writing extensive documentation.** This ensures your Skill solves real problems rather than documenting imagined ones.

**Evaluation-driven development:**

1. **Identify gaps**: Run Claude on representative tasks without a Skill. Document specific failures or missing context
2. **Create evaluations**: Build three scenarios that test these gaps
3. **Establish baseline**: Measure Claude's performance without the Skill
4. **Write minimal instructions**: Create just enough content to address the gaps and pass evaluations
5. **Iterate**: Execute evaluations, compare against baseline, and refine

This approach ensures you're solving actual problems rather than anticipating requirements that may never materialize.

**Evaluation structure**:

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Successfully reads the PDF file using an appropriate PDF processing library or command-line tool",
    "Extracts text content from all pages in the document without missing any pages",
    "Saves the extracted text to a file named output.txt in a clear, readable format"
  ]
}
```

<Note>
This example demonstrates a data-driven evaluation with a simple testing rubric. We do not currently provide a built-in way to run these evaluations. Users can create their own evaluation system. Evaluations are your source of truth for measuring Skill effectiveness.
</Note>

### Develop Skills iteratively with Claude

The most effective Skill development process involves Claude itself. Work with one instance of Claude ("Claude A") to create a Skill that will be used by other instances ("Claude B"). Claude A helps you design and refine instructions, while Claude B tests them in real tasks. This works because Claude models understand both how to write effective agent instructions and what information agents need.

**Creating a new Skill:**

1. **Complete a task without a Skill**: Work through a problem with Claude A using normal prompting. As you work, you'll naturally provide context, explain preferences, and share procedural knowledge. Notice what information you repeatedly provide.

2. **Identify the reusable pattern**: After completing the task, identify what context you provided that would be useful for similar future tasks.

   **Example**: If you worked through a BigQuery analysis, you might have provided table names, field definitions, filtering rules (like "always exclude test accounts"), and common query patterns.

3. **Ask Claude A to create a Skill**: "Create a Skill that captures this BigQuery analysis pattern we just used. Include the table schemas, naming conventions, and the rule about filtering test accounts."

   <Tip>
   Claude models understand the Skill format and structure natively. You don't need special system prompts or a "writing skills" skill to get Claude to help create Skills. Simply ask Claude to create a Skill and it will generate properly structured SKILL.md content with appropriate frontmatter and body content.
   </Tip>

4. **Review for conciseness**: Check that Claude A hasn't added unnecessary explanations. Ask: "Remove the explanation about what win rate means - Claude already knows that."

5. **Improve information architecture**: Ask Claude A to organize the content more effectively. For example: "Organize this so the table schema is in a separate reference file. We might add more tables later."

6. **Test on similar tasks**: Use the Skill with Claude B (a fresh instance with the Skill loaded) on related use cases. Observe whether Claude B finds the right information, applies rules correctly, and handles the task successfully.

7. **Iterate based on observation**: If Claude B struggles or misses something, return to Claude A with specifics: "When Claude used this Skill, it forgot to filter by date for Q4. Should we add a section about date filtering patterns?"

**Iterating on existing Skills:**

The same hierarchical pattern continues when improving Skills. You alternate between:

- **Working with Claude A** (the expert who helps refine the Skill)
- **Testing with Claude B** (the agent using the Skill to perform real work)
- **Observing Claude B's behavior** and bringing insights back to Claude A

1. **Use the Skill in real workflows**: Give Claude B (with the Skill loaded) actual tasks, not test scenarios

2. **Observe Claude B's behavior**: Note where it struggles, succeeds, or makes unexpected choices

   **Example observation**: "When I asked Claude B for a regional sales report, it wrote the query but forgot to filter out test accounts, even though the Skill mentions this rule."

3. **Return to Claude A for improvements**: Share the current SKILL.md and describe what you observed. Ask: "I noticed Claude B forgot to filter test accounts when I asked for a regional report. The Skill mentions filtering, but maybe it's not prominent enough?"

4. **Review Claude A's suggestions**: Claude A might suggest reorganizing to make rules more prominent, using stronger language like "MUST filter" instead of "always filter", or restructuring the workflow section.

5. **Apply and test changes**: Update the Skill with Claude A's refinements, then test again with Claude B on similar requests

6. **Repeat based on usage**: Continue this observe-refine-test cycle as you encounter new scenarios. Each iteration improves the Skill based on real agent behavior, not assumptions.

**Gathering team feedback:**

1. Share Skills with teammates and observe their usage
2. Ask: Does the Skill activate when expected? Are instructions clear? What's missing?
3. Incorporate feedback to address blind spots in your own usage patterns

**Why this approach works**: Claude A understands agent needs, you provide domain expertise, Claude B reveals gaps through real usage, and iterative refinement improves Skills based on observed behavior rather than assumptions.

### Observe how Claude navigates Skills

As you iterate on Skills, pay attention to how Claude actually uses them in practice. Watch for:

- **Unexpected exploration paths**: Does Claude read files in an order you didn't anticipate? This might indicate your structure isn't as intuitive as you thought
- **Missed connections**: Does Claude fail to follow references to important files? Your links might need to be more explicit or prominent
- **Overreliance on certain sections**: If Claude repeatedly reads the same file, consider whether that content should be in the main SKILL.md instead
- **Ignored content**: If Claude never accesses a bundled file, it might be unnecessary or poorly signaled in the main instructions

Iterate based on these observations rather than assumptions. The 'name' and 'description' in your Skill's metadata are particularly critical. Claude uses these when deciding whether to trigger the Skill in response to the current task. Make sure they clearly describe what the Skill does and when it should be used.

## Anti-patterns to avoid

### Avoid Windows-style paths

Always use forward slashes in file paths, even on Windows:

- ✓ **Good**: `scripts/helper.py`, `reference/guide.md`
- ✗ **Avoid**: `scripts\helper.py`, `reference\guide.md`

Unix-style paths work across all platforms, while Windows-style paths cause errors on Unix systems.

### Avoid offering too many options

Don't present multiple approaches unless necessary:

````markdown
**Bad example: Too many choices** (confusing):
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

**Good example: Provide a default** (with escape hatch):
"Use pdfplumber for text extraction:
```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
````

## Advanced: Skills with executable code

The sections below focus on Skills that include executable scripts. If your Skill uses only markdown instructions, skip to [Checklist for effective Skills](#checklist-for-effective-skills).

### Solve, don't punt

When writing scripts for Skills, handle error conditions rather than punting to Claude.

**Good example: Handle errors explicitly**:

```python
def process_file(path):
    """Process a file, creating it if it doesn't exist."""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        # Create file with default content instead of failing
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        # Provide alternative instead of failing
        print(f"Cannot access {path}, using default")
        return ''
```

**Bad example: Punt to Claude**:

```python
def process_file(path):
    # Just fail and let Claude figure it out
    return open(path).read()
```

Configuration parameters should also be justified and documented to avoid "voodoo constants" (Ousterhout's law). If you don't know the right value, how will Claude determine it?

**Good example: Self-documenting**:

```python
# HTTP requests typically complete within 30 seconds
# Longer timeout accounts for slow connections
REQUEST_TIMEOUT = 30

# Three retries balances reliability vs speed
# Most intermittent failures resolve by the second retry
MAX_RETRIES = 3
```

**Bad example: Magic numbers**:

```python
TIMEOUT = 47  # Why 47?
RETRIES = 5   # Why 5?
```

### Provide utility scripts

Even if Claude could write a script, pre-made scripts offer advantages:

**Benefits of utility scripts**:

- More reliable than generated code
- Save tokens (no need to include code in context)
- Save time (no code generation required)
- Ensure consistency across uses

![Bundling executable scripts alongside instruction files](/docs/images/agent-skills-executable-scripts.png)

The diagram above shows how executable scripts work alongside instruction files. The instruction file (forms.md) references the script, and Claude can execute it without loading its contents into context.

**Important distinction**: Make clear in your instructions whether Claude should:

- **Execute the script** (most common): "Run `analyze_form.py` to extract fields"
- **Read it as reference** (for complex logic): "See `analyze_form.py` for the field extraction algorithm"

For most utility scripts, execution is preferred because it's more reliable and efficient. See the [Runtime environment](#runtime-environment) section below for details on how script execution works.

**Example**:

````markdown
## Utility scripts

**analyze_form.py**: Extract all form fields from PDF

```bash
python scripts/analyze_form.py input.pdf > fields.json
```

Output format:
```json
{
  "field_name": {"type": "text", "x": 100, "y": 200},
  "signature": {"type": "sig", "x": 150, "y": 500}
}
```

**validate_boxes.py**: Check for overlapping bounding boxes

```bash
python scripts/validate_boxes.py fields.json
# Returns: "OK" or lists conflicts
```

**fill_form.py**: Apply field values to PDF

```bash
python scripts/fill_form.py input.pdf fields.json output.pdf
```
````

### Use visual analysis

When inputs can be rendered as images, have Claude analyze them:

````markdown
## Form layout analysis

1. Convert PDF to images:
   ```bash
   python scripts/pdf_to_images.py form.pdf
   ```

2. Analyze each page image to identify form fields
3. Claude can see field locations and types visually
````

<Note>
In this example, you'd need to write the `pdf_to_images.py` script.
</Note>

Claude's vision capabilities help understand layouts and structures.

### Create verifiable intermediate outputs

When Claude performs complex, open-ended tasks, it can make mistakes. The "plan-validate-execute" pattern catches errors early by having Claude first create a plan in a structured format, then validate that plan with a script before executing it.

**Example**: Imagine asking Claude to update 50 form fields in a PDF based on a spreadsheet. Without validation, Claude might reference non-existent fields, create conflicting values, miss required fields, or apply updates incorrectly.

**Solution**: Use the workflow pattern shown above (PDF form filling), but add an intermediate `changes.json` file that gets validated before applying changes. The workflow becomes: analyze → **create plan file** → **validate plan** → execute → verify.

**Why this pattern works:**

- **Catches errors early**: Validation finds problems before changes are applied
- **Machine-verifiable**: Scripts provide objective verification
- **Reversible planning**: Claude can iterate on the plan without touching originals
- **Clear debugging**: Error messages point to specific problems

**When to use**: Batch operations, destructive changes, complex validation rules, high-stakes operations.

**Implementation tip**: Make validation scripts verbose with specific error messages like "Field 'signature_date' not found. Available fields: customer_name, order_total, signature_date_signed" to help Claude fix issues.

### Package dependencies

Skills run in the code execution environment with platform-specific limitations:

- **claude.ai**: Can install packages from npm and PyPI and pull from GitHub repositories
- **Anthropic API**: Has no network access and no runtime package installation

List required packages in your SKILL.md and verify they're available in the [code execution tool documentation](/docs/en/agents-and-tools/tool-use/code-execution-tool).

### Runtime environment

Skills run in a code execution environment with filesystem access, bash commands, and code execution capabilities. For the conceptual explanation of this architecture, see [The Skills architecture](/docs/en/agents-and-tools/agent-skills/overview#the-skills-architecture) in the overview.

**How this affects your authoring:**

**How Claude accesses Skills:**

1. **Metadata pre-loaded**: At startup, the name and description from all Skills' YAML frontmatter are loaded into the system prompt
2. **Files read on-demand**: Claude uses bash Read tools to access SKILL.md and other files from the filesystem when needed
3. **Scripts executed efficiently**: Utility scripts can be executed via bash without loading their full contents into context. Only the script's output consumes tokens
4. **No context penalty for large files**: Reference files, data, or documentation don't consume context tokens until actually read

- **File paths matter**: Claude navigates your skill directory like a filesystem. Use forward slashes (`reference/guide.md`), not backslashes
- **Name files descriptively**: Use names that indicate content: `form_validation_rules.md`, not `doc2.md`
- **Organize for discovery**: Structure directories by domain or feature
  - Good: `reference/finance.md`, `reference/sales.md`
  - Bad: `docs/file1.md`, `docs/file2.md`
- **Bundle comprehensive resources**: Include complete API docs, extensive examples, large datasets; no context penalty until accessed
- **Prefer scripts for deterministic operations**: Write `validate_form.py` rather than asking Claude to generate validation code
- **Make execution intent clear**:
  - "Run `analyze_form.py` to extract fields" (execute)
  - "See `analyze_form.py` for the extraction algorithm" (read as reference)
- **Test file access patterns**: Verify Claude can navigate your directory structure by testing with real requests

**Example:**

```
bigquery-skill/
├── SKILL.md (overview, points to reference files)
└── reference/
    ├── finance.md (revenue metrics)
    ├── sales.md (pipeline data)
    └── product.md (usage analytics)
```

When the user asks about revenue, Claude reads SKILL.md, sees the reference to `reference/finance.md`, and invokes bash to read just that file. The sales.md and product.md files remain on the filesystem, consuming zero context tokens until needed. This filesystem-based model is what enables progressive disclosure. Claude can navigate and selectively load exactly what each task requires.

For complete details on the technical architecture, see [How Skills work](/docs/en/agents-and-tools/agent-skills/overview#how-skills-work) in the Skills overview.

### MCP tool references

If your Skill uses MCP (Model Context Protocol) tools, always use fully qualified tool names to avoid "tool not found" errors.

**Format**: `ServerName:tool_name`

**Example**:

```markdown
Use the BigQuery:bigquery_schema tool to retrieve table schemas.
Use the GitHub:create_issue tool to create issues.
```

Where:

- `BigQuery` and `GitHub` are MCP server names
- `bigquery_schema` and `create_issue` are the tool names within those servers

Without the server prefix, Claude may fail to locate the tool, especially when multiple MCP servers are available.

### Avoid assuming tools are installed

Don't assume packages are available:

````markdown
**Bad example: Assumes installation**:
"Use the pdf library to process the file."

**Good example: Explicit about dependencies**:
"Install required package: `pip install pypdf`

Then use it:
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```"
````

## Technical notes

### YAML frontmatter requirements

The SKILL.md frontmatter requires `name` and `description` fields with specific validation rules:

- `name`: Maximum 64 characters, lowercase letters/numbers/hyphens only, no XML tags, no reserved words
- `description`: Maximum 1024 characters, non-empty, no XML tags

See the [Skills overview](/docs/en/agents-and-tools/agent-skills/overview#skill-structure) for complete structure details.

### Token budgets

Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds this, split it into separate files using the progressive disclosure patterns described earlier. For architectural details, see the [Skills overview](/docs/en/agents-and-tools/agent-skills/overview#how-skills-work).

## Checklist for effective Skills

Before sharing a Skill, verify:

### Core quality

- [ ] Description is specific and includes key terms
- [ ] Description includes both what the Skill does and when to use it
- [ ] SKILL.md body is under 500 lines
- [ ] Additional details are in separate files (if needed)
- [ ] No time-sensitive information (or in "old patterns" section)
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract
- [ ] File references are one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps

### Code and scripts

- [ ] Scripts solve problems rather than punt to Claude
- [ ] Error handling is explicit and helpful
- [ ] No "voodoo constants" (all values justified)
- [ ] Required packages listed in instructions and verified as available
- [ ] Scripts have clear documentation
- [ ] No Windows-style paths (all forward slashes)
- [ ] Validation/verification steps for critical operations
- [ ] Feedback loops included for quality-critical tasks

### Testing

- [ ] At least three evaluations created
- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated (if applicable)

## Next steps

<CardGroup cols={2}>
  <Card
    title="Get started with Agent Skills"
    icon="rocket"
    href="/docs/en/agents-and-tools/agent-skills/quickstart"
  >
    Create your first Skill
  </Card>
  <Card
    title="Use Skills in Claude Code"
    icon="terminal"
    href="https://code.claude.com/docs/en/skills"
  >
    Create and manage Skills in Claude Code
  </Card>
  <Card
    title="Use Skills in the Agent SDK"
    icon="cube"
    href="/docs/en/agent-sdk/skills"
  >
    Use Skills programmatically in TypeScript and Python
  </Card>
  <Card
    title="Use Skills with the API"
    icon="code"
    href="/docs/en/build-with-claude/skills-guide"
  >
    Upload and use Skills programmatically
  </Card>
</CardGroup>



# FILE: references/dynamic_context_from_cursur.md

This document explains Cursor's "dynamic context discovery" pattern, teaching an agent to improve token efficiency and response quality by loading context from files on demand rather than relying on static pre-loading.

# Dynamic Context Discovery

Coding agents are quickly changing how software is built. Their rapid improvement comes from both improved agentic models and better context engineering to steer them.

Cursor's agent harness, the instructions and tools we provide the model, is optimized individually for every new frontier model we support. However, there are context engineering improvements we can make, such as how we gather context and optimize token usage over a long trajectory, that apply to all models inside our harness.

As models have become better as agents, we've found success by providing fewer details up front, making it easier for the agent to pull relevant context on its own. We're calling this pattern **dynamic context discovery**, in contrast to static context which is always included.

## Files for dynamic context discovery

Dynamic context discovery is far more token-efficient, as only the necessary data is pulled into the context window. It can also improve the agent's response quality by reducing the amount of potentially confusing or contradictory information in the context window.

Here's how we've used dynamic context discovery in Cursor:

* Turning long tool responses into files
* Referencing chat history during summarization
* Supporting the Agent Skills open standard
* Efficiently loading only the MCP tools needed
* Treating all integrated terminal sessions as files

## 1. Turning long tool responses into files

Tool calls can dramatically increase the context window by returning a large JSON response.

For first-party tools in Cursor, like editing files and searching the codebase, we can prevent context bloat with intelligent tool definitions and minimal response formats, but third-party tools (i.e. shell commands or MCP calls) don't natively get this same treatment.

The common approach coding agents take is to truncate long shell commands or MCP results. This can lead to data loss, which could include important information you wanted in the context. In Cursor, we instead write the output to a file and give the agent the ability to read it. The agent calls `tail` to check the end, and then read more if it needs to.

This has resulted in fewer unnecessary summarizations when reaching context limits.

## 2. Referencing chat history during summarization

When the model's context window fills up, Cursor triggers a summarization step to give the agent a fresh context window with a summary of its work so far.

But the agent's knowledge can degrade after summarization since it's a lossy compression of the context. The agent might have forgotten crucial details about its task. In Cursor, we use the chat history as files to improve the quality of summarization.

After the context window limit is reached, or the user decides to summarize manually, we give the agent a reference to the history file. If the agent knows that it needs more details that are missing from the summary, it can search through the history to recover them.

## 3. Supporting the Agent Skills open standard

Cursor supports **Agent Skills**, an open standard for extending coding agents with specialized capabilities. Similar to other types of Rules, Skills are defined by files that tell the agent how to perform on a domain-specific task.

Skills also include a name and description which can be included as "static context" in the system prompt. The agent can then do dynamic context discovery to pull in relevant skills, using tools like `grep` and Cursor's semantic search.

Skills can also bundle executables or scripts relevant to the task. Since they're just files, the agent can easily find what's relevant to a particular skill.

## 4. Efficiently loading only the MCP tools needed

MCP is helpful for accessing secured resources behind OAuth. That could be production logs, external design files, or internal context and documentation for an enterprise.

Some MCP servers include many tools, often with long descriptions, which can significantly bloat the context window. Most of these tools go unused even though they are always included in the prompt. This compounds if you use multiple MCP servers.

It's not feasible to expect every MCP server to optimize for this. We believe it's the responsibility of the coding agents to reduce context usage. In Cursor, we support dynamic context discovery for MCP by syncing tool descriptions to a folder.

The agent now only receives a small bit of static context, including names of the tools, prompting it to look up tools when the task calls for it. In an A/B test, we found that in runs that called an MCP tool, this strategy reduced total agent tokens by 46.9% (statistically significant, with high variance based on the number of MCPs installed).

This file approach also unlocks the ability to communicate the status of MCP tools to the agent. For example, previously if an MCP server needed re-authentication, the agent would forget about those tools entirely, leaving the user confused. Now, it can actually let the user know to re-authenticate proactively.

## 5. Treating all integrated terminal sessions as files

Rather than needing to copy/paste the output of a terminal session into the agent input, Cursor now syncs the integrated terminal outputs to the local filesystem.

This makes it easy to ask "why did my command fail?" and allow the agent to understand what you're referencing. Since terminal history can be long, the agent can `grep` for only the relevant outputs, which is useful for logs from a long-running process like a server.

This mirrors what CLI-based coding agents see, with prior shell output in context, but discovered dynamically rather than injected statically.

## Simple abstractions

It's not clear if files will be the final interface for LLM-based tools.

But as coding agents quickly improve, files have been a simple and powerful primitive to use, and a safer choice than yet another abstraction that can't fully account for the future. Stay tuned for lots more exciting work to share in this space.



# FILE: references/agent_skills_spec_from_agentskills_io.md

# Overview

> A simple, open format for giving agents new capabilities and expertise.

Agent Skills are folders of instructions, scripts, and resources that agents can discover and use to do things more accurately and efficiently.

## Why Agent Skills?

Agents are increasingly capable, but often don't have the context they need to do real work reliably. Skills solve this by giving agents access to procedural knowledge and company-, team-, and user-specific context they can load on demand. Agents with access to a set of skills can extend their capabilities based on the task they're working on.

**For skill authors**: Build capabilities once and deploy them across multiple agent products.

**For compatible agents**: Support for skills lets end users give agents new capabilities out of the box.

**For teams and enterprises**: Capture organizational knowledge in portable, version-controlled packages.

## What can Agent Skills enable?

* **Domain expertise**: Package specialized knowledge into reusable instructions, from legal review processes to data analysis pipelines.
* **New capabilities**: Give agents new capabilities (e.g. creating presentations, building MCP servers, analyzing datasets).
* **Repeatable workflows**: Turn multi-step tasks into consistent and auditable workflows.
* **Interoperability**: Reuse the same skill across different skills-compatible agent products.

## Adoption

Agent Skills are supported by leading AI development tools.

## Open development

The Agent Skills format was originally developed by [Anthropic](https://www.anthropic.com/), released as an open standard, and has been adopted by a growing number of agent products. The standard is open to contributions from the broader ecosystem.

[View on GitHub](https://github.com/agentskills/agentskills)

## Get started

# What are skills?

> Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows.

At its core, a skill is a folder containing a `SKILL.md` file. This file includes metadata (`name` and `description`, at minimum) and instructions that tell an agent how to perform a specific task. Skills can also bundle scripts, templates, and reference materials.

```directory  theme={null}
my-skill/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

## How skills work

Skills use **progressive disclosure** to manage context efficiently:

1. **Discovery**: At startup, agents load only the name and description of each available skill, just enough to know when it might be relevant.

2. **Activation**: When a task matches a skill's description, the agent reads the full `SKILL.md` instructions into context.

3. **Execution**: The agent follows the instructions, optionally loading referenced files or executing bundled code as needed.

This approach keeps agents fast while giving them access to more context on demand.

## The SKILL.md file

Every skill starts with a `SKILL.md` file containing YAML frontmatter and Markdown instructions:

```mdx  theme={null}
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
---

# PDF Processing

## When to use this skill
Use this skill when the user needs to work with PDF files...

## How to extract text
1. Use pdfplumber for text extraction...

## How to fill forms
...
```

The following frontmatter is required at the top of `SKILL.md`:

* `name`: A short identifier
* `description`: When to use this skill

The Markdown body contains the actual instructions and has no specific restrictions on structure or content.

This simple format has some key advantages:

* **Self-documenting**: A skill author or user can read a `SKILL.md` and understand what it does, making skills easy to audit and improve.

* **Extensible**: Skills can range in complexity from just text instructions to executable code, assets, and templates.

* **Portable**: Skills are just files, so they're easy to edit, version, and share.

## Next steps

* [View the specification](/specification) to understand the full format.
* [Add skills support to your agent](/integrate-skills) to build a compatible client.
* [See example skills](https://github.com/anthropics/skills) on GitHub.
* [Read authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) for writing effective skills.
* [Use the reference library](https://github.com/agentskills/agentskills/tree/main/skills-ref) to validate skills and generate prompt XML.

# Specification

> The complete format specification for Agent Skills.

This document defines the Agent Skills format.

## Directory structure

A skill is a directory containing at minimum a `SKILL.md` file:

```text
skill-name/
└── SKILL.md          # Required
```

[!Tip]
> You can optionally include [additional directories](#optional-directories) such as `scripts/`, `references/`, and `assets/` to support your skill.

## SKILL.md format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter (required)

```yaml  theme={null}
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

With optional fields:

```yaml  theme={null}
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

| Field           | Required | Constraints                                                                                                       |
| --------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.             |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                                 |
| `license`       | No       | License name or reference to a bundled license file.                                                              |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata.                                                              |
| `allowed-tools` | No       | Space-delimited list of pre-approved tools the skill may use. (Experimental)                                      |

#### `name` field

The required `name` field:

* Must be 1-64 characters
* May only contain unicode lowercase alphanumeric characters and hyphens (`a-z` and `-`)
* Must not start or end with `-`
* Must not contain consecutive hyphens (`--`)
* Must match the parent directory name

Valid examples:

```yaml  theme={null}
name: pdf-processing
```

```yaml  theme={null}
name: data-analysis
```

```yaml  theme={null}
name: code-review
```

Invalid examples:

```yaml  theme={null}
name: PDF-Processing  # uppercase not allowed
```

```yaml  theme={null}
name: -pdf  # cannot start with hyphen
```

```yaml  theme={null}
name: pdf--processing  # consecutive hyphens not allowed
```

#### `description` field

The required `description` field:

* Must be 1-1024 characters
* Should describe both what the skill does and when to use it
* Should include specific keywords that help agents identify relevant tasks

Good example:

```yaml  theme={null}
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

Poor example:

```yaml  theme={null}
description: Helps with PDFs.
```

#### `license` field

The optional `license` field:

* Specifies the license applied to the skill
* We recommend keeping it short (either the name of a license or the name of a bundled license file)

Example:

```yaml  theme={null}
license: Proprietary. LICENSE.txt has complete terms
```

#### `compatibility` field

The optional `compatibility` field:

* Must be 1-500 characters if provided
* Should only be included if your skill has specific environment requirements
* Can indicate intended product, required system packages, network access needs, etc.

Examples:

```yaml  theme={null}
compatibility: Designed for Claude Code (or similar products)
```

```yaml  theme={null}
compatibility: Requires git, docker, jq, and access to the internet
```

[!Note]
> Most skills do not need the `compatibility` field.

#### `metadata` field

The optional `metadata` field:

* A map from string keys to string values
* Clients can use this to store additional properties not defined by the Agent Skills spec
* We recommend making your key names reasonably unique to avoid accidental conflicts

Example:

```yaml  theme={null}
metadata:
  author: example-org
  version: "1.0"
```

#### `allowed-tools` field

The optional `allowed-tools` field:

* A space-delimited list of tools that are pre-approved to run
* Experimental. Support for this field may vary between agent implementations

Example:

```yaml  theme={null}
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

### Body content

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions. Write whatever helps agents perform the task effectively.

Recommended sections:

* Step-by-step instructions
* Examples of inputs and outputs
* Common edge cases

Note that the agent will load this entire file once it's decided to activate a skill. Consider splitting longer `SKILL.md` content into referenced files.

## Optional directories

### scripts/

Contains executable code that agents can run. Scripts should:

* Be self-contained or clearly document dependencies
* Include helpful error messages
* Handle edge cases gracefully

Supported languages depend on the agent implementation. Common options include Python, Bash, and JavaScript.

### references/

Contains additional documentation that agents can read when needed:

* `REFERENCE.md` - Detailed technical reference
* `FORMS.md` - Form templates or structured data formats
* Domain-specific files (`finance.md`, `legal.md`, etc.)

Keep individual [reference files](#file-references) focused. Agents load these on demand, so smaller files mean less use of context.

### assets/

Contains static resources:

* Templates (document templates, configuration templates)
* Images (diagrams, examples)
* Data files (lookup tables, schemas)

## Progressive disclosure

Skills should be structured for efficient use of context:

1. **Metadata** (\~100 tokens): The `name` and `description` fields are loaded at startup for all skills
2. **Instructions** (\< 5000 tokens recommended): The full `SKILL.md` body is loaded when the skill is activated
3. **Resources** (as needed): Files (e.g. those in `scripts/`, `references/`, or `assets/`) are loaded only when required

Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files.

## File references

When referencing other files in your skill, use relative paths from the skill root:

```markdown  theme={null}
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.

## Validation

Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference library to validate your skills:

```bash  theme={null}
skills-ref validate ./my-skill
```

This checks that your `SKILL.md` frontmatter is valid and follows all naming conventions.

# Integrate skills into your agent

> How to add Agent Skills support to your agent or tool.

This guide explains how to add skills support to an AI agent or development tool.

## Integration approaches

The two main approaches to integrating skills are:

**Filesystem-based agents** operate within a computer environment (bash/unix) and represent the most capable option. Skills are activated when models issue shell commands like `cat /path/to/my-skill/SKILL.md`. Bundled resources are accessed through shell commands.

**Tool-based agents** function without a dedicated computer environment. Instead, they implement tools allowing models to trigger skills and access bundled assets. The specific tool implementation is up to the developer.

## Overview

A skills-compatible agent needs to:

1. **Discover** skills in configured directories
2. **Load metadata** (name and description) at startup
3. **Match** user tasks to relevant skills
4. **Activate** skills by loading full instructions
5. **Execute** scripts and access resources as needed

## Skill discovery

Skills are folders containing a `SKILL.md` file. Your agent should scan configured directories for valid skills.

## Loading metadata

At startup, parse only the frontmatter of each `SKILL.md` file. This keeps initial context usage low.

### Parsing frontmatter

```typescript
function parseMetadata(skillPath):
    content = readFile(skillPath + "/SKILL.md")
    frontmatter = extractYAMLFrontmatter(content)

    return {
        name: frontmatter.name,
        description: frontmatter.description,
        path: skillPath
    }
```

### Injecting into context

Include skill metadata in the system prompt so the model knows what skills are available.

Follow your platform's guidance for system prompt updates. For example, for Claude models, the recommended format uses XML:

```xml  theme={null}
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extracts text and tables from PDF files, fills forms, merges documents.</description>
    <location>/path/to/skills/pdf-processing/SKILL.md</location>
  </skill>
  <skill>
    <name>data-analysis</name>
    <description>Analyzes datasets, generates charts, and creates summary reports.</description>
    <location>/path/to/skills/data-analysis/SKILL.md</location>
  </skill>
</available_skills>
```

For filesystem-based agents, include the `location` field with the absolute path to the SKILL.md file. For tool-based agents, the location can be omitted.

Keep metadata concise. Each skill should add roughly 50-100 tokens to the context.

## Security considerations

Script execution introduces security risks. Consider:

* **Sandboxing**: Run scripts in isolated environments
* **Allowlisting**: Only execute scripts from trusted skills
* **Confirmation**: Ask users before running potentially dangerous operations
* **Logging**: Record all script executions for auditing

## Reference implementation

The [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) library provides Python utilities and a CLI for working with skills.

For example:

**Validate a skill directory:**

```text
skills-ref validate <path>
```

**Generate `<available_skills>` XML for agent prompts:**

```text
skills-ref to-prompt <path>...
```

Use the library source code as a reference implementation.



# FILE: skills/inspecting-the-environment/SKILL.md

---
name: inspect-environment
description: Fast environment briefing for agents and subagents. Use at session start to learn OS/shell, container/WSL/VM status, git repo + upstream + dirty state, Python venv status/locations, markdown folders to read, and availability of common tools (uv, mcpc, rg/grep/jq/git/python/node/npm/pnpm, etc.).
---
# Environment Inspection

## Overview
Collect a quick, machine-readable snapshot of the current workspace so agents know operating constraints, dev tooling, and where to look first for context.

## Quick Start
Generate JSON (default):
```bash
python scripts/inspect_environment.py
```
Readable text:
```bash
python scripts/inspect_environment.py --format text
```

Key fields:
- `os`: system, release, version, machine
- `shell`: detected shell/command host
- `environment`: container hint, WSL flag, VM hint (via systemd-detect-virt when available)
- `git`: repo presence, root, branch, upstream, dirty state
- `python`: interpreter path/version, active venv/conda, whether running inside a venv
- `virtualenv_dirs`: nearby `.venv`/`venv`/`env` folders
- `markdown_dirs`: directories (depth-limited) containing `.md` files worth skimming
- `tools`: availability of common CLIs (uv, mcpc, rg/grep/jq/git/python/node/npm/pnpm, etc.)

## Options
- `--root PATH` to inspect a different directory (default: cwd).
- `--format json|text` for programmatic vs quick-read output (default: json).
- `--md-limit N` / `--md-depth N` to cap markdown directory discovery (defaults: 40 dirs, depth 5; skips .git/node_modules/.venv/venv/.tox/dist/build/.cache).
- `--extra-tool NAME` (repeatable) to probe additional binaries.

## Notes and Heuristics
- Container detection uses marker files and `/proc/1/cgroup`; WSL is reported separately.
- VM detection is opportunistic via `systemd-detect-virt`; missing tools yield `null`.
- Git checks are no-op outside a repo and never modify state.
- Traversal is pruned to avoid heavy dirs; adjust limits if you need more coverage.



# FILE: skills/using-mcp-tools-with-mcpc/SKILL.md

---
name: using-mcp-tools-with-mcpc
description: Use mcpc CLI to interact with MCP servers - call tools, read resources, get prompts. Use when working with Model Context Protocol servers, calling MCP tools, or accessing MCP resources programmatically; prefer key:=value bindings over raw JSON bodies.
allowed-tools: Bash(mcpc:*), Bash(node dist/cli/index.js:*), Read, Grep
---

# mcpc: MCP command-line client

Use `mcpc` to interact with MCP (Model Context Protocol) servers from the command line.
This is more efficient than function calling - generate shell commands instead.

## Trust pattern
- **Always**: Read-only mcpc commands in the sandbox (e.g., `tools-list`, `tools-get`, `resources-list/read`, `prompts-list/get`, `tools-call` for read/search-only endpoints), session status checks, and commands that reuse already-created auth profiles.
- **Ask**: Anything that writes or needs network/OAuth (login/logout must be human-initiated in the foreground), connecting to new servers, commands that create/update/delete data, helper scripts that write files, or when sandbox blocks the command.
- **Never**: Destructive workspace actions (moves/deletes) without explicit user request; connecting to unknown MCP servers without instruction; backgrounding `mcpc <server> login` or trying to auto-open a browser.

## Quick reference

```bash
# List sessions and auth profiles
mcpc

# Show server info
mcpc <server>
mcpc @<session>

# Tools
mcpc <target> tools-list
mcpc <target> tools-get <tool-name>
mcpc <target> tools-call <tool-name> key:=value key2:="string value"

# Resources
mcpc <target> resources-list
mcpc <target> resources-read <uri>

# Prompts
mcpc <target> prompts-list
mcpc <target> prompts-get <prompt-name> arg1:=value1

# Sessions (persistent connections)
mcpc <server> connect @<name>
mcpc @<name> <command>
mcpc @<name> close

# Authentication
mcpc <server> login
mcpc <server> logout
```

## Target types

- `mcp.example.com` - Direct HTTPS connection to remote server
- `localhost:8080` or `127.0.0.1:8080` - Local HTTP server (http:// is default for localhost)
- `@session-name` - Named persistent session (faster, maintains state)
- `config-entry` - Entry from config file (with `--config`)

## Passing arguments

Prefer `key:=value` bindings. Use inline JSON only when needed (e.g., first-arg object or complex arrays):   

```bash
# String values
mcpc @s tools-call search query:="hello world"

# Numbers, booleans, null (auto-parsed as JSON)
mcpc @s tools-call search query:="hello" limit:=10 enabled:=true

# Complex JSON values
mcpc @s tools-call search config:='{"nested":"value"}' items:='[1,2,3]'

# Force string type with JSON quotes
mcpc @s tools-call search id:='"123"'

# Inline JSON object (if first arg starts with { or [)
mcpc @s tools-call search '{"query":"hello","limit":10}'

# From stdin (auto-detected when piped)
echo '{"query":"hello"}' | mcpc @s tools-call search
```

## JSON output for scripting

Always use `--json` flag for machine-readable output:

```bash
# Get tools as JSON
mcpc --json @apify tools-list

# Call tool and parse result with jq
mcpc --json @apify tools-call search query:="test" | jq '.content[0].text'

# Chain commands
mcpc --json @server1 tools-call get-data | mcpc @server2 tools-call process
```

## Sessions for efficiency

Create sessions for repeated interactions:

```bash
# Create session (or reconnect if exists)
mcpc mcp.apify.com connect @apify

# Use session (faster - no reconnection overhead)
mcpc @apify tools-list
mcpc @apify tools-call search query:="test"

# Restart session (useful after server updates)
mcpc @apify restart

# Close when done
mcpc @apify close
```

**Session states:**
- 🟢 **live** - Bridge running, server might or might not be responding
- 🟡 **crashed** - Bridge crashed; auto-restarts on next use
- 🔴 **expired** - Server rejected session; needs `close` and reconnect

## Authentication

**OAuth (interactive login – human-only, foreground)**:
- `mcpc <server> login` opens the browser; mcpc never opens it itself. Do not background this command or it will miss the localhost callback.
- Run login once per profile, then reuse the saved credentials in scripts.
- Re-run login to refresh/change scopes.

Python preflight to enforce “login first” in scripts (no automatic browser launches):
```python
import json, os, sys

server = os.environ.get("MCP_SERVER", "mcp.apify.com")
profile = os.environ.get("MCP_PROFILE", "default")
profiles_path = os.path.join(os.path.expanduser("~"), ".mcpc", "profiles.json")

try:
    data = json.load(open(profiles_path, "r", encoding="utf-8"))
    profiles = data.get("profiles", [])
except FileNotFoundError:
    profiles = []

has_profile = any(p.get("server") == server and p.get("name") == profile for p in profiles)
if not has_profile:
    print(f"No mcpc auth profile '{profile}' for {server}.")
    print(f"Run this yourself (foreground): mcpc {server} login --profile {profile}")
    sys.exit(1)
```

After the preflight succeeds, scripts may call `mcpc --profile <name> ...` or rely on the default profile.

**Bearer token**:
```bash
mcpc -H "Authorization: Bearer $TOKEN" mcp.apify.com tools-list
mcpc -H "Authorization: Bearer $TOKEN" mcp.apify.com connect @myserver
```

## Proxy server for AI isolation

Create a proxy MCP server that hides authentication tokens:

```bash
# Human creates authenticated session with proxy
mcpc mcp.apify.com connect @ai-proxy --proxy 8080

# AI agent connects to proxy (no access to original tokens)
# Note: localhost defaults to http://
mcpc localhost:8080 tools-list
mcpc 127.0.0.1:8080 connect @sandboxed
```

## Common patterns

**List and inspect tools**:
```bash
mcpc @s tools-list
mcpc @s tools-get tool-name
```

**Call tool and extract text result**:
```bash
mcpc --json @s tools-call my-tool | jq -r '.content[0].text'
```

**Read resource content**:
```bash
mcpc @s resources-read "file:///path/to/file"
```

**Use config file for local servers**:
```bash
mcpc --config .vscode/mcp.json filesystem resources-list
```

## Exit codes

- `0` - Success
- `1` - Client error (invalid arguments)
- `2` - Server error (tool failed)
- `3` - Network error
- `4` - Authentication error

## Debugging

```bash
# Verbose output shows protocol details
mcpc --verbose @s tools-call my-tool
```

## Example script

See [`docs/examples/company-lookup.sh`](../examples/company-lookup.sh) for a complete example
of an AI-generated script that validates prerequisites and calls MCP tools.



# FILE: skills/creating-mcp-code-mode-skills/SKILL.md

---
name: creating-mcp-code-mode-skills
version: 1.3.0
description: >
  A meta-skill for authoring high-performance, verifiable, long-running MCP skills
  using Code Mode. This skill blends Anthropic and OpenAI skill-authoring guidance
  with Code-Mode-first, MCP-backed execution, dynamic context discovery, and
  file-backed agent harnesses.

metadata:
  short-description: Author modular, deterministic, token-efficient MCP skills.
  audience: skill-authors
  stability: stable
---

# Creating MCP Code Mode Skills

This skill teaches **how to author agent skills**, not how to prompt models. You are designing **deterministic scaffolding for a probabilistic system**. Assume the model is capable. Favor **constraints, structure, and files** over prose.

## Mental Model

> **The model reasons.  
> Code executes.  
> The filesystem remembers.**

A Code Mode MCP skill is a **closed-loop control system**, not a function call.

- Reasoning lives in the model
- Work happens in code
- Truth persists on disk

If information is large, fragile, repetitive, or stateful, it does **not** belong in the context window.

## 0. Prior art

Before you start skill creation, and if you have any questions about how to proceed, check the following references (you can examine the first line of the file to understand its contents before deciding whether to read it):

- reference/skill_creator_from_codex.md
- reference/skill_creator_from_anthropic.md
- reference/skill_authoring_best_practices_from_anthropic.md
- reference/dynamic_context_from_cursor.md

## 1. What a Skill *Is*

A skill is:

- A **capability contract**, not a conversation
- A **repeatable procedure**, not a one-off answer
- A **tool-augmented behavior**, not just text generation

Every skill must clearly define:

- What problem it solves
- When it should be used
- What it is allowed to do
- How it makes progress
- How it fails safely

## 2. Architectural First Principles

### 2.1 Code Is the Only Tool Interface

When code execution is available:

- The model MUST NOT call tools directly
- MCP access MUST occur via executable code
- Validation, retries, and error handling live in scripts

Models are more reliable at **writing code** than emitting fragile tool calls.

### 2.2 Dynamic Context Discovery (Cursor)

Static context is a liability.

Do NOT preload:

- Full MCP schemas
- Large tool responses
- Logs or tables

Instead:

- Start minimal
- Discover on demand
- Write to files
- Query selectively

Context must be **discoverable, queryable, and discardable**.

Dynamic context patterns (do these instead of dumping blobs into chat):

- Write large tool/MCP responses to files; inspect the tail first, then read more only as needed.
- Treat long chat history and terminal output as files you can grep to recover details after summarization.
- Cache MCP tool descriptions/status to files and load only the tools needed for the task (empirically cuts token use nearly in half in Cursor A/B).
- Use files as the durable interface for anything that must outlive the current context window.

### 2.3 Files Are the Context Boundary

For long-running agents, files are the **only reliable memory**.

Anything that must survive:

- retries
- summarization
- context eviction
- multi-phase execution

**must be written to disk**.

Canonical artifacts:

- `plan.json` — immutable intent
- `progress.txt` — append-only log
- `results.json` — structured outputs # you can use more output files than just results.json, and you should be thoughtful about clobbering
- `errors.log` — diagnostics

## 3. Skill Structure & Naming

### 3.1 Naming

Use **gerund form** to describe capability:

- `provisioning-infrastructure`
- `syncing-databases`
- `auditing-permissions`

Skills describe **process**, not outcome.

### 3.2 Directory Layout

```text
SKILL.md
scripts/
references/
mcp_tools/
templates/
```

#### SKILL.md

- Entry point and behavioral contract
- Invocation rules
- Under 500 lines
- Progressive disclosure: static prompt carries only name/description; load SKILL.md body and references on demand; execute scripts for real work.

#### scripts/

- Deterministic executables
- Defensive and idempotent
- Use `mcpc --json`.

#### references/

- Lightweight, navigable context
- Tables of contents
- Explicit pointers from SKILL.md
- No monolithic dumps

#### mcp_tools/

- Dynamic Context Discovery cache
- Never pasted directly into prompts
- Generated on demand via:

```bash
mcpc <target> tools-get <tool-name> --json
```

#### templates/

- Low-entropy schemas (JSON/YAML)
- Plans, approvals, reports

#### Keep the file set minimal

- Only include what the agent needs (SKILL.md + scripts + references + assets/templates).
- Avoid extra docs (README/CHANGELOG/etc.) that bloat discovery and add ambiguity.

## 4. Code Mode via mcpc (Proxy Pattern)

All MCP interaction MUST go through `mcpc`. Use `mcpc --help` to learn the tool. All arguments to tool calls are bound via `:=`.  session names must be quoted in powershell, `'@session'`.

Required properties:

- `--json` output only
- Filter before returning to context
- Prefer `jq` or equivalent

Example:

```bash
mcpc --json @session tools-call get_data id:="123" \
  | jq '{id, status, summary}' > results.json
```

The model may then read **only** `results.json`.

## 5. Scripts, References, Templates

### Scripts (Required)

- Execute work
- Validate inputs
- Verify MCP connectivity
- Handle retries
- Fail locally

### Templates (Required)

- Define shape, not content
- Used for `plan.json`, approvals, reports

### References (Required, Lightweight)

Good references:

- Are indexed and navigable
- Are pointed to, not dumped
- Respect token economy
- May include cached MCP schemas

Bad references:

- Large static blobs
- Blindly copied tool specs

## 6. Trust Policy (Always / Never / Ask)

Each skill MUST define its **own** trust policy.

Defaults are a baseline only.

### ALWAYS

- Read-only inspection
- Listing tools
- Viewing references

### NEVER

- Credential exfiltration
- Irreversible destructive actions
- Executing untrusted code

## ASK

- State-changing MCP calls
- Deletes, writes, deploys
- Any irreversible action

Skills SHOULD extend these rules.

## 7. Degrees of Freedom

Match freedom to task fragility and variability. Each level constrains **context, reasoning, and tools**.

### High Freedom — Explore, *Figure out what to do.*

- Context: natural language, summaries, file pointers
- Reasoning: prompt-style thinking, agents/subagents
- Tools: inspection, planning

### Medium Freedom — Shape, *Configure a known solution.*

- Context: templates, schemas, parameters
- Reasoning: constrained adaptation
- Tools: parameterized scripts, validation helpers

### Low Freedom — Execute, *Do exactly one safe thing.*

- Context: fully specified files
- Reasoning: none at execution time
- Tools: deterministic, validated scripts

**Rule:** Never mix freedom levels.
Split workflows: **decide → configure → execute**.

## 8. Long-Running Agent Harness

Assume interruption. Design for restart:

- Write progress after every step
- Make scripts idempotent
- Resume by reading files

If the agent restarts, it should know exactly where it is.

## 9. Canonical Execution Loop

1. Discover minimal context
2. Cache schemas/data as files
3. Write `plan.json`
4. Validate environment
5. Execute scripts
6. Persist results
7. Summarize selectively

## 10. Explicit Anti-Patterns

- Dumping MCP JSON into chat
- Copying full schemas into prompts
- Trusting tool calls without verification
- Relying on model memory instead of files

## 11. Reference-derived Practices

- Enforce progressive disclosure: static metadata → on-demand references → executed scripts.
- Challenge every paragraph for token cost; prefer concise examples over exposition.
- Match degree-of-freedom (explore/shape/execute) to task fragility, and keep phases separate.
- Default to files as the memory surface for tool outputs, history, terminal logs, and MCP tool caches.
- Keep the skill artifact set lean; remove auxiliary docs unless they unlock execution.

## Final Principle

> **If it matters, write it down.**

Code Mode MCP skills move truth *out of the model* and into code, files, and structure. The model is a strategist — not a storage device.



# FILE: skills/creating-skills/SKILL.md

---
name: creating-skills
description: >
  General skill authoring and improvement. Use when creating or updating any skill (with or without MCP),
  selecting structure, generating scaffolds, or packaging resources (scripts/references/assets/templates)
  that follow progressive disclosure, deterministic execution, and restartable artifacts.
---

# Creating Skills (General)

This skill helps you design and ship skills that are concise, restartable, and discoverable—whether or not MCP is involved. Assume the model is capable; focus on structure, guardrails, and on-disk artifacts.

## Quick Start

- Pick scope + name first (gerund, hyphen-case, ≤64 chars). Examples: `creating-skills`, `auditing-permissions`.
- Run the scaffold script when starting fresh: `python creating-skills/scripts/init_skill.py <skill-name> --path <target> [--resources scripts,references,assets,templates] [--examples]`.
- Keep SKILL.md under 500 lines; push bulk info into `references/` or `templates/`; keep references one level deep.
- Use the decide → configure → execute pattern; never mix freedom levels in one step.
- Persist intent/results: `plan.json` (intent), `progress.log` (append-only log), `results.json` (structured outputs), `errors.log` (diagnostics). Do not write inside skill bundles during use.
- Observability: log execution steps/commands to append-only files so the agent can observe flow; use tail/grep/summarize instead of dumping entire logs into context to stay token-efficient.

## Trust Policy

- ALWAYS: read/list files, list tools, dry-run planning.
- ASK: writes, packaging, networked installs, destructive actions.
- NEVER: credential exfil, irreversible deletes, running untrusted code.

## Degrees of Freedom

- High (explore): gather examples, choose structure, confirm triggers.
- Medium (shape): fill templates, parameterize scripts, generate plan.json.
- Low (execute): run deterministic scripts, validators, packagers.

Keep phases separate: decide → configure → execute.

## Minimal Workflow (new skill)

1) **Clarify scope & triggers**
   - Define what the skill does, when it triggers, and its trust posture.
   - Normalize name; ensure description includes both capability and triggers.

2) **Scaffold**
   - Run `scripts/init_skill.py` (see Quick Start) into the target path (not inside this skill).
   - Choose only needed resources; delete placeholders you won’t use.

3) **Design info architecture**
   - Keep SKILL.md lean; link to references one level deep.
   - Use templates for plan/results/approvals; keep them low-entropy.
   - For code-heavy skills, prefer scripts over inline tool calls; make scripts idempotent and explicit about deps/timeouts.

4) **Author content**
   - Frontmatter: only `name` + `description` (third person, triggers included).
   - Body: imperative guidance, decision trees, checklists, and pointers to references/scripts/templates.
   - Include validation/feedback loops and “old patterns” if legacy behavior matters.

5) **Validate**
   - Run your own checks or add a validator script; ensure naming, description quality, path hygiene (forward slashes), and reference depth.
   - Add quick self-tests or exemplar tasks if possible.

6) **Package / iterate**
   - If packaging, zip the skill directory (excluding transient artifacts); keep a `dist/` outside the skill folder.
   - After usage, update SKILL.md or references based on observed gaps; log changes in `progress.log` (outside the skill).

## Content Patterns (apply as needed)

- **Progressive disclosure**: metadata → SKILL.md → references/scripts/templates on demand.
- **Decision trees**: route to the right reference/script; state defaults and escape hatches.
- **Templates**: prefer JSON/YAML/Markdown scaffolds over prose; keep strict vs flexible variants clear.
- **Validation loops**: plan → validate → execute; favor machine-checkable validators.
- **Dynamic context discovery**: write large outputs/logs to files; read with `head`/`tail`/`grep` as needed; avoid dumping blobs into context.
- **Execution logs**: keep append-only logs (progress/errors/results) for debuggability and learning; when sharing in context, prefer succinct summaries or tails to conserve tokens.

## References

- For deeper patterns and examples, open:
  - `references/skill-authoring-checklist.md` — condensed checklist and triggers
  - `references/templates/plan.json` — plan scaffold (edit per skill)
  - `references/templates/results.json` — results scaffold with `id` and `step`

Keep references succinct; add domain-specific guides per skill, one level deep.



# FILE: skills/slicing-long-contexts/SKILL.md

---
name: slicing-long-contexts
description: "Run Recursive Language Model-style map/reduce workflows via CLI (with codex or gemini: load long/complex inputs as data, slice by headings/chunks, issue sub-LM calls on slices, and optionally run a summarizing reducer; supports dry-run planning and divide-and-conquer for large or dense tasks."
---

# RLM CLI Runner

Use this skill to replicate the paper's REPL-based RLM pattern: treat the long prompt as data in a Python REPL, peek/slice it with code, and spawn recursive sub-LM calls (codex or gemini) on targeted snippets. Designed for dynamic context (write big outputs to files; read with tail/rg) and AGENTS preferences (plans/logs/results outside the skill dir).

Trust posture: ASK for writes/network; keep sandbox workspace-write unless a task requires more. `--with-network` toggles codex/gemini network; leave it off unless needed.

## When to use

- You have a long or complex input (multi-doc reasoning, codebase understanding, tool schemas, long chat history, terminal logs) and want RLM-style recursion to plan and execute sub-queries programmatically.
- You want a coordinator (root depth 0) that slices, runs sub-calls, and optionally a reducer pass to stitch/summarize.
- If the context clearly fits in the base LM and is low-density, consider a direct call; otherwise prefer this skill for dense inputs or when you need reproducible map/reduce artifacts.

## Inputs / Outputs

- **Inputs**: prompt file path, task/question, sub-call budget (count/time), recursion depth (max 1–2), target LM CLI (`codex`/`gemini`).
- **Outputs**: `FINAL_ANSWER` text; append-only `progress.log` / `results.json` in the repo root (not in `skills/`); slice files in `<out-dir>/rlm_slice_<tag>.txt`; per-subcall prompts in `<out-dir>/rlm_prompt_<tag>.txt`; sub-responses in `<out-dir>/rlm_subresp_<tag>.txt`; final in `<out-dir>/rlm_final.txt` (default `./rlm_outputs`).

## Trust / bounds

- ASK for writes; keep recursion depth <=2; cap sub-calls (e.g., max 5) and wall time. Prefer batching ~200k chars per sub-call to avoid thousands of calls (per paper’s Qwen prompt).
- Keep tmp paths deterministic; avoid leaking full prompt to sub-calls—send only slices.
- Use coding-capable models for sub-calls; weak coding models behave poorly per paper.

## Prereqs

- `uv` env active (`.venv` exists); run with `UV_CACHE_DIR=.uv-cache uv run ...`.
- CLI LMs configured: `codex` or `gemini`.
- Long prompt stored as a file (e.g., `prompt.txt`).

## Workflow (decide → configure → execute)

1) **Decide**: Define the question, budget (max sub-calls/time), depth limit (1–2), and slice strategy (markers vs fixed chunks).

1) **Configure dynamic context**:

- Set log paths (repo root): `progress.log`, `results.json`; append entries (id/step, inputs, outputs, status). Example log line: `{"id":"rlm-run-001","step":"subcall","tag":"h0","rc":0}`.
- Choose output dir (absolute or repo-relative; defaults to `<cwd>/rlm_outputs`): slices, prompts, sub-responses, final answer live here (configurable via `--out-dir/--output-dir`). Avoid writing inside `skills/`.
  - Note context stats for the REPL prompt: total chars, planned chunk sizes; record in log.

1) **Load prompt into REPL (root, depth 0)**:

   ```bash
   UV_CACHE_DIR=.uv-cache uv run python -q <<'PY'
   from pathlib import Path
   prompt = Path("prompt.txt").read_text()
   print("chars", len(prompt))
   print(prompt[:200])  # peek
   PY
   ```

   Keep `prompt` as the REPL variable; do not pipe the entire text to LMs.

2) **Plan slices** (programmatic): use markers or fallback to fixed-size chunking. See `references/repl-snippets.md`.
   - Optional: use heading-based slices (`--prefer-headings`) or install markdown tooling (`scripts/setup_markdown_tools.sh`) for richer parsing.

3) **Issue sub-calls on slices (depth=1)**:

   ```bash
   slice_file=/tmp/rlm_slice_ch1.txt
   UV_CACHE_DIR=.uv-cache uv run python - <<'PY'
   from pathlib import Path
   prompt = Path("prompt.txt").read_text()
   start = prompt.find("Chapter 1")
   end = prompt.find("Chapter 2")
   if start == -1:  # marker missing -> fallback to fixed chunk
       start, end = 0, 4000
   Path("/tmp/rlm_slice_ch1.txt").write_text(prompt[start:end])
   PY

   codex --model gpt-4o "Sub-task: list items before the Great Catastrophe in this slice.\n---\n$(cat $slice_file)" > /tmp/rlm_subresp_ch1.txt
   ```

   - Label each sub-response; keep a list in REPL (`sub_responses = {"ch1": Path(...).read_text()}`).
   - Batch slices when possible (target ~200k chars per call) to reduce call count.
   - Use `tail -n 40` to inspect long outputs instead of pasting everything.

4) **Aggregate + verify in REPL**:

   ```bash
   UV_CACHE_DIR=.uv-cache uv run python - <<'PY'
   from pathlib import Path
   subs = {
       "ch1": Path("/tmp/rlm_subresp_ch1.txt").read_text(),
       "ch3": Path("/tmp/rlm_subresp_ch3.txt").read_text(),
   }
   final = f"From chapter 1: {subs['ch1']}\nFrom chapter 3: {subs['ch3']}"
   Path("/tmp/rlm_final.txt").write_text(final)
   print(final)
   PY
   ```

   Optionally run a verification sub-call on the same slice to sanity-check a claim. Keep the final answer in a variable/file (analogous to FINAL_VAR in the paper) and emit once.

5) **Emit final answer**: print `FINAL_ANSWER`; log paths used and remaining budget. Stop if quality is adequate.

## Patterns to reuse

- Peek before sending: `print(prompt[:N])`, regex hits, newline splits.
- Keyword/TOC chunking: `prompt.split("Chapter 2")`, regex finditer for headers.
- Fixed-size fallback when markers are missing.
- Dynamic context: write big tool outputs to files; inspect with `tail`/`rg`; avoid copying whole blobs into prompts.
- Long docs (PRD/tech design/research/PDF): ask if divide-and-conquer is acceptable; draft a slice prompt that states per-chunk goals and aggregation plan; run `--dry-run` to choose headings vs fixed-size chunking before spending real sub-calls.
- Use cases beyond “large docs”: multi-document synthesis; codebase/source understanding; loading tool schemas/logs on demand; recovering detail from chat history by saving it to files; domain-scoped skills (sales/finance/etc.) to keep context tight.
- Reliability: use `--retry-count/--retry-wait` to recover transient failures; `--skip-on-failure` to keep going; `--verify-slices` for spot checks; `--overlap` to add coherence between fixed chunks; rerun/verify helpers live in `scripts/`.
- Sub-call labeling: keep per-slice tags so aggregation is deterministic.
- Long outputs: store sub-call outputs in variables/files and stitch; avoid regenerating from scratch.
- Verification: run spot-check sub-calls on the same slice; stop when adequate to cap variance.
- Cost/risk: sequential sub-calls are slower; async would help but is out-of-scope here—budget accordingly.

## References

- `references/repl-snippets.md` — slicing/search/compose helpers and logging snippets.
- `references/dynamic_context_from_cursur.md` — dynamic context discovery pattern to minimize tokens.
- `scripts/rlm_cli_runner.py --help` — view runnable options (slicing modes, code-mode, system prompt, logs).
- `scripts/setup_markdown_tools.sh` — optional markdown parsing helpers via uvx.
- `scripts/rerun_slice.py` / `scripts/verify_slice.py` — rerun or spot-check saved slice prompts.
- `scripts/slice_utils.py` (CLI): slice prompt → slices + manifest.
- `scripts/subcall_runner.py` (CLI): run one prompt with retries/skip.
- `scripts/aggregator.py` (CLI): aggregate sub-responses from manifest order.
- `scripts/summarize.py` (CLI): run a summarizing reducer over sub-responses in manifest order.
- `scripts/estimate_tokens.py` (CLI): estimate tokens for files (heuristic, optional tiktoken).

### Default vs advanced usage

- Default: use `rlm_cli_runner.py` to orchestrate slicing → subcalls → aggregation; it writes a manifest and all artifacts (slices/prompts/subresponses/final).
- Advanced (compose manually):
  1. `slice_utils.py --prompt ... --out-dir ...` → slices + `manifest.json`
  2. `subcall_runner.py --prompt rlm_prompt_<tag>.txt --cmd-template ...` → run one slice (retries/skip supported)
  3. `aggregator.py --manifest manifest.json --subresp-dir ... --out final.txt` → ordered reduce (optional dedup)
  4. `rerun_slice.py` / `verify_slice.py` for targeted reruns/spot-checks
  5. `summarize.py --manifest manifest.json --subresp-dir ... --cmd-template ... --out summary.txt` for a summarizing reducer

## Usage notes

- Codex example cmd template: `codex --sandbox workspace-write --ask-for-approval untrusted exec --model {model} "$(cat {prompt_path})"`
- Gemini example cmd template: `gemini --approval-mode auto_edit --model {model} "$(cat {prompt_path})"`
- If Codex needs access to ~/.codex, add a writable dir: `--add-dir ~/.codex` (and `--add-dir ~/.codex/skills` if needed). Runner convenience: `--with-user-codex-access` appends these.
- Network: `--with-network` adds `-c sandbox_workspace_write.network_access=true` for Codex. Gemini CLI is networked by default; there is no user-facing flag to disable it.
- Greedy path: `--greedy-first` will run a single summarizing call (using `--summary-cmd-template`) when the prompt fits under `--greedy-max-chars` (default 180k), skipping slicing.
- Token warning: runner estimates tokens (heuristic) and warns at `--warn-tokens` (default 64k) that the doc is likely long enough to divide and conquer.
- Note: In WSL, symlinks to /mnt/c may still be blocked by NTFS perms/sandbox. Prefer WSL-local ~/.codex/.gemini or mount C: with metadata so the CLI can write sessions.

## Common commands

- Codex, headings, 3 slices, network off:

  ```bash
  python skills/rlm-cli-runner/scripts/rlm_cli_runner.py \\
    --prompt references/work.md \\
    --question "Summarize top tasks" \\
    --prefer-headings --max-slices 3 \\
    --approval-flags "--sandbox workspace-write --ask-for-approval untrusted"
  ```

- Gemini with network, custom out dir:

  ```bash
  python skills/rlm-cli-runner/scripts/rlm_cli_runner.py \\
    --prompt prompt.txt --question "Find risks" \\
    --cmd-template 'gemini --approval-mode auto_edit --model {model} "$(cat {prompt_path})"' \\
    --with-network --out-dir /tmp/rlm_run \\
    --approval-flags ""  # gemini handles approval-mode
  ```

- Override template that needs {question}:

  ```bash
  python skills/rlm-cli-runner/scripts/rlm_cli_runner.py \\
    --prompt prompt.txt --question "List blockers" \\
    --cmd-template 'codex {approval_flags} exec --model {model} "{question}\\n\\n$(cat {prompt_path})"'
  ```

Note: `--prompt` must point to an existing file and `--question` cannot be empty; the runner will error otherwise.

## Logging helpers

- Runner logs to `progress.log` (init, slices_ready, subcall) and `results.json` (final) using JSONL; optionally set `--run-id` to tag all entries.
- To append manual notes in the same format, use the helper:  

  ```bash
  python skills/rlm-cli-runner/scripts/log_entry.py --log progress.log --run-id rlm-run-001 --step note --kv message="Paused for approval" --timestamp
  ```



# FILE: /home/aufrank/.codex/AGENTS.md

# AGENTS.md instructions for /home/aufrank

<INSTRUCTIONS>
## Skills
A skill is a set of local instructions stored in a `SKILL.md` file. Frontmatter keeps the skill list in context automatically; no need to enumerate it here. When a task matches or names a skill, open its `SKILL.md` and follow the workflow.
### How to use skills
- Discovery: Use the skill list already present in context; skill bodies live on disk at their listed paths.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- Missing/blocked: If a named skill isn't in the list or the path can't be read, say so briefly and continue with the best fallback.
- How to use a skill (progressive disclosure):
  1) After deciding to use a skill, open its `SKILL.md`. Read only enough to follow the workflow.
  2) If `SKILL.md` points to extra folders such as `references/`, load only the specific files needed for the request from within that skill's directory; don't bulk-load everything.
  3) If `scripts/` exist, prefer running or patching them instead of retyping large code blocks. Execute skill scripts with absolute paths (never by changing into the skill directory). Write outputs to relevant locations in the current project/repo—not into the skill's script directory.
  4) If `assets/` or templates exist, reuse them instead of recreating from scratch.
- Coordination and sequencing:
  - If multiple skills apply, choose the minimal set that covers the request and state the order you'll use them.
  - Announce which skill(s) you're using and why (one short line). If you skip an obvious skill, say why.
- User interaction:
  - Favor interactive decisions: use AskUser-style prompts/tools and offer meaningful options when they exist; avoid forcing A/B/C unless there are real alternatives.
- Version control habits (user preference):
  - Commit early/commit often; nag if context is getting too large to summarize into a clear commit message.
  - Work in feature branches by default; plan to summarize commits in PRs (squash/rebase per team norms).
- LSP leverage:
  - Encourage adding language-relevant LSPs to projects and building skills/utilities/CICD hooks that use them; treat LSPs as first-class discovery/navigation tools alongside CLI and agent capabilities.
  - Prefer `pyrefly` for Python and `@typescript/native-preview` for TypeScript when available.
- Context hygiene:
  - Keep context small: summarize long sections; load only what’s needed; avoid deep reference-chasing beyond files linked from `SKILL.md`; pick only relevant variant refs and note the choice.
- Workflow orchestration (general pattern, skills included):
  - Define clear inputs/outputs for each step; capture intermediates on disk so steps can be restarted or reused.
  - Make outputs chainable (machine-readable formats, predictable filenames/paths) so they can feed other scripts or tools; avoid writing into skill directories.
  - Treat flows like DAGs: decide dependencies upfront, then execute in topological order; resume by reading prior outputs instead of re-deriving context.
  - Log decisions and results alongside artifacts (e.g., `progress.txt`, `results.json`) for verifiability and restartability.
- Default agent quality:
  - Prefer machine-readable outputs (JSON/CSV/NDJSON) with minimal schemas/examples; use predictable filenames/paths for chaining.
  - Validate early and often: add lightweight checks (schema validation, lint/format/unit, plan/validate/execute loops) before/after risky steps; cache expensive results/tool metadata to disk with timestamps/keys.
  - Observability: when executing scripts/commands, capture append-only logs (e.g., progress.log/results.json) so the agent can observe execution flow for debugging/learning; keep logs tail-able and compact to protect tokens (summaries over full dumps).
  - Observability by default: keep `progress.log` and `results.json` with commands run, inputs used, outputs produced; include stderr/error summaries for debugging.
  - `results.json` conventions: one per project/task root (predictable path); append entries (don’t clobber) with `id`/`step`, timestamp, inputs (paths/params), outputs (paths, hashes, brief summary), status, notes/errors; read→merge→write; roll by date/task if large and keep a “current” pointer.
  - IDs and discoverability: use grep-friendly IDs (e.g., `task-foo-001`); include git context when present (branch, short SHA) and canonical artifact paths; reuse the same ID across plans/logs/results/commits/branches so `rg`/`git log -G` tie artifacts and code; note commands/scripts for reproducibility.
  - Guardrails in scripts: deterministic flags, explicit errors, timeouts/retries with backoff, input validation; fail fast on missing deps/permissions.
  - Reusability: factor common routines into scripts/templates; avoid writing into skill directories; normalize naming for assets/logs.
  - Trust/permissions: default ASK for writes/deletes; NEVER for creds/destruction; ALWAYS for read/inspect; prefer allowlists over bypassing prompts.
- Continuous improvement:
  - Proactively suggest edits to user-/project-scoped `AGENTS.md` when friction or gaps appear; ask before writing.
  - Suggest improvements to any `SKILL.md` and bundled resources; propose new scripts/templates/assets that reduce repetition or add validation, and keep them in project space (not skill directories).
  - Recommend devex helpers (CLI wrappers, lint/format hooks, setup docs) when they cut future toil; keep suggestions concise and contextual.
- Team and workflow practices:
  - Keep shared guidance alive: maintain team/project `AGENTS.md`/`CLAUDE.md`; add “do/don’t” notes after errors; align on model/settings in repo when appropriate.
  - Plan-first: propose/iterate on plans before auto-accept; keep plan files when useful for traceability.
  - Automate inner loops: add slash-command equivalents or helper scripts for repeated flows (commit/push/PR, lint/format/test) and keep them in-repo; surface them to the agent.
  - Subagents/hooks: suggest specialized sub-flows (simplify/verify) and post-action hooks (formatters, checkers) to harden outputs.
  - Permissions posture: maintain a shared allowlist of safe commands/settings to reduce prompt friction; prefer allowlists over blanket bypass.
  - Shared MCP/tool configs: check in permitted MCP settings/configs so agents can reach org tools (chat/search/analytics/logs) without rediscovery.
  - Where to put utilities: 
    - Repo scripts when they’re project-specific, touch code/assets, or need versioning alongside the codebase.
    - Repo skills when the project needs structured instructions plus scripts/templates for repeated behaviors unique to the repo.
    - General skills when the capability spans projects/users and benefits from shared discovery/versioning.
    - Slash commands for short, high-frequency chat-driven workflows that avoid re-prompting and don’t need to live in the codebase.
- Validation is the unlock:
  - Make success verifiable. Implement validators first when starting new work; keep them current as outputs change.
  - If validation approach is unclear, ask the user how they’d judge success and propose options.
  - Use whatever fits: tests (unit/smoke/fixtures), schema checks, diff/grep invariants, idempotence checks, round-trip or checksum comparisons, command exit codes, or MCP/tool-specific validators.
- Code-mode skill creation (apply when authoring/updating skills):
  - Progressive disclosure: keep `SKILL.md` lean (<500 lines), link to references/templates/scripts instead of inlining; keep references one level deep and point to them explicitly.
  - Files as memory: write large tool/MCP outputs and chat/terminal logs to files; read with `tail`/search instead of pasting blobs; cache MCP tool specs on disk.
  - Scripts over raw tool calls: route MCP via `mcpc --json` and filter (e.g., `jq`); prefer executing scripts with absolute paths over emitting tool calls in-context.
  - Degrees of freedom: split decide → configure → execute; match freedom to task fragility and avoid mixing levels in a single step.
  - Skill structure: gerund/hyphenated naming; frontmatter only `name` and `description` with clear “what” and “when to use”; keep bundles minimal (only resources that unlock execution).
  - Validation and safety: make scripts deterministic/idempotent with explicit errors; use plan/validate/execute loops for risky or batch ops; justify timeouts/constants.
  - Trust policy: Always for reads/listings; Ask for state-changing MCP calls/writes/deletes; Never for credential exfil or destructive/irreversible actions.
- Safety and fallback: If a skill can't be applied cleanly (missing files, unclear instructions), state the issue, pick the next-best approach, and continue.
</INSTRUCTIONS>


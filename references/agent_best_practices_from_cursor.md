Source: https://cursor.com/blog/agent-best-practices

# Best practices for coding with agents

> Jan 9, 2026 by Cursor Team in product

Coding agents are changing how software gets built. Models can now run for hours, complete ambitious multi-file refactors, and iterate until tests pass. But getting the most out of agents requires understanding how they work and developing new patterns.

This guide covers techniques for working with Cursor's agent. Whether you're new to agentic coding or looking to learn how our team uses Cursor, we'll cover the best practices for coding with agents.

## Understanding agent harnesses

An agent harness is built on three components:

* **Instructions:** The system prompt and rules that guide agent behavior
* **Tools:** File editing, codebase search, terminal execution, and more
* **User messages:** Your prompts and follow-ups that direct the work

Cursor's agent harness orchestrates these components for each model we support. We tune instructions and tools specifically for every frontier model based on internal evals and external benchmarks.

The harness matters because different models respond differently to the same prompts. A model trained heavily on shell-oriented workflows might prefer `grep` over a dedicated search tool. Another might need explicit instructions to call linter tools after edits. Cursor's agent handles this for you, so as new models are released, you can focus on building software.

## Start with plans

The most impactful change you can make is planning before coding.

A study from the University of Chicago found that experienced developers are more likely to plan before generating code. Planning forces clear thinking about what you're building and gives the agent concrete goals to work toward.

### Using Plan Mode

Press `Shift+Tab` in the agent input to toggle Plan Mode. Instead of immediately writing code, the agent will:

1. Research your codebase to find relevant files
2. Ask clarifying questions about your requirements
3. Create a detailed implementation plan with file paths and code references
4. Wait for your approval before building

Plans open as Markdown files you can edit directly to remove unnecessary steps, adjust the approach, or add context the agent missed.

**Tip:** Click "Save to workspace" to store plans in `.cursor/plans/`. This creates documentation for your team, makes it easy to resume interrupted work, and provides context for future agents working on the same feature.

Not every task needs a detailed plan. For quick changes or tasks you've done many times before, jumping straight to the agent is fine.

### Starting over from a plan

Sometimes the agent builds something that doesn't match what you wanted. Instead of trying to fix it through follow-up prompts, go back to the plan.

Revert the changes, refine the plan to be more specific about what you need, and run it again. This is often faster than fixing an in-progress agent, and produces cleaner results.

## Managing context

As you get more comfortable with agents writing code, your job becomes giving each agent the context it needs to complete its task.

### Let the agent find context

You don't need to manually tag every file in your prompt.

Cursor's agent has powerful search tools and pulls context on demand. When you ask about "the authentication flow," the agent finds relevant files through grep and semantic search, even if your prompt doesn't contain those exact words.

Keep it simple: if you know the exact file, tag it. If not, the agent will find it. Including irrelevant files can confuse the agent about what's important.

Cursor's agent also has helpful tools, like `@Branch`, which allow you to give the agent context about what you're working on. "Review the changes on this branch" or "What am I working on?" become natural ways to orient the agent to your current task.

### When to start a new conversation

One of the most common questions: should I continue this conversation or start fresh?

**Start a new conversation when:**

* You're moving to a different task or feature
* The agent seems confused or keeps making the same mistakes
* You've finished one logical unit of work

**Continue the conversation when:**

* You're iterating on the same feature
* The agent needs context from earlier in the discussion
* You're debugging something it just built

Long conversations can cause the agent to lose focus. After many turns and summarizations, the context accumulates noise and the agent can get distracted or switch to unrelated tasks. If you notice the effectiveness of the agent decreasing, it's time to start a new conversation.

### Reference past work

When you start a new conversation, use `@Past Chats` to reference previous work rather than copy-pasting the whole conversation. The agent can selectively read from the chat history to pull in only the context it needs.

This is more efficient than duplicating entire conversations.

## Extending the agent

Cursor provides two main ways to customize agent behavior: **Rules** for static context that applies to every conversation, and **Skills** for dynamic capabilities the agent can use when relevant.

### Rules: Static context for your project

Rules provide persistent instructions that shape how the agent works with your code. Think of them as always-on context that the agent sees at the start of every conversation.

Create rules as folders in `.cursor/rules/` containing a `RULE.md` file:

```markdown
# Commands
- `npm run build`: Build the project
- `npm run typecheck`: Run the typechecker
- `npm run test`: Run tests (prefer single test files for speed)

# Code style
- Use ES modules (import/export), not CommonJS (require)
- Destructure imports when possible: `import { foo } from 'bar'`
- See `components/Button.tsx` for canonical component structure

# Workflow
- Always typecheck after making a series of code changes
- API routes go in `app/api/` following existing patterns

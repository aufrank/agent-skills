# AI Agents: The case for Eval Driven Development

[!Note]
> from [https://sdarchitect.blog/2025/10/21/ai-agents-the-case-for-eval-driven-development](sdarchitect.blog).

Posted by Sanjeev Sharma on October 21, 2025
AI agents have become the prevailing core architectural component of AI-enabled systems. They allow us to build complex solutions that leverage Large Language Models (LLMs) alongside the myriad data sources, tools and other Agents organizations use to manage, transact with, and process data. Agents truly emerged as a leading element in AI systems with the release of the MCP protocol by Anthropic, which enabled AI agents to communicate not only with LLMs but also with data sources and the business logic used by existing systems to deliver services to end users. Other protocols like A2A then allowed Agents to interact easily with other Agents, within and outside the organization. Fundamentally, agents were easy for developers to adopt as a key architectural element because they were essentially software programs written in the language of the developer’s choice. These programs could be orchestrated using logic that is easily programmed, while also sending composable prompts to LLMs informed by both organizational data and existing business logic. MCP and similar protocols subsequently enabled AI agents to make ‘API-type’ calls to commercial tools, databases, data warehouses, custom applications, and other Agents – virtually everything operates behind an MCP server today.

This ease of agent development has broadened access for developers. Developers lacking AI or advanced data science expertise – those who cannot fine-tune models or practice advanced context engineering – can now bring their programming skills and knowledge of their organization’s data sources and tools to directly ‘program’ LLMs. Their familiar application delivery pipelines still apply, as do their standard software engineering methods. But do these traditional approaches truly work without significant changes to development practices and processes? Let’s examine the difference.

## Evals vs Tests

Are the ‘evals’ used to validate agentic systems anything more than tests? Software testing practices – unit tests, integration tests, system tests, user acceptance tests, etc – are mature methodologies decades in the making. So what’s new? The answer hinges on the nature of generative AI systems that use LLMs: they are stochastic and non-deterministic. In traditional (non-genAI) systems, functionality testing is only necessary when the system changes. Continuous testing for performance and availability reflects shifts in system load and usage, but absent code or configuration changes, there is little reason to repeatedly test for functionality. This process works because traditional systems are deterministic: the same inputs and system states yield the same results, reliably. (Notably, system state does impact outputs; however, for a given state and input, the result is deterministic.)

For LLM-based (genAI) systems, this is not the case. LLMs base outputs on prediction models and are inherently non-deterministic. Unless inputs and outputs are extremely simple, thousands of runs with the same data and state will likely produce no two identical outputs – a feature of genAI, not a bug. Consequently, the ‘test-once-until-next-change’ paradigm does not work. These systems must be tested continuously. For AI agent-based systems, these tests are called ‘evals.’ The objective of evals is to determine whether the system operates as intended. As with traditional testing, evals should be layered to allow continuous evaluation as systems become more complex and critical to operations.

> “I’ve often found evals to be a critical tool in the agent development process — they can be the difference between picking the right thing to work on vs. wasting weeks of effort.”
> Andrew Ng, Founder, deeplearning.ai

Evals fall into several broad categories. In addition to the standard evals for precision, accuracy, and recall – basic LLM behavior checks – evals for model drift and bias are fundamental for any system employing an LLM, whether or not agents are involved. Risk and compliance evals are also essential for large-scale systems, especially in commercial or public sector deployments where regulatory or internal policy requirements apply. Beyond compliance, evals addressing robustness, reliability, security, and human factors should be mapped to the specific deployment and user context. These topics will be explored in future posts, so stay tuned.

## Eval Driven Development (EDD)

Test Driven Development (TDD) is a well-established methodology in software engineering. For those unfamiliar, TDD requires developers to write automated tests before crafting the code to satisfy those tests. The cycle follows “Red-Green-Refactor”: write a failing test (red); write just enough code to pass the test (green); then refine the code while ensuring all tests continue to pass (refactor). This iterative approach keeps code modular, reduces bugs, and helps maintain clean, well-tested software. It delivers fast feedback, supports better design decisions, and makes maintenance easier because every feature is linked to specific, testable requirements.

Similarly, we need Eval Driven Development (EDD) for AI agentic systems. Start by writing automated evals for your agents before authoring agent code or structuring prompts for model context. Importantly, evals must be run continuously, and when an eval fails, it must be traceable through all layers of the agentic system to diagnose the root cause. A test failure does not necessarily indicate a bug – it could arise from data pipelines, queries, ETL issues, misconfigured settings, or even errors from external APIs or endpoints. The same applies to agentic systems, but with continuous, real-time operation, an extensive observability stack is essential at each layer. Across this stack, what might cause an agent to deliver an incorrect (or unacceptable) output? Is the fault in the agent, a tool or data source accessed via MCP, or another Agent, an LLM hallucination or drift, a data pipeline error, a poorly crafted prompt, incomplete or inaccurate context, a security event (like prompt injection or model poisoning), model bias, or just user error?

> “The strongest predictor of how quickly teams advance AI agents is a disciplined process for evals and error analysis rather than ad hoc fixes or chasing buzzy tools.”
> Andrew Ng, Founder, deeplearning.ai

Beginning with evals – just as TDD begins with tests – helps anticipate failure modes and develop mitigation plans for those that matter most. Like TDD tests, evals should be updated each time any system component changes, and ideally, they should be revised before any updates are implemented. Eval first. Eval driven.

Evals also serve a secondary function: compliance, especially for systems subject to regulatory oversight. Evals provide transparency. In the event of an audit or disclosure requirement, evals demonstrate how the system behaves and document the approach to handling edge cases, security, compliance, bias, drift, and more. This transparency becomes essential as increasingly critical, human-impacting decisions are delegated to AI agents.

> “If people don’t trust your evals, they won’t trust you.”
> Hamel Husain, ML Engineer and Eval expert

## Final Thoughts

In summary, if you are building AI agents – even if they are currently simple prototypes or used internally – begin with Eval Driven Development (EDD). As your systems mature, grow in complexity, and produce results that must be reliably kept within acceptable bounds, EDD gives you the framework to ensure your agents perform as desired, continuously.

In future posts, I will present the leading frameworks used for developing evals. In my next post, I’ll introduce the recently released NIST AI Risk Management Framework and explain why it’s a solid foundation for starting your EDD journey. I’m also working on domain-specific eval frameworks for financial services based on FFIEC guidance, and for insurance based on state directives for AI in insurance systems. Feel free to reach out for details – posts on these topics will follow soon. Watch this space.

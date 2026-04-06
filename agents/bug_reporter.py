from core.ai_factory import AIFactory
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger


class BugReporter:
    def __init__(self, shared_memory: list = None):
        self.llm = AIFactory.get_model()
        self.memory = shared_memory if shared_memory is not None else []

        # LangChain Expression Language (LCEL) — pipe syntax chains the
        # prompt template directly into the model. This is the modern
        # LangChain pattern: structured prompt management + model in one chain.
        self.prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a Senior QA Lead writing professional Jira-ready bug reports. "
                "You analyse failure patterns across a test run and identify recurring issues. "
                "Always follow the exact template provided. Be specific about selectors and actions."
            ),
            (
                "human",
                "{pattern_context}\n\n"
                "A test case just failed. Use this EXACT template:\n\n"
                "--- TEMPLATE START ---\n"
                "SUMMARY: [UI_FAILURE] - {title}\n"
                "ENVIRONMENT: OrangeHRM-Pilot\n"
                "SEVERITY: High\n\n"
                "REPRODUCE STEPS:\n"
                "{steps_text}\n\n"
                "ACTUAL RESULT:\n"
                "{error_message}\n\n"
                "EXPECTED RESULT:\n"
                "The step '{last_action}' should succeed without errors.\n\n"
                "PATTERN ANALYSIS:\n"
                "Based on the failure history above, state if this looks like a recurring "
                "selector issue or an isolated failure. Be specific about which selector.\n"
                "--- TEMPLATE END ---\n\n"
                "SCREENSHOT FILENAME: {screenshot_path}"
            )
        ])

        # The LCEL chain: prompt → model (| is the LangChain pipe operator)
        self.chain = self.prompt_template | self.llm

    def draft_bug_report(self, test_case, error_message, screenshot_path):
        title = test_case.get('title', 'Unknown Test')
        steps = test_case.get('steps', [])

        # Format steps for the prompt
        steps_list = []
        for s in steps:
            action = s.get('action', '')
            selector = f"[{s.get('selector')}]" if s.get('selector') else ""
            data = f"-> '{s.get('data')}'" if s.get('data') else ""
            steps_list.append(f"- {action} {selector} {data}")
        steps_text = "\n".join(steps_list)

        last_action = steps[-1].get('action', 'unknown') if steps else 'unknown'

        # Extract failing selector for memory
        failing_selector = next(
            (s.get('selector') for s in reversed(steps) if s.get('selector')), "unknown"
        )

        # Build pattern context from accumulated failures this run
        if self.memory:
            pattern_lines = "\n".join(
                [f"  - [{f['title']}] selector='{f['selector']}' error={f['error'][:80]}"
                 for f in self.memory]
            )
            pattern_context = (
                "PATTERN CONTEXT (previous failures this run — use to detect recurring issues):\n"
                + pattern_lines
            )
        else:
            pattern_context = "PATTERN CONTEXT: This is the first failure in this run."

        logger.info(f"🤖 AI chain invoking for: {title}")
        try:
            # Invoke the LCEL chain with named variables — LangChain injects
            # these into the ChatPromptTemplate slots defined above
            response = self.chain.invoke({
                "pattern_context": pattern_context,
                "title": title,
                "steps_text": steps_text,
                "error_message": str(error_message),
                "last_action": last_action,
                "screenshot_path": screenshot_path
            })

            content = response.content if hasattr(response, 'content') else str(response)

            # Record into shared memory for pattern detection
            self.memory.append({
                "title": title,
                "selector": failing_selector,
                "error": str(error_message)
            })
            logger.info(f"📝 Failure logged to shared memory ({len(self.memory)} total this run)")

            return content

        except Exception as e:
            logger.error(f"AI chain failed to generate report: {e}")
            self.memory.append({
                "title": title,
                "selector": failing_selector,
                "error": str(error_message)
            })
            return f"Error generating bug report: {str(e)}"

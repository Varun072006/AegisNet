"""AI Workflow Engine — orchestrates multi-stage model pipelines."""

from typing import List, Dict, Any, Optional
from gateway import process_chat
from sqlalchemy.ext.asyncio import AsyncSession

class WorkflowEngine:
    """Executes sequences of AI tasks with state passing."""

    async def execute_workflow(
        self,
        steps: List[Dict[str, Any]],
        initial_input: str,
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Executes a list of steps. Each step can use results from previous steps.
        Format: [{'id': 'step1', 'task': 'research', 'model': '...', 'prompt_template': '...'}]
        """
        context = {"initial_input": initial_input}
        results = []

        for step in steps:
            step_id = step.get("id")
            processor_model = step.get("model")
            prompt_template = step.get("prompt_template", "{input}")
            
            # Interpolate context into prompt
            # e.g., "Summarize this: {step1_output}"
            try:
                formatted_prompt = prompt_template.format(input=initial_input, **context)
            except KeyError as e:
                raise ValueError(f"Workflow Error: Missing context key {e} in step {step_id}")

            # Execute via standard gateway (reusing security, routing, and logs)
            response = await process_chat(
                messages=[{"role": "user", "content": formatted_prompt}],
                model_preference=processor_model,
                routing_strategy="auto",
                user_id=user_id,
                max_tokens=step.get("max_tokens", 1024),
                temperature=step.get("temperature", 0.7),
                db=db
            )

            output_text = response["content"]
            context[f"{step_id}_output"] = output_text
            results.append({
                "step_id": step_id,
                "model": response["metadata"]["model"],
                "content": output_text
            })

        return {
            "workflow_id": "wf_" + str(int(1000)), # Placeholder ID
            "final_output": results[-1]["content"] if results else "",
            "steps": results
        }

# Global instance
workflow_engine = WorkflowEngine()

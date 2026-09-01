from __future__ import annotations

from core.command_router import CommandRouter
from core.logger import get_logger
from core.task_manager import TaskManager
from ai.brain import Brain, BrainError


class Assistant:
    def __init__(self) -> None:
        self.router = CommandRouter()
        self.tasks = TaskManager()
        self.brain = Brain()
        self.logger = get_logger("assistant")

    def handle(self, command: str) -> str:
        self.logger.info("command=%r", command)
        def act() -> str:
            local_result = self.router.execute(command)
            if not local_result.startswith("I don't support that command yet."):
                return local_result
            plan = self.brain.plan(command)
            return self.router.execute_intent(plan) if plan else local_result

        task = self.tasks.submit(act)
        completed = self.tasks.run_next()
        if not completed or completed.id != task.id:
            return "Task queue error."
        if completed.error:
            self.logger.error("task=%s error=%s", task.id, completed.error)
            return f"I couldn't complete that: {completed.error}"
        self.logger.info("task=%s completed", task.id)
        return str(completed.result)

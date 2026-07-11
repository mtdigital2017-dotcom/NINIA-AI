from __future__ import annotations
from pathlib import Path
from typing import Any
from .memory_curator import MemoryCurator
from .context_builder import ContextBuilder
from .dt_guardian import DTGuardian
from .qa_architect import QAArchitect
from .learning_advisor import LearningAdvisor

class DTRuntimeOrchestrator:
    """Coordina los agentes internos de memoria, contexto, prevención y QA."""

    def __init__(self, root: Path):
        self.root = root
        self.curator = MemoryCurator(root)
        self.builder = ContextBuilder()
        self.guardian = DTGuardian()
        self.qa = QAArchitect()
        self.learning = LearningAdvisor()

    def refresh(self) -> dict[str, Any]:
        memory = self.curator.load()
        context = self.builder.build(memory)
        qa = self.qa.validate(self.root, context)
        context["qa"] = qa
        self.curator.write_context(context)
        return context

    def review(self, proposal: str, requires_manual_action: bool = False) -> dict[str, Any]:
        context = self.refresh()
        return {
            "context": context,
            "guardian": self.guardian.review_proposal(proposal, context),
            "guidance": self.learning.guidance(context, requires_manual_action),
        }

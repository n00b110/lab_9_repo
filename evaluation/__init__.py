"""Evaluation package for model assessment and quality metrics."""

from evaluation.evaluate import (
    TEST_QUESTIONS,
    ModelEvaluator,
    generate_markdown_report,
    run_evaluation,
    save_evaluation_report,
)

__all__ = [
    "run_evaluation",
    "save_evaluation_report",
    "generate_markdown_report",
    "ModelEvaluator",
    "TEST_QUESTIONS",
]

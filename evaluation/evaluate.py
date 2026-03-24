"""Enhanced evaluation script for the Domain Adapted AI Assistant."""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/evaluation.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# Configuration
API_URL = "http://localhost:8000"
EVALUATION_OUTPUT_DIR = Path("evaluation_results")
EVALUATION_OUTPUT_DIR.mkdir(exist_ok=True)

# Test questions for evaluation
TEST_QUESTIONS = [
    "What is deadlock in operating systems?",
    "Explain semaphores and their use in synchronization",
    "What is a mutex and how does it differ from a semaphore?",
    "Describe the process scheduling algorithm",
    "What is virtual memory and why is it important?",
    "Explain the difference between preemptive and non-preemptive scheduling",
    "What are the main components of a process control block?",
    "Describe the page replacement algorithms",
    "What is context switching and when does it occur?",
    "Explain the concept of race conditions",
]


def check_api_health() -> bool:
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"API health check failed: {str(e)}")
        return False


def ask_question(question: str) -> Dict[str, Any]:
    """Ask a question to the API."""
    try:
        payload = {
            "question": question,
            "max_length": 500,
            "use_cache": False,
        }

        response = requests.post(
            f"{API_URL}/ask",
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": True,
                "message": f"API Error: {response.status_code}",
            }

    except requests.exceptions.Timeout:
        return {
            "error": True,
            "message": "Request timed out",
        }
    except Exception as e:
        return {
            "error": True,
            "message": str(e),
        }


def evaluate_model_quality(response: str) -> Dict[str, float]:
    """
    Evaluate the quality of a response.

    This is a simple heuristic-based evaluation.
    In a real scenario, you might use more sophisticated metrics.
    """
    quality_metrics = {
        "length_score": 0.0,
        "structure_score": 0.0,
        "technical_score": 0.0,
    }

    # Length score (longer responses tend to be more informative)
    length = len(response)
    quality_metrics["length_score"] = min(length / 300, 1.0)

    # Structure score (check for paragraphs and sentences)
    sentences = response.count(".") + response.count("?") + response.count("!")
    quality_metrics["structure_score"] = min(sentences / 5, 1.0)

    # Technical score (check for technical terms)
    technical_terms = [
        "algorithm",
        "process",
        "memory",
        "synchronization",
        "concurrent",
        "scheduler",
        "lock",
        "thread",
        "interrupt",
        "resource",
    ]
    technical_count = sum(
        1 for term in technical_terms if term.lower() in response.lower()
    )
    quality_metrics["technical_score"] = min(technical_count / 3, 1.0)

    # Overall score
    overall_score = (
        quality_metrics["length_score"]
        + quality_metrics["structure_score"]
        + quality_metrics["technical_score"]
    ) / 3

    quality_metrics["overall_score"] = overall_score

    return quality_metrics


def run_evaluation() -> Dict[str, Any]:
    """Run comprehensive evaluation."""
    logger.info("=" * 60)
    logger.info("Starting Model Evaluation")
    logger.info("=" * 60)

    # Check API health
    logger.info("Checking API health...")
    if not check_api_health():
        logger.error("API is not running. Please start the API first.")
        logger.error("Run: python -m uvicorn app.api:app --reload")
        return {"error": True, "message": "API not available"}

    logger.info("✅ API is running and healthy")

    # Evaluation results
    evaluation_results = {
        "evaluation_time": datetime.now().isoformat(),
        "api_url": API_URL,
        "total_questions": len(TEST_QUESTIONS),
        "questions_evaluated": 0,
        "successful_responses": 0,
        "failed_responses": 0,
        "average_inference_time": 0.0,
        "average_quality_score": 0.0,
        "detailed_results": [],
        "metrics": {},
    }

    logger.info(f"Evaluating {len(TEST_QUESTIONS)} test questions...")
    logger.info("-" * 60)

    inference_times = []
    quality_scores = []

    for i, question in enumerate(TEST_QUESTIONS, 1):
        logger.info(f"\n[{i}/{len(TEST_QUESTIONS)}] Question: {question[:50]}...")

        # Ask question
        start_time = time.time()
        result = ask_question(question)
        inference_time = time.time() - start_time

        if "error" in result and result.get("error"):
            logger.warning(f"  ❌ Failed: {result.get('message')}")
            evaluation_results["failed_responses"] += 1

            evaluation_results["detailed_results"].append(
                {
                    "question": question,
                    "status": "failed",
                    "error": result.get("message"),
                    "inference_time": inference_time,
                }
            )
        else:
            logger.info(f"  ✅ Success")
            logger.debug(f"  Inference time: {inference_time:.3f}s")

            response_text = result.get("response", "")

            # Evaluate quality
            quality_metrics = evaluate_model_quality(response_text)
            quality_score = quality_metrics.get("overall_score", 0.0)

            logger.info(f"  Quality score: {quality_score:.3f}")
            logger.debug(f"  Response preview: {response_text[:100]}...")

            evaluation_results["successful_responses"] += 1
            inference_times.append(inference_time)
            quality_scores.append(quality_score)

            evaluation_results["detailed_results"].append(
                {
                    "question": question,
                    "status": "success",
                    "response": response_text[:200],  # Store preview only
                    "inference_time": inference_time,
                    "from_cache": result.get("from_cache", False),
                    "tokens_generated": result.get("tokens_generated", 0),
                    "quality_metrics": quality_metrics,
                }
            )

        evaluation_results["questions_evaluated"] += 1

    logger.info("\n" + "=" * 60)
    logger.info("Evaluation Summary")
    logger.info("=" * 60)

    # Calculate averages
    if inference_times:
        evaluation_results["average_inference_time"] = sum(inference_times) / len(
            inference_times
        )

    if quality_scores:
        evaluation_results["average_quality_score"] = sum(quality_scores) / len(
            quality_scores
        )

    # Log summary
    logger.info(f"Total questions: {evaluation_results['total_questions']}")
    logger.info(f"Successful responses: {evaluation_results['successful_responses']}")
    logger.info(f"Failed responses: {evaluation_results['failed_responses']}")
    logger.info(
        f"Success rate: {evaluation_results['successful_responses'] / evaluation_results['questions_evaluated'] * 100:.1f}%"
    )
    logger.info(
        f"Average inference time: {evaluation_results['average_inference_time']:.3f}s"
    )
    logger.info(
        f"Average quality score: {evaluation_results['average_quality_score']:.3f}/1.0"
    )

    # Get API metrics
    logger.info("\nFetching API metrics...")
    try:
        response = requests.get(f"{API_URL}/metrics", timeout=5)
        if response.status_code == 200:
            evaluation_results["metrics"] = response.json()
            logger.info("✅ API metrics retrieved")
    except Exception as e:
        logger.warning(f"Failed to get API metrics: {str(e)}")

    logger.info("=" * 60)

    return evaluation_results


def save_evaluation_report(results: Dict[str, Any]) -> str:
    """Save evaluation report to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = EVALUATION_OUTPUT_DIR / f"evaluation_report_{timestamp}.json"

    try:
        with open(report_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"✅ Evaluation report saved to: {report_file}")
        return str(report_file)

    except Exception as e:
        logger.error(f"Failed to save report: {str(e)}")
        return ""


def generate_markdown_report(results: Dict[str, Any]) -> str:
    """Generate a markdown report of the evaluation."""
    report = "# Model Evaluation Report\n\n"
    report += f"**Evaluation Time:** {results.get('evaluation_time')}\n\n"

    report += "## Summary\n\n"
    report += f"- Total Questions: {results.get('total_questions')}\n"
    report += f"- Successful Responses: {results.get('successful_responses')}\n"
    report += f"- Failed Responses: {results.get('failed_responses')}\n"

    success_rate = (
        results.get("successful_responses", 0)
        / results.get("questions_evaluated", 1)
        * 100
    )
    report += f"- Success Rate: {success_rate:.1f}%\n\n"

    report += "## Performance Metrics\n\n"
    report += (
        f"- Average Inference Time: {results.get('average_inference_time', 0):.3f}s\n"
    )
    report += f"- Average Quality Score: {results.get('average_quality_score', 0):.3f}/1.0\n\n"

    report += "## Detailed Results\n\n"

    for i, result in enumerate(results.get("detailed_results", []), 1):
        report += f"### Question {i}\n\n"
        report += f"**Q:** {result.get('question')}\n\n"

        if result.get("status") == "success":
            report += "**Status:** ✅ Success\n\n"
            report += f"**Response Preview:** {result.get('response', 'N/A')}\n\n"
            report += f"**Inference Time:** {result.get('inference_time', 0):.3f}s\n\n"

            quality = result.get("quality_metrics", {})
            if quality:
                report += "**Quality Metrics:**\n\n"
                report += f"- Overall Score: {quality.get('overall_score', 0):.3f}\n"
                report += f"- Length Score: {quality.get('length_score', 0):.3f}\n"
                report += (
                    f"- Structure Score: {quality.get('structure_score', 0):.3f}\n"
                )
                report += (
                    f"- Technical Score: {quality.get('technical_score', 0):.3f}\n\n"
                )
        else:
            report += "**Status:** ❌ Failed\n\n"
            report += f"**Error:** {result.get('error', 'Unknown error')}\n\n"

    if results.get("metrics"):
        report += "## API Metrics\n\n"
        metrics = results.get("metrics", {})
        report += f"- Total Requests: {metrics.get('total_requests', 0)}\n"
        report += f"- Error Rate: {metrics.get('error_rate', 'N/A')}\n"
        report += f"- Average Inference Time: {metrics.get('average_inference_time', 0):.3f}s\n"

    return report


def main():
    """Main evaluation function."""
    logger.info("Domain Adapted AI Assistant - Evaluation Script")
    logger.info(f"Testing API at: {API_URL}")

    # Run evaluation
    results = run_evaluation()

    if results.get("error"):
        logger.error("Evaluation failed")
        return

    # Save report
    report_file = save_evaluation_report(results)

    # Generate markdown report
    markdown_report = generate_markdown_report(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_file = EVALUATION_OUTPUT_DIR / f"evaluation_report_{timestamp}.md"

    try:
        with open(md_file, "w") as f:
            f.write(markdown_report)
        logger.info(f"✅ Markdown report saved to: {md_file}")
    except Exception as e:
        logger.error(f"Failed to save markdown report: {str(e)}")

    logger.info("\n✅ Evaluation complete!")
    logger.info(f"Results saved to: {EVALUATION_OUTPUT_DIR}")


if __name__ == "__main__":
    main()

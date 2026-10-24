import pytest
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from brown.workflows.generate_article import invoke_media_job


class DiagramArgs(BaseModel):
    description_of_the_diagram: str


async def draw(description_of_the_diagram: str) -> str:
    """Draw a diagram."""
    return f"diagram: {description_of_the_diagram}"


TOOL = StructuredTool.from_function(coroutine=draw, name="mermaid_diagram_generator_tool", args_schema=DiagramArgs)


@pytest.mark.asyncio
async def test_a_malformed_media_job_is_skipped_instead_of_failing_the_article() -> None:
    # Seen live: the orchestrator called the tool with {"description": "No diagram needed", ...}.
    result = await invoke_media_job(TOOL, {"description": "No diagram needed", "diagram_title": "placeholder"})

    assert result is None


@pytest.mark.asyncio
async def test_a_valid_media_job_returns_the_tool_output() -> None:
    result = await invoke_media_job(TOOL, {"description_of_the_diagram": "pipeline"})

    assert result == "diagram: pipeline"

import pytest

from brown.entities.research import Research
from brown.nodes.article_reviewer import ArticleReviewer, ReviewsOutput


class SpyModel:
    """Captures the prompt the reviewer sends and returns no reviews."""

    def __init__(self) -> None:
        self.prompt = ""

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, inputs, *args, **kwargs) -> ReviewsOutput:
        self.prompt = "".join(part["text"] for message in inputs for part in message["content"] if part.get("type") == "text")
        return ReviewsOutput(reviews=[])


def build_reviewer(spy: SpyModel, research, article, guideline, profiles) -> ArticleReviewer:
    reviewer = ArticleReviewer(to_review=article, article_guideline=guideline, model=spy, article_profiles=profiles, research=research)
    reviewer.model = spy
    return reviewer


@pytest.mark.asyncio
async def test_reviewer_sees_the_research_so_it_can_flag_unsourced_claims(
    mock_article_simple, mock_article_guideline_simple, mock_article_profiles_simple
) -> None:
    spy = SpyModel()
    research = Research(content="DuckDB reads Wyscout parquet files natively.")

    await build_reviewer(spy, research, mock_article_simple, mock_article_guideline_simple, mock_article_profiles_simple).ainvoke()

    assert "DuckDB reads Wyscout parquet files natively." in spy.prompt
    assert "[EXPERIENCE:" in spy.prompt  # the reviewer is told to keep the markers


@pytest.mark.asyncio
async def test_reviewer_still_works_without_research(
    mock_article_simple, mock_article_guideline_simple, mock_article_profiles_simple
) -> None:
    spy = SpyModel()

    reviews = await build_reviewer(spy, None, mock_article_simple, mock_article_guideline_simple, mock_article_profiles_simple).ainvoke()

    assert reviews.reviews == []

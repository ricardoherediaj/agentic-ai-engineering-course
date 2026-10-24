import pytest
from langchain_core.messages import AIMessage

from brown.entities.exceptions import EmptyModelOutputException
from brown.nodes.article_writer import ArticleWriter


class StubModel:
    """Returns a fixed AIMessage, like a provider that filtered or truncated the answer."""

    def __init__(self, message: AIMessage) -> None:
        self.message = message

    async def ainvoke(self, *args, **kwargs) -> AIMessage:
        return self.message


def build_writer(message: AIMessage, guideline, research, profiles, media_items, examples) -> ArticleWriter:
    writer = ArticleWriter(
        article_guideline=guideline,
        research=research,
        article_profiles=profiles,
        media_items=media_items,
        article_examples=examples,
        model=StubModel(message),
    )
    writer.model = StubModel(message)
    return writer


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message",
    [
        AIMessage(content="", response_metadata={"finish_reason": "content_filter"}),
        AIMessage(content="   \n", response_metadata={"finish_reason": "stop"}),
    ],
    ids=["content_filter", "blank"],
)
async def test_writer_raises_instead_of_returning_an_empty_article(
    message,
    mock_article_guideline_simple,
    mock_research_simple,
    mock_article_profiles_simple,
    mock_media_items,
    mock_article_examples_simple,
) -> None:
    writer = build_writer(
        message,
        mock_article_guideline_simple,
        mock_research_simple,
        mock_article_profiles_simple,
        mock_media_items,
        mock_article_examples_simple,
    )

    with pytest.raises(EmptyModelOutputException) as error:
        await writer.ainvoke()

    assert str(message.response_metadata["finish_reason"]) in str(error.value)


@pytest.mark.asyncio
async def test_writer_returns_the_article_when_the_model_writes_text(
    mock_article_guideline_simple,
    mock_research_simple,
    mock_article_profiles_simple,
    mock_media_items,
    mock_article_examples_simple,
) -> None:
    writer = build_writer(
        AIMessage(content="# Title\n\nBody.", response_metadata={"finish_reason": "stop"}),
        mock_article_guideline_simple,
        mock_research_simple,
        mock_article_profiles_simple,
        mock_media_items,
        mock_article_examples_simple,
    )

    article = await writer.ainvoke()

    assert article.content == "# Title\n\nBody."

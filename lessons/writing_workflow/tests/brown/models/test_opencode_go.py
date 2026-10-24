"""Tests for the OpenCode Go fallback provider in get_model."""

from pathlib import Path
from unittest.mock import patch

import pytest
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from brown.config import Settings
from brown.config_app import AppConfig
from brown.models.config import SupportedModels
from brown.models.get_model import get_model

CONFIGS_DIR = Path(__file__).parents[3] / "configs"


def make_settings(**overrides) -> Settings:
    with patch.dict("os.environ", {"CONFIG_FILE": "configs/debug.yaml"}, clear=True):
        return Settings(_env_file=None, **overrides)


@pytest.mark.parametrize(
    ("model", "model_id", "responses"),
    [
        (SupportedModels.OPENCODE_GO_GPT_6_LUNA, "gpt-6-luna", True),
        (SupportedModels.OPENCODE_GO_DEEPSEEK_V4_FLASH, "deepseek-v4-flash", False),
        (SupportedModels.OPENCODE_GO_DEEPSEEK_V41_FLASH, "deepseek-v4.1-flash", False),
        (SupportedModels.OPENCODE_GO_GLM_53, "glm-5.3", False),
    ],
)
def test_opencode_model_builds_offline(model, model_id, responses) -> None:
    settings = make_settings(OPENCODE_API_KEY="injected-test-key")
    with patch("brown.models.get_model.get_settings", return_value=settings):
        llm = get_model(model)

    assert isinstance(llm, ChatOpenAI)
    assert llm.model_name == model_id
    assert llm.openai_api_base == "https://opencode.ai/zen/go/v1"
    assert llm.default_headers["User-Agent"] == "underdoc-evals/0.1"
    # Go rejects requests without a stable per-run session header.
    assert llm.default_headers["x-opencode-session"]
    with patch("brown.models.get_model.get_settings", return_value=settings):
        assert get_model(model).default_headers["x-opencode-session"] == llm.default_headers["x-opencode-session"]
    assert bool(llm.use_responses_api) is responses
    assert llm.openai_api_key.get_secret_value() == "injected-test-key"


def test_deepseek_defaults_to_temperature_zero_and_ignores_gemini_keys() -> None:
    from brown.models.config import ModelConfig

    settings = make_settings(OPENCODE_API_KEY="k")
    config = ModelConfig(temperature=0.0, thinking_level="high", max_retries=2)
    with patch("brown.models.get_model.get_settings", return_value=settings):
        llm = get_model(SupportedModels.OPENCODE_GO_DEEPSEEK_V4_FLASH, config)
    assert llm.temperature == 0.0
    assert llm.max_retries == 2


@pytest.mark.parametrize("model", [SupportedModels.OPENCODE_GO_GPT_6_LUNA, SupportedModels.OPENCODE_GO_DEEPSEEK_V41_FLASH])
def test_opencode_model_without_key_raises(model) -> None:
    settings = make_settings()
    with patch("brown.models.get_model.get_settings", return_value=settings):
        with pytest.raises(ValueError, match="OPENCODE_API_KEY"):
            get_model(model)


def test_opencode_key_is_optional_for_settings() -> None:
    assert make_settings().OPENCODE_API_KEY is None


def test_google_path_unchanged() -> None:
    settings = make_settings(GOOGLE_API_KEY="g")
    with (
        patch("brown.models.get_model.get_settings", return_value=settings),
        patch("brown.models.get_model.init_chat_model") as init_mock,
    ):
        get_model(SupportedModels.GOOGLE_GEMINI_37_FLASH)
    kwargs = init_mock.call_args.kwargs
    assert kwargs["model"] == "google_genai:gemini-3.7-flash"
    assert kwargs["api_key"] == "g"
    assert kwargs["thinking_level"] == "low"
    assert "base_url" not in kwargs


@pytest.mark.parametrize(
    ("name", "writer"),
    [
        ("course-fallback.yaml", "opencode_go:deepseek-v4.1-flash"),
        # v4.1-flash returns `content_filter` on the full Underdoc writer prompt, so Underdoc writes with v4-pro.
        ("underdoc-fallback.yaml", "opencode_go:deepseek-v4-pro"),
    ],
)
def test_fallback_configs_parse(name, writer) -> None:
    app_config = AppConfig.from_yaml(CONFIGS_DIR / name)
    dumped = app_config.model_dump(mode="json")
    model_ids = {k: v["model_id"] for k, v in dumped["nodes"].items()}
    assert model_ids["review_article"] == "opencode_go:gpt-6-luna"
    assert model_ids["review_selected_text"] == "opencode_go:gpt-6-luna"
    assert model_ids["write_article"] == writer
    assert all(v.startswith("opencode_go:") for v in model_ids.values())


class Pong(BaseModel):
    answer: str


class DiagramShape(BaseModel):
    """Mirrors `GeneratedMermaidDiagram`."""

    content: str
    caption: str


def _build(model):
    settings = make_settings(OPENCODE_API_KEY="injected-test-key")
    with patch("brown.models.get_model.get_settings", return_value=settings):
        return get_model(model)


def test_deepseek_structured_output_defaults_to_function_calling() -> None:
    from brown.models.get_model import FunctionCallingChatOpenAI

    llm = _build(SupportedModels.OPENCODE_GO_DEEPSEEK_V41_FLASH)
    assert isinstance(llm, FunctionCallingChatOpenAI)
    with patch.object(ChatOpenAI, "with_structured_output", return_value="x") as parent:
        llm.with_structured_output(Pong)
        assert parent.call_args.kwargs["method"] == "function_calling"
        llm.with_structured_output(Pong, method="json_mode")
        assert parent.call_args.kwargs["method"] == "json_mode"


def test_gpt_luna_is_plain_chat_openai() -> None:
    from brown.models.get_model import FunctionCallingChatOpenAI

    llm = _build(SupportedModels.OPENCODE_GO_GPT_6_LUNA)
    assert type(llm) is ChatOpenAI
    assert not isinstance(llm, FunctionCallingChatOpenAI)


@pytest.mark.parametrize("model", [SupportedModels.OPENCODE_GO_GPT_6_LUNA, SupportedModels.OPENCODE_GO_DEEPSEEK_V41_FLASH])
def test_opencode_live_smoke(model) -> None:
    """One tiny structured-output call per model. Skipped without OPENCODE_API_KEY in settings."""
    from brown.config import get_settings

    if not get_settings().OPENCODE_API_KEY:
        pytest.skip("OPENCODE_API_KEY not available in settings")
    llm = get_model(model).with_structured_output(Pong)
    result = llm.invoke("Reply with the single word: pong")
    assert isinstance(result, Pong)
    assert result.answer


def test_deepseek_live_smoke_diagram_shape() -> None:
    """Structured output shaped like `GeneratedMermaidDiagram` must work on DeepSeek (no json_schema)."""
    from brown.config import get_settings

    if not get_settings().OPENCODE_API_KEY:
        pytest.skip("OPENCODE_API_KEY not available in settings")
    llm = get_model(SupportedModels.OPENCODE_GO_DEEPSEEK_V41_FLASH).with_structured_output(DiagramShape, include_raw=False)
    result = llm.invoke("Generate a tiny mermaid flowchart A to B. content is the fenced mermaid block, caption a short description.")
    assert isinstance(result, DiagramShape)
    assert result.content and result.caption

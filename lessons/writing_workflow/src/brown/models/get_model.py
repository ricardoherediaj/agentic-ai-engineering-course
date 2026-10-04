import json

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from brown.config import get_settings

from .config import (
    DEFAULT_MODEL_CONFIGS,
    ModelConfig,
    SupportedModels,
)
from .fake_model import FakeModel

MODEL_TO_REQUIRED_API_KEY = {
    SupportedModels.GOOGLE_GEMINI_37_FLASH: "GOOGLE_API_KEY",
    SupportedModels.GOOGLE_GEMINI_31_FLASH_LITE: "GOOGLE_API_KEY",
    SupportedModels.GOOGLE_GEMINI_31_PRO_PREVIEW: "GOOGLE_API_KEY",
    SupportedModels.GOOGLE_GEMINI_25_PRO: "GOOGLE_API_KEY",
}


OPENCODE_GO_PREFIX = "opencode_go:"
OPENCODE_GO_BASE_URL = "https://opencode.ai/zen/go/v1"
# Go's terms ask clients to identify with their own user agent (never impersonate OpenCode).
OPENCODE_GO_USER_AGENT = "underdoc-evals/0.1"
# Models served by the OpenAI Responses endpoint; the rest use chat completions.
OPENCODE_GO_RESPONSES_MODELS = {SupportedModels.OPENCODE_GO_GPT_6_LUNA}
# Gemini-only ModelConfig fields that ChatOpenAI would reject.
_GEMINI_ONLY_KEYS = ("thinking_budget", "thinking_level", "response_modalities")


def _get_opencode_go_model(model: SupportedModels, config: ModelConfig) -> BaseChatModel:
    from langchain_openai import ChatOpenAI

    api_key = get_settings().OPENCODE_API_KEY
    if not api_key:
        raise ValueError("Required environment variable `OPENCODE_API_KEY` is not set (needed for `opencode_go:` models)")

    use_responses_api = model in OPENCODE_GO_RESPONSES_MODELS
    kwargs = {k: v for k, v in config.model_dump().items() if k not in _GEMINI_ONLY_KEYS}
    if "max_output_tokens" in kwargs:
        kwargs["max_tokens"] = kwargs.pop("max_output_tokens")
    if use_responses_api:
        # Reasoning models on the Responses API may reject sampling parameters.
        kwargs.pop("temperature", None)

    return ChatOpenAI(
        model=model.value.removeprefix(OPENCODE_GO_PREFIX),
        base_url=OPENCODE_GO_BASE_URL,
        api_key=api_key,
        default_headers={"User-Agent": OPENCODE_GO_USER_AGENT},
        use_responses_api=use_responses_api,
        **kwargs,
    )


def get_model(model: SupportedModels, config: ModelConfig | None = None) -> BaseChatModel:
    if model == SupportedModels.FAKE_MODEL:
        if config and config.mocked_response is not None:
            if hasattr(config.mocked_response, "model_dump"):
                mocked_response_json = config.mocked_response.model_dump(mode="json")
            else:
                mocked_response_json = json.dumps(config.mocked_response)
            return FakeModel(responses=[mocked_response_json])
        else:
            return FakeModel(responses=[])

    config = config or DEFAULT_MODEL_CONFIGS.get(model) or ModelConfig()
    if model.value.startswith(OPENCODE_GO_PREFIX):
        return _get_opencode_go_model(model, config)

    model_kwargs = {
        "model": model.value,
        **config.model_dump(),
    }

    required_api_key = MODEL_TO_REQUIRED_API_KEY.get(model)
    if required_api_key == "GOOGLE_API_KEY":
        # Gemini supports both the Gemini Developer API (API key) and Vertex AI
        # (Application Default Credentials); the settings decide which one is active.
        model_kwargs.update(get_settings().google_client_kwargs)
    elif required_api_key:
        settings = get_settings()
        if not getattr(settings, required_api_key):
            raise ValueError(f"Required environment variable `{required_api_key}` is not set")
        else:
            model_kwargs["api_key"] = getattr(settings, required_api_key)

    return init_chat_model(**model_kwargs)

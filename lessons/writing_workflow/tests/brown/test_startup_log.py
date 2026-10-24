from pathlib import Path

from loguru import logger

from brown.config_app import AppConfig, log_startup_config

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "underdoc-fallback.yaml"


def test_startup_log_names_config_path_and_node_model_ids() -> None:
    messages: list[str] = []
    sink_id = logger.add(lambda message: messages.append(str(message)), level="INFO")
    try:
        log_startup_config(CONFIG, AppConfig.from_yaml(CONFIG))
    finally:
        logger.remove(sink_id)

    line = next(m for m in messages if "CONFIG_FILE" in m)
    assert str(CONFIG.resolve()) in line
    assert "write_article=opencode_go:deepseek-v4-pro" in line
    assert "review_article=opencode_go:gpt-6-luna" in line

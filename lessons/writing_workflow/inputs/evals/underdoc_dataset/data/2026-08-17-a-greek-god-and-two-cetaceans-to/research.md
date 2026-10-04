# Research dossier: Hermes Agent + DeepSeek V4 Flash + Orca session

Facts reconstructed from the published post.

## Components
- Hermes Agent: Nous Research's autonomous agent, MIT-licensed, with persistent memory and its own skills. Source: https://github.com/NousResearch/hermes-agent
- Installation via a one-line install script; it pulls in uv, Python 3.11.15, ripgrep, ffmpeg and Chromium (via Playwright). Source: https://hermes-agent.nousresearch.com/install.sh
- Nous Portal provides billing and a tool gateway (LLM providers, web search/extract via Firecrawl, image/video via FAL, Whisper speech-to-text, text-to-speech, browser automation); OAuth login in the browser. Source: https://hermes-agent.nousresearch.com/
- DeepSeek V4 Flash: 284B-parameter mixture-of-experts model with 1M-token context built for agentic and coding tasks; variants `deepseek-v4-flash` and cheaper `deepseek-v4-flash-0731`. Source: https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731
- Portal prices cited: $0.11 / $0.22 per million tokens for the default flash variant. Source: https://api-docs.deepseek.com/quick_start/pricing/
- Orca: an agentic development environment that runs any CLI agent (Hermes, Claude Code, Codex) in isolated git worktrees with terminals, diffs and browser preview. Source: https://www.onorca.dev/
- Model release notes. Source: https://api-docs.deepseek.com/updates/

## Session
- Task: refactor the football tutorial repo into a package and wrap it as a skill taking a URL and outputting a rendered match report; goal set with the `/goal` feature. Source: https://github.com/ricardoherediaj/football-analytics-tutorials
- Credit loaded: $5.10 ($5 top-up plus $0.10 courtesy). Source: https://hermes-agent.nousresearch.com/
- Total session cost $2.88: default flash variant processed 119.5M input and 351K output tokens for $2.82; the 0731 variant 24.5M input and 213K output for $0.05; about 144M tokens for roughly $2.87 combined; remaining usage was a few free calls and Firecrawl use. Source: https://hermes-agent.nousresearch.com/
- Review was visual only (no formal eval): pass-network rendering and unreadable stat labels; a SESSION.md was written to log decisions and mistakes, which reduced errors in the player report. Source: https://github.com/ricardoherediaj/football-analytics-tutorials
- Postscript: DeepSeek raised V4 series pricing as of August 16. Source: https://api-docs.deepseek.com/quick_start/pricing/
- Opening poem reference. Source: https://www.reddit.com/r/Hellenism/comments/12cu6hf/poem_for_hermes_day/

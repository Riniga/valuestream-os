"""
MAF adapter — thin wrapper around Microsoft Agent Framework.

This module is the single place in the codebase that imports and configures
the agent_framework package. No other module should import agent_framework
directly. This isolation means that breaking changes in the preview SDK
only affect this file.

Supported credential configurations (read from environment):

  Azure OpenAI (direct):
    AZURE_OPENAI_API_KEY    — API key
    AZURE_OPENAI_ENDPOINT   — endpoint URL
    AZURE_OPENAI_DEPLOYMENT — deployment / model name (default: gpt-4o)
    AZURE_OPENAI_API_VERSION — optional, defaults to 2025-04-01-preview

  OpenAI:
    OPENAI_API_KEY          — API key
    OPENAI_MODEL            — model name (default: gpt-4o)
"""
from __future__ import annotations

import asyncio
import os
from urllib.parse import urlparse


class AgentRunner:
    """
    Runs an agent via Microsoft Agent Framework.

    Usage::

        runner = AgentRunner(name="BusinessAnalyst", instructions="...")
        text = runner.run("Your prompt here")
    """

    def __init__(self, name: str, instructions: str) -> None:
        self._name = name
        self._instructions = instructions
        self._client = _build_client()

    async def run_async(self, prompt: str) -> str:
        """Run the agent inside the current event loop."""
        return await self._run_async(prompt)

    def run(self, prompt: str) -> str:
        """Run the agent synchronously using one temporary event loop."""
        return asyncio.run(self._run_async(prompt))

    async def _run_async(self, prompt: str) -> str:
        from agent_framework import Agent

        agent = Agent(
            self._client,
            instructions=self._instructions,
            name=self._name,
        )
        try:
            response = await agent.run(prompt)
            return response.text
        finally:
            await self._close_underlying_client()

    async def _close_underlying_client(self) -> None:
        """
        Close the underlying async OpenAI/Azure client before the event loop ends.

        MAF clients keep an async HTTP client internally on ``client`` after first use.
        If it is left to finalizers while the loop is already shutting down, httpx/anyio
        can emit ``RuntimeError: Event loop is closed`` on Windows.
        """
        inner_client = getattr(self._client, "client", None)
        if inner_client is None:
            return

        aclose = getattr(inner_client, "aclose", None)
        if callable(aclose):
            await aclose()


# ---------------------------------------------------------------------------
# Internal: client factory
# ---------------------------------------------------------------------------

def _build_client():
    """Build the appropriate MAF client from environment variables."""
    azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

    if azure_key and azure_endpoint:
        return _build_azure_client(azure_key, azure_endpoint)

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        return _build_openai_client(openai_key)

    raise EnvironmentError(
        "Ingen LLM konfigurerad.\n"
        "Alternativ 1 — Azure OpenAI: sätt AZURE_OPENAI_API_KEY och AZURE_OPENAI_ENDPOINT i .env\n"
        "Alternativ 2 — OpenAI: sätt OPENAI_API_KEY i .env"
    )


def _build_azure_client(api_key: str, endpoint: str):
    from agent_framework.azure._responses_client import AzureOpenAIResponsesClient

    parsed = urlparse(endpoint)
    host = parsed.netloc
    if host.endswith(".openai.azure.com"):
        host = host.replace(".openai.azure.com", ".cognitiveservices.azure.com")
    clean_endpoint = f"{parsed.scheme}://{host}/"

    env_version = os.environ.get("AZURE_OPENAI_API_VERSION", "")
    api_version = (
        env_version
        if env_version and env_version <= "2025-04-01-preview"
        else "2025-04-01-preview"
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    return AzureOpenAIResponsesClient(
        api_key=api_key,
        endpoint=clean_endpoint,
        deployment_name=deployment,
        api_version=api_version,
    )


def _build_openai_client(api_key: str):
    from agent_framework.openai._responses_client import OpenAIResponsesClient

    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    return OpenAIResponsesClient(api_key=api_key, model_id=model)

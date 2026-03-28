"""
Business Analyst Agent — thin Microsoft Agent Framework adapter.

The public interface (run) is deliberately minimal so that swapping the
underlying LLM client only requires changes in this file.

Supports both OpenAI and Azure OpenAI.
Azure is used when AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are set.
"""

from __future__ import annotations

import os

from openai import AzureOpenAI, OpenAI


class BusinessAnalystAgent:
    """
    Agent implementing the Business Analyst role from docs/Roller/Business Analyst.md.

    Wraps an OpenAI-compatible client behind a simple run() interface.
    When a dedicated Microsoft Agent Framework SDK is available, only this
    class needs to be updated — callers depend solely on run().

    Priority:
        1. Azure OpenAI  (AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT set)
        2. OpenAI direct (OPENAI_API_KEY set)
    """

    SYSTEM_PROMPT = (
        "Du är en Business Analyst i ValueStream OS-ramverket. "
        "Du arbetar stegvis, strukturerat och tydligt. "
        "Du genererar artifakter exakt enligt den mall du får — utan att lägga till "
        "rubriker, sektioner eller text som inte finns i mallen. "
        "All output ska vara på svenska om inget annat anges."
    )

    def __init__(self, model: str | None = None) -> None:
        azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

        if azure_key and azure_endpoint:
            # Resolve to the Foundry-compatible base URL.
            # Azure AI Foundry Responses API requires the cognitiveservices.azure.com
            # domain. If the .env contains an openai.azure.com or full-path URL,
            # we normalise it automatically.
            from urllib.parse import urlparse
            parsed = urlparse(azure_endpoint)
            host = parsed.netloc
            # Convert openai.azure.com → cognitiveservices.azure.com (Foundry endpoint)
            if host.endswith(".openai.azure.com"):
                resource_name = host.split(".")[0]
                region = host.split(".")[1] if len(host.split(".")) > 1 else ""
                # Extract region from hostname: <name>-<region>.openai.azure.com
                # Foundry naming: <name>-<region>.cognitiveservices.azure.com
                host = host.replace(".openai.azure.com", ".cognitiveservices.azure.com")
            clean_endpoint = f"{parsed.scheme}://{host}/"
            # Use the Responses-API-compatible version.
            # The env var may contain a version from a Foundry URL that does not work
            # with the cognitiveservices endpoint — fall back to the confirmed version.
            _env_ver = os.environ.get("AZURE_OPENAI_API_VERSION", "")
            api_version = _env_ver if _env_ver and _env_ver <= "2025-04-01-preview" else "2025-04-01-preview"
            self._client = AzureOpenAI(
                api_key=azure_key,
                azure_endpoint=clean_endpoint,
                api_version=api_version,
            )
            self._model = model or os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
            self._backend = "azure"
        else:
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                raise EnvironmentError(
                    "Ingen LLM konfigurerad.\n"
                    "Alternativ 1 — Azure OpenAI: sätt AZURE_OPENAI_API_KEY och AZURE_OPENAI_ENDPOINT i .env\n"
                    "Alternativ 2 — OpenAI: sätt OPENAI_API_KEY i .env"
                )
            self._client = OpenAI(api_key=openai_key)
            self._model = model or os.environ.get("OPENAI_MODEL", "gpt-4o")
            self._backend = "openai"

    def run(self, prompt: str) -> str:
        """Send prompt to the LLM and return the generated text.

        Uses the Responses API (openai >= 2.0) which is supported by
        Azure AI Foundry deployments and openai.com.
        """
        response = self._client.responses.create(
            model=self._model,
            instructions=self.SYSTEM_PROMPT,
            input=prompt,
        )
        return response.output_text or ""

    @property
    def backend(self) -> str:
        """Return which backend is active: 'azure' or 'openai'."""
        return self._backend

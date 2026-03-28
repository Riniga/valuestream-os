from __future__ import annotations

import os
from urllib.parse import urlparse

from openai import AzureOpenAI, OpenAI


class BusinessAnalystAgent:

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
            parsed = urlparse(azure_endpoint)
            host = parsed.netloc
            # Azure AI Foundry Responses API requires cognitiveservices.azure.com.
            # Foundry-generated URLs often contain openai.azure.com — normalise here.
            if host.endswith(".openai.azure.com"):
                host = host.replace(".openai.azure.com", ".cognitiveservices.azure.com")
            clean_endpoint = f"{parsed.scheme}://{host}/"

            # Foundry-generated URLs may embed an API version that predates the
            # Responses API. Fall back to a known-working version when needed.
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
        response = self._client.responses.create(
            model=self._model,
            instructions=self.SYSTEM_PROMPT,
            input=prompt,
        )
        return response.output_text or ""

    @property
    def backend(self) -> str:
        return self._backend

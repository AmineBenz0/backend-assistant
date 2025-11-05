"""
LLM Service client abstraction.

This module provides an async client that prefers Azure OpenAI by default
and can optionally fall back to OpenAI.
"""
import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
import openai
from openai import AsyncOpenAI, AsyncAzureOpenAI

logger = logging.getLogger(__name__)


class SimpleLLMClient:
    """
    Simple LLM client that directly uses Azure OpenAI with optional OpenAI fallback.
    
    This client is designed to work with the pipeline_key as prompt_key pattern,
    where pipeline steps can be either Python classes or prompt-based LLM calls.
    """
    
    def __init__(
        self,
        azure_api_key: Optional[str] = None,
        azure_api_base: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        default_model: str = "gpt-5-mini",
        fallback_to_openai: bool = False,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the simple LLM client
        
        Args:
            azure_api_key: Azure OpenAI API key
            azure_api_base: Azure OpenAI API base URL
            azure_api_version: Azure OpenAI API version
            default_model: Default model to use
            fallback_to_openai: Whether to fallback to OpenAI if Azure fails
            openai_api_key: OpenAI API key for fallback
        """
        self.default_model = default_model
        self.fallback_to_openai = fallback_to_openai
        self._initialized = False
        
        # Get configuration from environment if not provided
        self.azure_config = {
            "api_key": azure_api_key or os.getenv("AZURE_OPENAI_API_KEY"),
            "api_base": azure_api_base or os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_BASE_URL"),
            "api_version": azure_api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
        }
        self.azure_secondary_key = os.getenv("AZURE_OPENAI_API_KEY_SECONDARY")
        
        self.openai_config = {
            "api_key": openai_api_key or os.getenv("OPENAI_API_KEY")
        }

        # Gemini configuration
        self.gemini_config = {
            "api_key": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        }

    def _get_gemini_keys(self) -> list[str]:
        """Return a list of Gemini API keys from env in priority order.
        Supports GEMINI_API_KEYS as comma/space separated list; falls back to
        GEMINI_API_KEY or GOOGLE_API_KEY if list is not set. Also supports
        numbered vars GEMINI_API_KEYS_1, GEMINI_API_KEYS_2, ... for docker envs.
        """
        keys_env = os.getenv("GEMINI_API_KEYS")
        keys: list[str] = []
        if keys_env:
            # split on commas and whitespace
            raw = [p.strip() for part in keys_env.split(",") for p in part.split()]  # type: ignore
            keys = [k for k in raw if k]
        # numbered vars (preserve numeric order)
        try:
            for i in range(1, 51):  # support up to 50 keys
                v = os.getenv(f"GEMINI_API_KEYS_{i}")
                if v and v.strip():
                    keys.append(v.strip())
        except Exception:
            pass
        # single-key fallbacks
        single = self.gemini_config.get("api_key") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if single:
            if single not in keys:
                keys.append(single)
        # de-dup while preserving order
        seen = set()
        unique_keys: list[str] = []
        for k in keys:
            if k not in seen:
                seen.add(k)
                unique_keys.append(k)
        return unique_keys
        
        # Initialize clients
        self.azure_client = None
        self.openai_client = None
    
    async def initialize(self) -> None:
        """Initialize the LLM clients"""
        if self._initialized:
            return
        
        try:
            # Initialize Azure OpenAI client if configured
            if self.azure_config["api_key"] and self.azure_config["api_base"]:
                # Use the proper Azure OpenAI client
                azure_endpoint = self.azure_config["api_base"]
                if not azure_endpoint.endswith('/'):
                    azure_endpoint += '/'
                
                self.azure_client = AsyncAzureOpenAI(
                    api_key=self.azure_config["api_key"],
                    azure_endpoint=azure_endpoint,
                    api_version=self.azure_config["api_version"]
                )
                logger.info(f"Azure OpenAI client initialized with endpoint: {azure_endpoint}")
            
            # Initialize OpenAI client if configured
            if self.openai_config["api_key"]:
                self.openai_client = AsyncOpenAI(
                    api_key=self.openai_config["api_key"]
                )
                logger.info("OpenAI client initialized")
            
            if not self.azure_client and not self.openai_client:
                raise ValueError("No LLM clients could be initialized")
            
            self._initialized = True
            logger.info("LLM client initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {str(e)}")
            raise
    
    async def call_llm(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 4000,
        **kwargs
    ) -> str:
        """
        Call LLM with the given prompt
        
        Args:
            prompt: The prompt to send
            model: Model to use (defaults to self.default_model)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments passed to the API
            
        Returns:
            The generated text response
        """
        if not self._initialized:
            await self.initialize()
        
        model = model or self.default_model
        
        try:
            # Detect provider (override > model heuristic)
            provider_override = kwargs.pop("provider", None)
            provider = None
            if isinstance(provider_override, str) and provider_override.strip():
                provider = provider_override.strip().lower()
            elif isinstance(model, str) and model.lower().startswith("gemini"):
                provider = "gemini"
            else:
                provider = "azure_openai"

            if provider == "gemini":
                json_object = bool(kwargs.get("json_object"))
                gemini_keys = self._get_gemini_keys()
                if not gemini_keys:
                    raise ValueError("No Gemini API key found. Set GEMINI_API_KEYS or GEMINI_API_KEY/GOOGLE_API_KEY")

                # Prefer new google-genai SDK if available, else fallback to google-generativeai
                def _run_gemini_sync_genai(api_key_value: str) -> str:
                    from google import genai as google_genai  # type: ignore
                    from google.genai import types as genai_types  # type: ignore
                    client = google_genai.Client(api_key=api_key_value)
                    model_name = model or "gemini-1.5-pro"
                    contents = [
                        genai_types.Content(
                            role="user",
                            parts=[genai_types.Part.from_text(text=prompt)],
                        )
                    ]
                    cfg_kwargs: Dict[str, Any] = {}
                    if temperature is not None:
                        cfg_kwargs["temperature"] = float(temperature)
                    if max_tokens is not None:
                        cfg_kwargs["max_output_tokens"] = int(max_tokens)
                    if json_object:
                        cfg_kwargs["response_mime_type"] = "application/json"
                    generate_cfg = genai_types.GenerateContentConfig(**cfg_kwargs)
                    # Respect server-indicated retry delay for 429
                    import time
                    from google.genai import errors as genai_errors  # type: ignore
                    attempt = 0
                    while True:
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=contents,
                                config=generate_cfg,
                            )
                            break
                        except Exception as e:
                            # Try to parse RetryInfo from error json
                            delay_s = None
                            try:
                                if hasattr(e, "response_json") and isinstance(e.response_json, dict):
                                    details = e.response_json.get("error", {}).get("details", [])
                                    for d in details:
                                        if d.get("@type", "").endswith("RetryInfo"):
                                            # value like '57s'
                                            raw = d.get("retryDelay", "")
                                            if raw.endswith("s"):
                                                delay_s = float(raw[:-1])
                                                break
                            except Exception:
                                pass
                            if delay_s is None:
                                # Default small backoff
                                delay_s = 60.0
                            time.sleep(delay_s)
                            attempt += 1
                            # Optional: limit attempts to avoid infinite loops
                            if attempt >= 2:
                                # one retry only
                                raise
                    if hasattr(response, "text") and response.text:
                        return response.text.strip()
                    return str(response)

                def _run_gemini_sync_generativeai(api_key_value: str) -> str:
                    import google.generativeai as generativeai  # type: ignore
                    generativeai.configure(api_key=api_key_value)
                    cfg: Dict[str, Any] = {}
                    if temperature is not None:
                        cfg["temperature"] = float(temperature)
                    if max_tokens is not None:
                        cfg["max_output_tokens"] = int(max_tokens)
                    if json_object:
                        cfg["response_mime_type"] = "application/json"
                    gmodel = generativeai.GenerativeModel(model or "gemini-1.5-pro")
                    import time
                    attempt = 0
                    while True:
                        try:
                            response = gmodel.generate_content(prompt, generation_config=cfg)
                            break
                        except Exception as e:
                            delay_s = None
                            try:
                                # generativeai exposes structured error via .args sometimes
                                msg = str(e)
                                # crude parse for 'retry in XXs'
                                import re
                                m = re.search(r"retry in (\d+(?:\.\d+)?)s", msg)
                                if m:
                                    delay_s = float(m.group(1))
                            except Exception:
                                pass
                            if delay_s is None:
                                delay_s = 60.0
                            time.sleep(delay_s)
                            attempt += 1
                            if attempt >= 2:
                                raise
                    if hasattr(response, "text") and response.text:
                        return response.text.strip()
                    if getattr(response, "candidates", None):
                        try:
                            return response.candidates[0].content.parts[0].text.strip()
                        except Exception:
                            pass
                    return str(response)

                last_err: Exception | None = None
                for idx, key in enumerate(gemini_keys):
                    try:
                        # Try new google-genai first with current key
                        return await asyncio.to_thread(_run_gemini_sync_genai, key)
                    except Exception as e1:
                        last_err = e1
                        try:
                            # Fallback to google-generativeai with same key
                            return await asyncio.to_thread(_run_gemini_sync_generativeai, key)
                        except Exception as e2:
                            last_err = e2
                            # Try next key
                            continue
                # Exhausted all keys
                if last_err:
                    raise last_err
                raise ValueError("Gemini call failed with all provided keys")

            # Try Azure OpenAI first
            if self.azure_client:
                try:
                    # Build params and adapt token parameter for 2025-04/gpt-5 models
                    params = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        **kwargs,
                    }
                    api_ver = (self.azure_config or {}).get("api_version", "")
                    is_gpt5 = (api_ver >= "2025-04-01") or ((model or "").startswith("gpt-5"))
                    if (not is_gpt5) and (temperature is not None):
                        params["temperature"] = temperature
                    token_key = "max_completion_tokens" if is_gpt5 else "max_tokens"
                    if max_tokens is not None:
                        params[token_key] = max_tokens
                    # Backoff on 429 with server-suggested delay when present
                    import time, re
                    attempts = 0
                    while True:
                        try:
                            response = await self.azure_client.chat.completions.create(**params)
                            return response.choices[0].message.content.strip()
                        except Exception as azure_error:
                            msg = str(azure_error)
                            delay_s = None
                            m = re.search(r"retry after (\d+) seconds", msg, re.IGNORECASE)
                            if m:
                                delay_s = float(m.group(1))
                            if delay_s is None:
                                delay_s = 20.0
                            attempts += 1
                            if attempts > 2:
                                raise
                            time.sleep(delay_s)
                except Exception as azure_error:
                    logger.warning(f"Azure OpenAI call failed: {azure_error}")
                    # Retry once using the secondary Azure key if available
                    if self.azure_secondary_key and self.azure_secondary_key != self.azure_config.get("api_key"):
                        try:
                            logger.info("Retrying Azure OpenAI with secondary API key")
                            # Recreate client with secondary key
                            endpoint = self.azure_config["api_base"]
                            if not endpoint.endswith('/'):
                                endpoint += '/'
                            self.azure_client = AsyncAzureOpenAI(
                                api_key=self.azure_secondary_key,
                                azure_endpoint=endpoint,
                                api_version=self.azure_config["api_version"]
                            )
                            params = {
                                "model": model,
                                "messages": [{"role": "user", "content": prompt}],
                                **kwargs,
                            }
                            api_ver = (self.azure_config or {}).get("api_version", "")
                            is_gpt5 = (api_ver >= "2025-04-01") or ((model or "").startswith("gpt-5"))
                            if (not is_gpt5) and (temperature is not None):
                                params["temperature"] = temperature
                            token_key = "max_completion_tokens" if is_gpt5 else "max_tokens"
                            if max_tokens is not None:
                                params[token_key] = max_tokens

                            # Same backoff on secondary
                            import time, re
                            attempts = 0
                            while True:
                                try:
                                    response = await self.azure_client.chat.completions.create(**params)
                                    return response.choices[0].message.content.strip()
                                except Exception as secondary_error_inner:
                                    msg = str(secondary_error_inner)
                                    delay_s = None
                                    m = re.search(r"retry after (\d+) seconds", msg, re.IGNORECASE)
                                    if m:
                                        delay_s = float(m.group(1))
                                    if delay_s is None:
                                        delay_s = 20.0
                                    attempts += 1
                                    if attempts > 2:
                                        raise secondary_error_inner
                                    time.sleep(delay_s)
                        except Exception as secondary_error:
                            logger.error(f"Secondary key retry failed: {secondary_error}")
                            # Restore to primary client for future attempts
                            endpoint = self.azure_config["api_base"]
                            if not endpoint.endswith('/'):
                                endpoint += '/'
                            self.azure_client = AsyncAzureOpenAI(
                                api_key=self.azure_config["api_key"],
                                azure_endpoint=endpoint,
                                api_version=self.azure_config["api_version"]
                            )
                            raise secondary_error
                    # No secondary key available, re-raise
                    raise azure_error
            
            # Fallback to OpenAI if Azure failed and fallback is enabled
            if self.openai_client and self.fallback_to_openai:
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                return response.choices[0].message.content.strip()
            
            # Final fallback: try Gemini flash if requested model is Azure and Gemini key is present
            try:
                if (isinstance(model, str) and (model.startswith("gpt-") or model.startswith("azure"))) and (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
                    return await self.call_llm(
                        prompt=prompt,
                        model="gemini-2.5-flash",
                        temperature=temperature,
                        max_tokens=max_tokens,
                        provider="gemini",
                        json_object=kwargs.get("json_object", False),
                    )
            except Exception:
                pass

            raise ValueError("No available LLM clients")
            
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise
    
    def call_llm_sync(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 4000,
        json_object: bool = False,
        **kwargs
    ) -> str:
        """
        Synchronous LLM call for Celery compatibility.
        
        Args:
            prompt: The prompt to send
            model: Model to use (defaults to self.default_model)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            json_object: Whether to request JSON object response format
            **kwargs: Additional arguments passed to the API
            
        Returns:
            The generated text response
        """
        import os
        from openai import AzureOpenAI
        
        model = model or self.default_model
        
        try:
            # Detect provider (override > model heuristic)
            provider_override = kwargs.pop("provider", None)
            provider = None
            if isinstance(provider_override, str) and provider_override.strip():
                provider = provider_override.strip().lower()
            elif isinstance(model, str) and model.lower().startswith("gemini"):
                provider = "gemini"
            else:
                provider = "azure_openai"

            if provider == "gemini":
                try:
                    from google import genai as google_genai  # type: ignore
                    from google.genai import types as genai_types  # type: ignore
                except ImportError as e:
                    raise RuntimeError("google-genai package is required for Gemini models. Install with: pip install google-genai") from e

                gemini_keys = self._get_gemini_keys()
                if not gemini_keys:
                    raise ValueError("No Gemini API key found. Set GEMINI_API_KEYS or GEMINI_API_KEY/GOOGLE_API_KEY")

                model_name = model or "gemini-1.5-pro"
                contents = [
                    genai_types.Content(
                        role="user",
                        parts=[genai_types.Part.from_text(text=prompt)],
                    )
                ]
                cfg_kwargs: Dict[str, Any] = {}
                if temperature is not None:
                    cfg_kwargs["temperature"] = float(temperature)
                if max_tokens is not None:
                    cfg_kwargs["max_output_tokens"] = int(max_tokens)
                if json_object:
                    cfg_kwargs["response_mime_type"] = "application/json"
                generate_cfg = genai_types.GenerateContentConfig(**cfg_kwargs)

                last_err: Exception | None = None
                for key in gemini_keys:
                    client = google_genai.Client(api_key=key)
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=contents,
                            config=generate_cfg,
                        )
                        if hasattr(response, "text") and response.text:
                            return response.text.strip()
                        return str(response)
                    except Exception as e:
                        last_err = e
                        # rotate to next key
                        continue
                if last_err:
                    raise last_err
                raise ValueError("Gemini call failed with all provided keys")

            # Initialize synchronous Azure OpenAI client
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_BASE_URL")
            )

            # Call Azure OpenAI synchronously
            # Build params and adapt token parameter for 2025-04/gpt-5 models
            params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object" if json_object else "text"},
                **kwargs
            }
            api_ver = os.getenv("AZURE_OPENAI_API_VERSION", "")
            is_gpt5 = (api_ver >= "2025-04-01") or ((model or "").startswith("gpt-5"))
            if (not is_gpt5) and (temperature is not None):
                params["temperature"] = temperature
            token_key = "max_completion_tokens" if is_gpt5 else "max_tokens"
            if max_tokens is not None:
                params[token_key] = max_tokens

            # Backoff on 429 with suggested delay
            import time, re
            attempts = 0
            while True:
                try:
                    response = client.chat.completions.create(**params)
                    return response.choices[0].message.content.strip()
                except Exception as e:
                    msg = str(e)
                    delay_s = None
                    m = re.search(r"retry after (\d+) seconds", msg, re.IGNORECASE)
                    if m:
                        delay_s = float(m.group(1))
                    if delay_s is None:
                        delay_s = 20.0
                    attempts += 1
                    if attempts > 2:
                        break
                    time.sleep(delay_s)

            # Final fallback to Gemini flash if Azure keeps failing and key available
            if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                return self.call_llm_sync(
                    prompt=prompt,
                    model="gemini-2.5-flash",
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_object=json_object,
                    provider="gemini",
                )

            raise

        except Exception as e:
            logger.error(f"Synchronous LLM call failed: {str(e)}")
            raise

    async def close(self) -> None:
        """Close the LLM clients"""
        try:
            if self.azure_client:
                await self.azure_client.close()
            if self.openai_client:
                await self.openai_client.close()
            self._initialized = False
            logger.info("LLM clients closed")
        except Exception as e:
            logger.warning(f"Warning: Error closing LLM clients: {e}")
        
        
# Backward compatibility alias used elsewhere in the repo
class PreprocessingLLMClient(SimpleLLMClient):
    pass

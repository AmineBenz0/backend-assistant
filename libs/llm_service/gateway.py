"""
LLM Gateway: single entrypoint to format prompts and call LLMs.

This module centralizes:
- Prompt retrieval/formatting via LangfusePromptManager
- LLM invocation via SimpleLLMClient
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union, List
import logging

from libs.llm_service.utils import flatten_dict, parse_llm_json_response 
from .llm_client import SimpleLLMClient
from ..promptStore_service import (
    LangfusePromptManager,
    get_default_langfuse_prompt_manager,
    get_langfuse_prompt_manager_from_config,
)
# PromptType import removed - using string keys directly now


logger = logging.getLogger(__name__)


class LLMGateway:
    """High-level gateway that formats prompts and calls the LLM."""

    def __init__(
        self,
        llm_client: Optional[SimpleLLMClient] = None,
        prompt_manager: Optional[LangfusePromptManager] = None,
    ) -> None:
        self.llm_client = llm_client or SimpleLLMClient()
        self.prompt_manager = prompt_manager or get_default_langfuse_prompt_manager()

    async def generate(
        self,
        prompt_key: str,
        variables: Dict[str, Any],
        *,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 4000,
        **kwargs: Any,
    ) -> str:
        """Format a prompt and generate text with the configured LLM."""
        # Get prompt and any config from Langfuse
        prompt_bundle = None
        try:
            prompt_bundle = self.prompt_manager.get_formatted_prompt_and_config(
                prompt_key, variables
            )
            prompt = prompt_bundle.get("prompt", "")
            config = prompt_bundle.get("config", {})
        except Exception:
            # Fallback to previous behavior if new API not available
            prompt = self.prompt_manager.get_any_prompt(prompt_key, variables)
            config = {}

        logger.debug(
            "Formatted prompt key=%s, length=%d", prompt_key, len(prompt)
        )

        # Resolve parameters from Langfuse config, then function args, then client defaults
        cfg_model = config.get("model") or config.get("llm") or None
        cfg_temperature = config.get("temperature")
        cfg_max_tokens = config.get("max_tokens") or config.get("max_completion_tokens")

        resolved_model = model or cfg_model or getattr(self.llm_client, "default_model", None)
        resolved_temperature = temperature if temperature is not None else (cfg_temperature if cfg_temperature is not None else 0.0)
        resolved_max_tokens = max_tokens if max_tokens is not None else cfg_max_tokens

        # Detect provider from config if present (e.g., provider: gemini)
        provider = (config.get("provider") or "").strip().lower() if isinstance(config, dict) else None

        return await self.llm_client.call_llm(
            prompt=prompt,
            model=resolved_model,
            temperature=resolved_temperature,
            max_tokens=resolved_max_tokens,
            provider=provider,
            **kwargs,
        )

    def send_request_sync(
        self,
        inputs: Dict[str, Any],
        project_name: str,
        prompt_config: Dict[str, Any],
        pipeline_key: str,
        json_object: bool = False,
        domain_id: Optional[str] = None
    ) -> Any:
        """
        Synchronous method for Celery compatibility.
        Uses pipeline_key as prompt_key to fetch from PromptStore (Langfuse).
        All domain logic and input transformation is handled by prompt_manager.
        """
        import os
        import json
        
        try:
            logger.info(f"Processing prompt-based step: {pipeline_key}")
            logger.info(f'################## LLMGateway.send_request_sync ##################')
            logger.info(f'{inputs=}')

            if any(['SkiPeD!!' in str(v) for v in flatten_dict(inputs).values()]):
                logger.info(f'llm call skiped, due to empty input {inputs=}')
                return '{"output": "SkiPeD!!"}'

            # Create prompt manager with configuration if needed
            # Handle both old format (prompt_config_src) and new format (prompt_config dict)
            if isinstance(prompt_config, dict) and prompt_config.get("source") == "langfuse":
                prompt_manager = get_langfuse_prompt_manager_from_config(prompt_config)
            elif isinstance(prompt_config, str) and prompt_config == "langfuse":
                # Fallback for old format - use default manager
                prompt_manager = self.prompt_manager
            else:
                prompt_manager = self.prompt_manager
            
            # Get formatted prompt and config from PromptStore - prompt_manager handles all domain logic
            try:
                prompt_bundle = prompt_manager.get_formatted_prompt_and_config(
                    pipeline_key,
                    inputs,
                    domain_id=domain_id
                )
                formatted_prompt = prompt_bundle.get("prompt", "")
                template_config = prompt_bundle.get("config", {})
            except Exception:
                # Fallback to existing behavior
                formatted_prompt = prompt_manager.get_formatted_prompt(
                    pipeline_key,
                    inputs,
                    domain_id=domain_id
                )
                template_config = {}
            logger.debug(f"Formatted prompt for {pipeline_key}: {formatted_prompt[:200]}...")
            
            # Use the LLM client's synchronous method
            # Resolve parameters from Langfuse config first (no env fallback for model)
            cfg_model = template_config.get("model") or template_config.get("llm")
            cfg_temperature = template_config.get("temperature")
            cfg_max_tokens = template_config.get("max_tokens") or template_config.get("max_completion_tokens")

            resolved_model = cfg_model or getattr(self.llm_client, "default_model", None)
            resolved_temperature = 0.0 if cfg_temperature is None else cfg_temperature
            resolved_max_tokens = cfg_max_tokens if cfg_max_tokens is not None else 4000

            # Detect provider from config if present
            provider = (template_config.get("provider") or "").strip().lower() if isinstance(template_config, dict) else None

            response_content = self.llm_client.call_llm_sync(
                prompt=formatted_prompt,
                model=resolved_model,
                temperature=resolved_temperature,
                max_tokens=resolved_max_tokens,
                json_object=json_object,
                provider=provider
            )
            
            logger.info(f"LLM response received for {pipeline_key}")
            
            # Parse JSON if requested and not already parsed
            if json_object and isinstance(response_content, str):
                parsed_ok = False
                # Attempt 1: direct JSON
                try:
                    response_content = json.loads(response_content)
                    parsed_ok = True
                    logger.debug(f"Parsed JSON response for {pipeline_key} (direct)")
                except Exception:
                    pass
                # Attempt 2: strip markdown fences
                if not parsed_ok:
                    try:
                        response_content = parse_llm_json_response(response_content)
                        parsed_ok = True
                        logger.debug(f"Parsed JSON response for {pipeline_key} (fence-stripped)")
                    except Exception:
                        pass
                # Attempt 3: extract JSON object substring
                if not parsed_ok:
                    try:
                        start = response_content.find('{')
                        end = response_content.rfind('}')
                        if start != -1 and end != -1 and end > start:
                            candidate = response_content[start:end+1]
                            response_content = json.loads(candidate)
                            parsed_ok = True
                            logger.debug(f"Parsed JSON response for {pipeline_key} (substring)")
                    except Exception:
                        pass
                if not parsed_ok:
                    logger.error(f"Failed to parse JSON response for {pipeline_key}; returning raw text for visibility")
                    # Return as text to avoid hard failure; caller can decide
            
            return response_content
            
        except Exception as e:
            logger.error(f"LLMGateway sync request failed for {pipeline_key}: {e}")
            raise



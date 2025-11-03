"""
LLM Gateway: single entrypoint to format prompts and call LLMs.

This module centralizes:
- Prompt retrieval/formatting via LangfusePromptManager
- LLM invocation via SimpleLLMClient

Graph builder code should depend on this gateway instead of crafting prompts
or touching LLM clients directly.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Union, List
import logging

from libs.llm_service.utils import flatten_dict 
from .llm_client import SimpleLLMClient
from ..promptStore_service import (
    LangfusePromptManager,
    get_default_langfuse_prompt_manager,
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
        prompt = self.prompt_manager.get_any_prompt(prompt_key, variables)
        logger.debug(
            "Formatted prompt key=%s, length=%d", prompt_key, len(prompt)
        )
        return await self.llm_client.call_llm(
            prompt=prompt,
            model=(model or getattr(self.llm_client, "default_model", None) or "gpt-4o"),
            temperature=(0.0 if temperature is None else temperature),
            max_tokens=max_tokens,
            **kwargs,
        )

    def send_request_sync(
        self,
        inputs: Dict[str, Any],
        project_name: str,
        prompt_config_src: str,
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

            # Get formatted prompt from PromptStore - prompt_manager handles all domain logic
            formatted_prompt = self.prompt_manager.get_formatted_prompt(
                pipeline_key, 
                inputs, 
                domain_id=domain_id
            )
            logger.debug(f"Formatted prompt for {pipeline_key}: {formatted_prompt[:200]}...")
            
            # Use the LLM client's synchronous method
            response_content = self.llm_client.call_llm_sync(
                prompt=formatted_prompt,
                model=os.getenv("AZURE_OPENAI_LLM", "gpt-4o"),
                temperature=0.0,
                max_tokens=4000,
                json_object=json_object
            )
            
            logger.info(f"LLM response received for {pipeline_key}")
            
            # Parse JSON if requested and not already parsed
            if json_object and isinstance(response_content, str):
                try:
                    response_content = json.loads(response_content)
                    logger.debug(f"Parsed JSON response for {pipeline_key}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response for {pipeline_key}: {e}")
                    raise
            
            return response_content
            
        except Exception as e:
            logger.error(f"LLMGateway sync request failed for {pipeline_key}: {e}")
            raise



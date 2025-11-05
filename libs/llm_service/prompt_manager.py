"""
VectorRAG Prompt Management System (moved to libs.llm_service)

This module provides comprehensive prompt management for VectorRAG operations,
including loading, validation, template variable substitution, and customization.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PromptType(str, Enum):
    """Types of VectorRAG prompts"""



@dataclass
class PromptTemplate:
    """Represents a prompt template with metadata"""
    name: str
    content: str
    variables: List[str] = field(default_factory=list)
    description: Optional[str] = None
    version: str = "1.0"
    required_variables: List[str] = field(default_factory=list)
    optional_variables: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Extract variables from template content after initialization"""
        if not self.variables:
            self.variables = self._extract_variables()
        
        # Categorize variables if not already done
        if not self.required_variables and not self.optional_variables:
            self._categorize_variables()
    
    def _extract_variables(self) -> List[str]:
        """Extract template variables from content"""
        # Find variables in format {variable_name}
        # But exclude JSON structure patterns like {{...}} and complex nested structures
        pattern = r'\{([^{}]+)\}'
        matches = re.findall(pattern, self.content)
        
        # Filter out JSON-like structures and complex patterns
        variables = []
        for match in matches:
            # Skip if it contains JSON-like patterns
            if any(char in match for char in ['"', ':', ',', '\n', '<', '>']):
                continue
            # Skip if it's empty or just whitespace
            if not match.strip():
                continue
            variables.append(match.strip())
        
        return list(set(variables))
    
    def _categorize_variables(self):
        """Categorize variables as required or optional based on common patterns"""
        # Common required variables for VectorRAG
        common_required = {
            'input_text', 'entity_types', 'text', 'entities', 
            'relationships', 'community_id', 'descriptions'
        }
        
        # Common optional variables
        common_optional = {
            'tuple_delimiter', 'record_delimiter', 'completion_delimiter',
            'max_entities', 'language', 'domain', 'context'
        }
        
        for var in self.variables:
            if var in common_required:
                self.required_variables.append(var)
            elif var in common_optional:
                self.optional_variables.append(var)
            else:
                # Default to required for unknown variables
                self.required_variables.append(var)
    
    def validate_variables(self, variables: Dict[str, Any]) -> List[str]:
        """Validate that all required variables are provided"""
        missing = []
        for var in self.required_variables:
            if var not in variables:
                missing.append(var)
        return missing
    
    def substitute(self, variables: Dict[str, Any]) -> str:
        """Substitute variables in the template"""
        # Validate required variables
        missing = self.validate_variables(variables)
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        # Add default values for optional variables
        defaults = self._get_default_values()
        final_variables = {**defaults, **variables}
        
        # Perform substitution
        try:
            return self.content.format(**final_variables)
        except KeyError as e:
            raise ValueError(f"Template variable not provided: {e}")
    
    def _get_default_values(self) -> Dict[str, str]:
        """Get default values for common optional variables"""
        return {
            'tuple_delimiter': '|',
            'record_delimiter': '##',
            'completion_delimiter': '<|COMPLETE|>',
            'max_entities': '10',
            'language': 'English',
            'domain': 'general'
        }


class VectorRAGPromptManager:
    """
    Manages VectorRAG prompts with loading, validation, and customization capabilities
    """
    
    def __init__(self, prompts_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the prompt manager
        
        Args:
            prompts_dir: Directory containing prompt files. If None, uses default location.
        """
        if prompts_dir is None:
            # Default to the prompts directory in this package
            current_dir = Path(__file__).parent
            self.prompts_dir = current_dir / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self.templates: Dict[str, PromptTemplate] = {}
        self.custom_templates: Dict[str, PromptTemplate] = {}
        
        # Default prompt file mappings
        self.prompt_files = {
        }
        
        # Load all prompts on initialization
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """Load all prompt templates from files"""
        for prompt_type, filename in self.prompt_files.items():
            try:
                self._load_prompt(prompt_type, filename)
                logger.info(f"Loaded prompt template: {prompt_type}")
            except Exception as e:
                logger.error(f"Failed to load prompt {prompt_type}: {e}")
    
    def _load_prompt(self, prompt_type: PromptType, filename: str):
        """Load a single prompt template from file"""
        file_path = self.prompts_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            template = PromptTemplate(
                name=prompt_type.value,
                content=content,
                description=f"VectorRAG {prompt_type.value.replace('_', ' ').title()} prompt"
            )
            
            self.templates[prompt_type.value] = template
            
        except Exception as e:
            raise RuntimeError(f"Error loading prompt from {file_path}: {e}")
    
    def get_prompt(self, prompt_type: Union[str, PromptType]) -> PromptTemplate:
        """
        Get a prompt template by type
        """
        if isinstance(prompt_type, PromptType):
            prompt_type = prompt_type.value
        
        # Check custom templates first
        if prompt_type in self.custom_templates:
            return self.custom_templates[prompt_type]
        
        if prompt_type not in self.templates:
            raise KeyError(f"Prompt type '{prompt_type}' not found")
        
        return self.templates[prompt_type]
    
    def get_formatted_prompt(
        self, 
        prompt_type: Union[str, PromptType], 
        variables: Dict[str, Any]
    ) -> str:
        """Get a formatted prompt with variables substituted"""
        template = self.get_prompt(prompt_type)
        return template.substitute(variables)
    
    def add_custom_prompt(
        self, 
        prompt_type: str, 
        content: str, 
        description: Optional[str] = None
    ):
        """Add a custom prompt template"""
        template = PromptTemplate(
            name=prompt_type,
            content=content,
            description=description or f"Custom {prompt_type} prompt"
        )
        
        self.custom_templates[prompt_type] = template
        logger.info(f"Added custom prompt template: {prompt_type}")
    
    def validate_prompt(self, prompt_type: Union[str, PromptType]) -> Dict[str, Any]:
        """Validate a prompt template"""
        try:
            template = self.get_prompt(prompt_type)
            
            return {
                "valid": True,
                "name": template.name,
                "variables": template.variables,
                "required_variables": template.required_variables,
                "optional_variables": template.optional_variables,
                "content_length": len(template.content),
                "version": template.version
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def list_available_prompts(self) -> Dict[str, Dict[str, Any]]:
        """List all available prompt templates"""
        all_prompts = {}
        
        # Add standard templates
        for name, template in self.templates.items():
            all_prompts[name] = {
                "type": "standard",
                "description": template.description,
                "variables": template.variables,
                "version": template.version
            }
        
        # Add custom templates
        for name, template in self.custom_templates.items():
            all_prompts[name] = {
                "type": "custom",
                "description": template.description,
                "variables": template.variables,
                "version": template.version
            }
        
        return all_prompts
    
    def reload_prompts(self):
        """Reload all prompt templates from files"""
        self.templates.clear()
        self._load_all_prompts()
        logger.info("Reloaded all prompt templates")
    
    def export_prompt(self, prompt_type: Union[str, PromptType], file_path: str):
        """Export a prompt template to a file"""
        template = self.get_prompt(prompt_type)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template.content)
        
        logger.info(f"Exported prompt {prompt_type} to {file_path}")
    
    def import_prompt(
        self, 
        prompt_type: str, 
        file_path: str, 
        description: Optional[str] = None
    ):
        """Import a prompt template from a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        self.add_custom_prompt(prompt_type, content, description)
        logger.info(f"Imported prompt {prompt_type} from {file_path}")


# Convenience function to create a default prompt manager
def create_default_prompt_manager() -> VectorRAGPromptManager:
    """Create a VectorRAG prompt manager with default settings"""
    return VectorRAGPromptManager()


# Global instance for easy access
_default_prompt_manager: Optional[VectorRAGPromptManager] = None


def get_default_prompt_manager() -> VectorRAGPromptManager:
    """Get the default global prompt manager instance"""
    global _default_prompt_manager
    if _default_prompt_manager is None:
        _default_prompt_manager = create_default_prompt_manager()
    return _default_prompt_manager



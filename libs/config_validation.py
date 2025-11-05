"""
Environment Variable Validation Module for Kotaemon Backend

Provides comprehensive validation for all required and optional environment variables
with clear error messages and configuration scenarios testing.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import re


class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Result of environment variable validation"""
    level: ValidationLevel
    variable: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class EnvironmentVariable:
    """Environment variable definition with validation rules"""
    name: str
    required: bool = True
    default_value: Optional[str] = None
    description: str = ""
    validation_pattern: Optional[str] = None
    validation_function: Optional[callable] = None
    depends_on: Optional[List[str]] = None
    group: str = "general"


class EnvironmentValidator:
    """Comprehensive environment variable validator"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.variables = self._define_variables()
    
    def _define_variables(self) -> Dict[str, EnvironmentVariable]:
        """Define all environment variables with their validation rules"""
        return {
            # Azure OpenAI Configuration (Primary LLM Provider)
            "AZURE_OPENAI_API_KEY": EnvironmentVariable(
                name="AZURE_OPENAI_API_KEY",
                required=True,
                description="Azure OpenAI API key for LLM and embeddings",
                validation_pattern=r"^[a-zA-Z0-9]{20,}$",
                group="llm_primary"
            ),
            "AZURE_OPENAI_BASE_URL": EnvironmentVariable(
                name="AZURE_OPENAI_BASE_URL",
                required=True,
                description="Azure OpenAI endpoint URL",
                validation_pattern=r"^https://.*\.openai\.azure\.com/?$",
                group="llm_primary"
            ),
            "AZURE_OPENAI_API_VERSION": EnvironmentVariable(
                name="AZURE_OPENAI_API_VERSION",
                required=False,
                default_value="2025-03-01-preview",
                description="Azure OpenAI API version",
                validation_pattern=r"^\d{4}-\d{2}-\d{2}(-preview)?$",
                group="llm_primary"
            ),
            "AZURE_OPENAI_LLM": EnvironmentVariable(
                name="AZURE_OPENAI_LLM",
                required=True,
                description="Azure OpenAI chat/LLM deployment name",
                validation_pattern=r"^[a-zA-Z0-9\-_]+$",
                group="llm_primary"
            ),
            "AZURE_OPENAI_EMBEDDINGS": EnvironmentVariable(
                name="AZURE_OPENAI_EMBEDDINGS",
                required=True,
                description="Azure OpenAI embeddings model deployment name",
                validation_pattern=r"^[a-zA-Z0-9\-_]+$",
                group="llm_primary"
            ),
            
            # OpenAI Configuration (Alternative Provider)
            "OPENAI_API_KEY": EnvironmentVariable(
                name="OPENAI_API_KEY",
                required=False,
                description="OpenAI API key for alternative LLM access",
                validation_pattern=r"^sk-[a-zA-Z0-9]{48,}$",
                group="llm_alternative"
            ),
            "OPENAI_BASE_URL": EnvironmentVariable(
                name="OPENAI_BASE_URL",
                required=False,
                default_value="https://api.openai.com/v1",
                description="OpenAI API base URL",
                validation_pattern=r"^https://.*$",
                group="llm_alternative"
            ),
            "OPENAI_CHAT_MODEL": EnvironmentVariable(
                name="OPENAI_CHAT_MODEL",
                required=False,
                default_value="gpt-4o-mini",
                description="OpenAI chat model name",
                group="llm_alternative"
            ),
            "OPENAI_EMBEDDINGS_MODEL": EnvironmentVariable(
                name="OPENAI_EMBEDDINGS_MODEL",
                required=False,
                default_value="text-embedding-3-small",
                description="OpenAI embeddings model name",
                group="llm_alternative"
            ),
            
            # Anthropic Configuration
            "ANTHROPIC_API_KEY": EnvironmentVariable(
                name="ANTHROPIC_API_KEY",
                required=False,
                description="Anthropic API key for Claude models",
                validation_pattern=r"^sk-ant-[a-zA-Z0-9\-_]{95,}$",
                group="llm_alternative"
            ),
            "ANTHROPIC_CHAT_MODEL": EnvironmentVariable(
                name="ANTHROPIC_CHAT_MODEL",
                required=False,
                default_value="claude-3-5-sonnet-20241022",
                description="Anthropic chat model name",
                group="llm_alternative"
            ),
            
            # Cohere Configuration
            "COHERE_API_KEY": EnvironmentVariable(
                name="COHERE_API_KEY",
                required=False,
                description="Cohere API key for embeddings",
                validation_pattern=r"^[a-zA-Z0-9]{40,}$",
                group="llm_alternative"
            ),
            
            # Database Configuration
            "CHROMADB_URL": EnvironmentVariable(
                name="CHROMADB_URL",
                required=False,
                default_value="http://localhost:8001",
                description="ChromaDB connection URL",
                validation_pattern=r"^https?://.*:\d+/?$",
                group="database"
            ),
            "CHROMA_HOST": EnvironmentVariable(
                name="CHROMA_HOST",
                required=False,
                default_value="localhost",
                description="ChromaDB host",
                group="database"
            ),
            "CHROMA_PORT": EnvironmentVariable(
                name="CHROMA_PORT",
                required=False,
                default_value="8001",
                description="ChromaDB port",
                validation_function=self._validate_port,
                group="database"
            ),
            
            # MinIO Configuration
            "MINIO_ENDPOINT": EnvironmentVariable(
                name="MINIO_ENDPOINT",
                required=False,
                default_value="localhost:9000",
                description="MinIO endpoint",
                validation_pattern=r"^[a-zA-Z0-9\.\-]+:\d+$",
                group="storage"
            ),
            "MINIO_ACCESS_KEY": EnvironmentVariable(
                name="MINIO_ACCESS_KEY",
                required=False,
                default_value="minioadmin",
                description="MinIO access key",
                group="storage"
            ),
            "MINIO_SECRET_KEY": EnvironmentVariable(
                name="MINIO_SECRET_KEY",
                required=False,
                default_value="minioadmin",
                description="MinIO secret key",
                group="storage"
            ),
            "MINIO_SECURE": EnvironmentVariable(
                name="MINIO_SECURE",
                required=False,
                default_value="false",
                description="Whether to use HTTPS for MinIO",
                validation_function=self._validate_boolean,
                group="storage"
            ),
            "MINIO_BUCKET": EnvironmentVariable(
                name="MINIO_BUCKET",
                required=False,
                default_value="kotaemon-pipeline",
                description="MinIO bucket name",
                validation_pattern=r"^[a-z0-9\-]{3,63}$",
                group="storage"
            ),
            
            # Redis Configuration
            "REDIS_HOST": EnvironmentVariable(
                name="REDIS_HOST",
                required=False,
                default_value="localhost",
                description="Redis host",
                group="cache"
            ),
            "REDIS_PORT": EnvironmentVariable(
                name="REDIS_PORT",
                required=False,
                default_value="6379",
                description="Redis port",
                validation_function=self._validate_port,
                group="cache"
            ),
            "REDIS_PASSWORD": EnvironmentVariable(
                name="REDIS_PASSWORD",
                required=False,
                description="Redis password (optional)",
                group="cache"
            ),
            "REDIS_DB": EnvironmentVariable(
                name="REDIS_DB",
                required=False,
                default_value="0",
                description="Redis database number",
                validation_function=self._validate_integer,
                group="cache"
            ),
            
            # Pipeline Configuration
            "LOG_LEVEL": EnvironmentVariable(
                name="LOG_LEVEL",
                required=False,
                default_value="INFO",
                description="Logging level",
                validation_function=self._validate_log_level,
                group="pipeline"
            ),
            "ENABLE_METRICS": EnvironmentVariable(
                name="ENABLE_METRICS",
                required=False,
                default_value="true",
                description="Enable metrics collection",
                validation_function=self._validate_boolean,
                group="pipeline"
            ),
            "ENABLE_LOGGING": EnvironmentVariable(
                name="ENABLE_LOGGING",
                required=False,
                default_value="true",
                description="Enable detailed logging",
                validation_function=self._validate_boolean,
                group="pipeline"
            ),
            "MAX_CONCURRENT_JOBS": EnvironmentVariable(
                name="MAX_CONCURRENT_JOBS",
                required=False,
                default_value="5",
                description="Maximum concurrent pipeline jobs",
                validation_function=self._validate_positive_integer,
                group="pipeline"
            ),
            "JOB_TIMEOUT_SECONDS": EnvironmentVariable(
                name="JOB_TIMEOUT_SECONDS",
                required=False,
                default_value="3600",
                description="Job timeout in seconds",
                validation_function=self._validate_positive_integer,
                group="pipeline"
            ),
            "RETRY_ATTEMPTS": EnvironmentVariable(
                name="RETRY_ATTEMPTS",
                required=False,
                default_value="3",
                description="Number of retry attempts for failed operations",
                validation_function=self._validate_positive_integer,
                group="pipeline"
            ),
            "RETRY_DELAY_SECONDS": EnvironmentVariable(
                name="RETRY_DELAY_SECONDS",
                required=False,
                default_value="30",
                description="Delay between retry attempts in seconds",
                validation_function=self._validate_positive_integer,
                group="pipeline"
            ),
            
            # Environment Configuration
            "ENVIRONMENT": EnvironmentVariable(
                name="ENVIRONMENT",
                required=False,
                default_value="development",
                description="Application environment",
                validation_function=self._validate_environment,
                group="general"
            ),
            "DEBUG": EnvironmentVariable(
                name="DEBUG",
                required=False,
                default_value="false",
                description="Enable debug mode",
                validation_function=self._validate_boolean,
                group="general"
            ),
            "TESTING": EnvironmentVariable(
                name="TESTING",
                required=False,
                default_value="false",
                description="Enable testing mode",
                validation_function=self._validate_boolean,
                group="general"
            ),
            
            # Mock Configuration for Testing
            "USE_MOCKS": EnvironmentVariable(
                name="USE_MOCKS",
                required=False,
                default_value="false",
                description="Use mock services for testing",
                validation_function=self._validate_boolean,
                group="testing"
            ),
            "MOCK_LLM_RESPONSES": EnvironmentVariable(
                name="MOCK_LLM_RESPONSES",
                required=False,
                default_value="false",
                description="Use mock LLM responses",
                validation_function=self._validate_boolean,
                group="testing"
            ),
            "MOCK_EMBEDDING_RESPONSES": EnvironmentVariable(
                name="MOCK_EMBEDDING_RESPONSES",
                required=False,
                default_value="false",
                description="Use mock embedding responses",
                validation_function=self._validate_boolean,
                group="testing"
            ),
        }
    
    def _validate_boolean(self, value: str) -> bool:
        """Validate boolean values"""
        return value.lower() in ("true", "false", "1", "0", "yes", "no")
    
    def _validate_port(self, value: str) -> bool:
        """Validate port numbers"""
        try:
            port = int(value)
            return 1 <= port <= 65535
        except ValueError:
            return False
    
    def _validate_integer(self, value: str) -> bool:
        """Validate integer values"""
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def _validate_positive_integer(self, value: str) -> bool:
        """Validate positive integer values"""
        try:
            return int(value) > 0
        except ValueError:
            return False
    
    def _validate_log_level(self, value: str) -> bool:
        """Validate log level values"""
        return value.upper() in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    
    def _validate_environment(self, value: str) -> bool:
        """Validate environment values"""
        return value.lower() in ("development", "staging", "production", "testing")
    
    def validate_single_variable(self, var_def: EnvironmentVariable) -> List[ValidationResult]:
        """Validate a single environment variable"""
        results = []
        value = os.getenv(var_def.name)
        
        # Check if required variable is missing
        if var_def.required and not value:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                variable=var_def.name,
                message=f"Required environment variable '{var_def.name}' is not set",
                suggestion=f"Set {var_def.name} in your .env file. {var_def.description}"
            ))
            return results
        
        # Use default value if not set and not required
        if not value and var_def.default_value:
            results.append(ValidationResult(
                level=ValidationLevel.INFO,
                variable=var_def.name,
                message=f"Using default value for '{var_def.name}': {var_def.default_value}",
                suggestion=f"You can override this by setting {var_def.name} in your .env file"
            ))
            value = var_def.default_value
        
        # Skip validation if no value and not required
        if not value and not var_def.required:
            return results
        
        # Validate pattern if provided
        if var_def.validation_pattern and value:
            if not re.match(var_def.validation_pattern, value):
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    variable=var_def.name,
                    message=f"Invalid format for '{var_def.name}': {value}",
                    suggestion=f"Value should match pattern: {var_def.validation_pattern}"
                ))
        
        # Validate using custom function if provided
        if var_def.validation_function and value:
            if not var_def.validation_function(value):
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    variable=var_def.name,
                    message=f"Invalid value for '{var_def.name}': {value}",
                    suggestion=f"Check the format and valid values for {var_def.name}"
                ))
        
        return results
    
    def validate_all(self) -> List[ValidationResult]:
        """Validate all environment variables"""
        self.results.clear()
        
        for var_def in self.variables.values():
            self.results.extend(self.validate_single_variable(var_def))
        
        return self.results
    
    def validate_group(self, group: str) -> List[ValidationResult]:
        """Validate environment variables in a specific group"""
        results = []
        
        for var_def in self.variables.values():
            if var_def.group == group:
                results.extend(self.validate_single_variable(var_def))
        
        return results
    
    def get_validation_summary(self) -> Dict[str, int]:
        """Get summary of validation results"""
        summary = {
            "total": len(self.results),
            "errors": len([r for r in self.results if r.level == ValidationLevel.ERROR]),
            "warnings": len([r for r in self.results if r.level == ValidationLevel.WARNING]),
            "info": len([r for r in self.results if r.level == ValidationLevel.INFO])
        }
        return summary
    
    def print_results(self, show_info: bool = True) -> None:
        """Print validation results in a formatted way"""
        if not self.results:
            print("✅ All environment variables are valid!")
            return
        
        # Group results by level
        errors = [r for r in self.results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]
        info = [r for r in self.results if r.level == ValidationLevel.INFO]
        
        # Print errors
        if errors:
            print("❌ ERRORS:")
            for result in errors:
                print(f"  • {result.variable}: {result.message}")
                if result.suggestion:
                    print(f"    💡 {result.suggestion}")
            print()
        
        # Print warnings
        if warnings:
            print("⚠️  WARNINGS:")
            for result in warnings:
                print(f"  • {result.variable}: {result.message}")
                if result.suggestion:
                    print(f"    💡 {result.suggestion}")
            print()
        
        # Print info messages
        if info and show_info:
            print("ℹ️  INFO:")
            for result in info:
                print(f"  • {result.variable}: {result.message}")
                if result.suggestion:
                    print(f"    💡 {result.suggestion}")
            print()
        
        # Print summary
        summary = self.get_validation_summary()
        print(f"📊 Summary: {summary['total']} total, {summary['errors']} errors, {summary['warnings']} warnings, {summary['info']} info")
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors"""
        return any(r.level == ValidationLevel.ERROR for r in self.results)
    
    def get_missing_required_variables(self) -> List[str]:
        """Get list of missing required variables"""
        missing = []
        for var_def in self.variables.values():
            if var_def.required and not os.getenv(var_def.name):
                missing.append(var_def.name)
        return missing
    
    def get_groups(self) -> List[str]:
        """Get list of all variable groups"""
        return list(set(var_def.group for var_def in self.variables.values()))
    
    def test_configuration_scenarios(self) -> Dict[str, bool]:
        """Test various configuration scenarios"""
        scenarios = {
            "minimal_azure_openai": self._test_minimal_azure_openai(),
            "full_azure_openai": self._test_full_azure_openai(),
            "openai_fallback": self._test_openai_fallback(),
            "development_mode": self._test_development_mode(),
            "production_mode": self._test_production_mode(),
            "testing_mode": self._test_testing_mode(),
        }
        return scenarios
    
    def _test_minimal_azure_openai(self) -> bool:
        """Test minimal Azure OpenAI configuration"""
        required_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_BASE_URL",
            "AZURE_OPENAI_CHAT_DEPLOYMENT",
            "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT",
        ]
        return all(os.getenv(var) for var in required_vars)
    
    def _test_full_azure_openai(self) -> bool:
        """Test full Azure OpenAI configuration with all optional variables"""
        return self._test_minimal_azure_openai() and all(
            os.getenv(var) for var in [
                "AZURE_OPENAI_API_VERSION",
            ]
        )
    
    def _test_openai_fallback(self) -> bool:
        """Test OpenAI fallback configuration"""
        return bool(os.getenv("OPENAI_API_KEY"))
    
    def _test_development_mode(self) -> bool:
        """Test development mode configuration"""
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    def _test_production_mode(self) -> bool:
        """Test production mode configuration"""
        env = os.getenv("ENVIRONMENT", "development")
        return env == "production" and not os.getenv("DEBUG", "false").lower() == "true"
    
    def _test_testing_mode(self) -> bool:
        """Test testing mode configuration"""
        return os.getenv("TESTING", "false").lower() == "true"


def validate_environment_variables(show_info: bool = True) -> bool:
    """
    Main function to validate all environment variables
    
    Args:
        show_info: Whether to show info-level messages
    
    Returns:
        True if validation passes (no errors), False otherwise
    """
    print("🔍 Validating Environment Variables")
    print("=" * 50)
    
    validator = EnvironmentValidator()
    validator.validate_all()
    validator.print_results(show_info=show_info)
    
    if validator.has_errors():
        print("\n❌ Environment validation failed. Please fix the errors above.")
        return False
    else:
        print("\n✅ Environment validation passed!")
        return True


def test_configuration_scenarios() -> None:
    """Test various configuration scenarios"""
    print("\n🧪 Testing Configuration Scenarios")
    print("=" * 50)
    
    validator = EnvironmentValidator()
    scenarios = validator.test_configuration_scenarios()
    
    for scenario, passed in scenarios.items():
        status = "✅" if passed else "❌"
        print(f"{status} {scenario.replace('_', ' ').title()}")
    
    print()


def main():
    """Main function for running validation as a script"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test-scenarios":
        test_configuration_scenarios()
        return 0
    
    success = validate_environment_variables()
    
    if "--test-scenarios" not in sys.argv:
        test_configuration_scenarios()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
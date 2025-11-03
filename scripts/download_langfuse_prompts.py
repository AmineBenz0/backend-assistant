#!/usr/bin/env python3
"""
Download all latest prompts from Langfuse to local .txt files.

This script downloads all prompts with the 'production' label from Langfuse
and saves them as {prompt_key}.txt files in backend/scripts/prompts/
"""

import argparse
import os
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

try:
    from langfuse import Langfuse
except Exception as import_error:
    raise RuntimeError(
        "The 'langfuse' package is required. Install it via pip (see backend/scripts/requirements.txt)."
    ) from import_error


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
REPO_ROOT = BACKEND_DIR.parent
PROMPTS_DIR = SCRIPT_DIR / "prompts"


def load_env_vars() -> None:
    """
    Load environment variables for Langfuse. Attempts the following (in order):
    - backend/local.env
    - .env at repo root
    - Existing process environment (always)
    """
    # Load backend/local.env if present
    backend_local_env = BACKEND_DIR / "local.env"
    if backend_local_env.exists():
        load_dotenv(dotenv_path=backend_local_env, override=True)

    # Load repo root .env if present
    repo_dotenv = REPO_ROOT / ".env"
    if repo_dotenv.exists():
        load_dotenv(dotenv_path=repo_dotenv, override=True)


def mask_key(value: str | None) -> str:
    if not value:
        return "<none>"
    if len(value) <= 8:
        return "****"
    return value[:8] + "..."


def get_all_prompts(langfuse: Langfuse, label: str = "production") -> List[Dict[str, Any]]:
    """
    Get all prompts with the specified label from Langfuse.
    
    Note: Langfuse doesn't have a direct API to list all prompts,
    so we'll try to get known prompt names and fetch them individually.
    """
    # Known prompt names that we expect to find
    known_prompt_names = [
        "extract-entities",
        "relationship-extraction", 
        "community-report",
        "summarize-descriptions",
        "claim-extraction",
        "duplicate-detection",
        "entity-merging"
    ]
    
    prompts = []
    
    for prompt_name in known_prompt_names:
        try:
            prompt = langfuse.get_prompt(name=prompt_name, label=label)
            if prompt:
                prompts.append({
                    "name": prompt_name,
                    "content": prompt.prompt,
                    "config": prompt.config or {},
                    "labels": prompt.labels or [],
                    "version": prompt.version or 1
                })
                print(f"[SUCCESS] Found prompt '{prompt_name}' (version {prompt.version or 1})")
            else:
                print(f"[WARN] Prompt '{prompt_name}' not found with label '{label}'")
        except Exception as e:
            print(f"[ERROR] Failed to fetch prompt '{prompt_name}': {e}")
    
    return prompts


def save_prompt_to_file(prompt: Dict[str, Any], prompts_dir: Path) -> bool:
    """Save a prompt to a .txt file"""
    try:
        prompt_name = prompt["name"]
        content = prompt["content"]
        
        # Convert kebab-case back to underscore for filename
        filename = prompt_name.replace("-", "_") + ".txt"
        filepath = prompts_dir / filename
        
        # Create directory if it doesn't exist
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Write the prompt content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[SUCCESS] Saved prompt '{prompt_name}' to {filepath}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to save prompt '{prompt['name']}': {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download all latest prompts from Langfuse to local .txt files"
    )
    parser.add_argument(
        "--organization",
        default=os.environ.get("LANGFUSE_ORGANIZATION_NAME"),
        help="Organization name in Langfuse (for logging/validation)",
    )
    parser.add_argument(
        "--project",
        default=os.environ.get("LANGFUSE_PROJECT_NAME"),
        help="Project name in Langfuse. Ensure API keys belong to this project.",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("LANGFUSE_HOST"),
        help="Langfuse host (e.g., http://localhost:3000)",
    )
    parser.add_argument(
        "--public-key",
        default=os.environ.get("LANGFUSE_PUBLIC_KEY"),
        help="Langfuse public key (project-scoped)",
    )
    parser.add_argument(
        "--secret-key",
        default=os.environ.get("LANGFUSE_SECRET_KEY"),
        help="Langfuse secret key (project-scoped)",
    )
    parser.add_argument(
        "--label",
        default="production",
        help="Label of prompts to download (default: production)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROMPTS_DIR),
        help=f"Directory to save prompt files (default: {PROMPTS_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, only prints actions without downloading files",
    )
    args = parser.parse_args()

    load_env_vars()

    # Resolve effective connection params
    effective_host = args.host or os.environ.get("LANGFUSE_HOST")
    effective_pk = args.public_key or os.environ.get("LANGFUSE_PUBLIC_KEY")
    effective_sk = args.secret_key or os.environ.get("LANGFUSE_SECRET_KEY")

    required_env = [
        ("LANGFUSE_PUBLIC_KEY", effective_pk),
        ("LANGFUSE_SECRET_KEY", effective_sk),
        ("LANGFUSE_HOST", effective_host),
    ]
    missing = [name for name, val in required_env if not val]
    if missing:
        missing_str = ", ".join(missing)
        raise EnvironmentError(
            f"Missing required environment variables for Langfuse: {missing_str}. "
            f"Set them in 'backend/local.env' or your environment."
        )

    target_org = args.organization or "<unspecified>"
    target_project = args.project or "<unspecified>"
    output_dir = Path(args.output_dir)

    print(f"Downloading prompts from Langfuse:")
    print(f"  LANGFUSE_HOST={effective_host}")
    print(f"  LANGFUSE_PUBLIC_KEY={mask_key(effective_pk)}")
    print(f"  Organization={target_org}")
    print(f"  Project={target_project}")
    print(f"  Label={args.label}")
    print(f"  Output directory={output_dir}")
    print()

    if args.dry_run:
        print("[DRY RUN] Would download prompts but not save files")
        langfuse = None
    else:
        # Initialize client
        langfuse = Langfuse(public_key=effective_pk, secret_key=effective_sk, host=effective_host)

    if args.dry_run:
        print("[DRY RUN] Would fetch all prompts with label 'production'")
        print("[DRY RUN] Would save them to .txt files in the output directory")
        return 0

    # Get all prompts
    print(f"Fetching all prompts with label '{args.label}'...")
    prompts = get_all_prompts(langfuse, args.label)
    
    if not prompts:
        print(f"[WARN] No prompts found with label '{args.label}'")
        return 1

    print(f"Found {len(prompts)} prompts to download")
    print()

    # Save each prompt to file
    success_count = 0
    for prompt in prompts:
        if save_prompt_to_file(prompt, output_dir):
            success_count += 1

    print()
    print(f"Done. Downloaded {success_count}/{len(prompts)} prompts to {output_dir}")
    
    if success_count > 0:
        print()
        print("Downloaded files:")
        for prompt in prompts:
            filename = prompt["name"].replace("-", "_") + ".txt"
            filepath = output_dir / filename
            if filepath.exists():
                print(f"  - {filepath}")
    
    return 0 if success_count == len(prompts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
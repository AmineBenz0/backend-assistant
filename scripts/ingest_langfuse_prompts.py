import argparse
import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

try:
    # Prefer get_client as per Langfuse docs, but allow explicit Langfuse init
    from langfuse import get_client, Langfuse
except Exception as import_error:  # pragma: no cover
    raise RuntimeError(
        "The 'langfuse' package is required. Install it via pip (see backend/scripts/requirements.txt)."
    ) from import_error


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
REPO_ROOT = BACKEND_DIR.parent
PROMPTS_DIR = SCRIPT_DIR / "prompts"

# Auto-discover prompt files in the prompts directory
def get_prompt_files() -> List[Path]:
    """Auto-discover all .txt files in the prompts directory"""
    if not PROMPTS_DIR.exists():
        return []
    return list(PROMPTS_DIR.glob("*.txt"))


def load_env_vars() -> None:
    """
    Load environment variables for Langfuse. Attempts the following (in order):
    - backend/local.env
    - .env at repo root
    - Existing process environment (always)
    """
    # Always keep existing env, only fill in missing from files
    # Load backend/local.env if present
    backend_local_env = BACKEND_DIR / "local.env"
    if backend_local_env.exists():
        # Force override to ensure correct project keys are used
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


def kebab_case(name: str) -> str:
    stem = Path(name).stem
    return stem.replace("_", "-")


def get_existing_prompt_versions(langfuse: Langfuse, prompt_name: str) -> List[dict]:
    """Get all existing versions of a prompt"""
    try:
        # Get all prompts and filter by name
        # Note: Langfuse doesn't have a direct API to get all versions of a specific prompt
        # We'll need to work with what's available
        return []
    except Exception as e:
        print(f"[WARN] Could not fetch existing versions for '{prompt_name}': {e}")
        return []


def archive_existing_prompt(langfuse: Langfuse, prompt_name: str, current_label: str = "production") -> bool:
    """Archive the current production version by changing its label"""
    try:
        # Get the current production prompt
        current_prompt = langfuse.get_prompt(name=prompt_name, label=current_label)
        if current_prompt:
            print(f"[INFO] Found existing prompt '{prompt_name}' with label '{current_label}'")
            print(f"[INFO] Current version will be archived when new version is created")
            return True
        return False
    except Exception as e:
        print(f"[WARN] Could not check existing prompt '{prompt_name}': {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest text prompts into Langfuse Prompt Management"
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
        default="http://localhost:3000",
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
        help="Label to assign to the created prompt versions (default: production)",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("DEFAULT_LLM_MODEL", "gpt-4o"),
        help="Model name to store in prompt config (default: gpt-4o)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=float(os.environ.get("DEFAULT_LLM_TEMPERATURE", 0)),
        help="Temperature to store in prompt config (default: 0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, only prints actions without creating prompts in Langfuse",
    )
    args = parser.parse_args()

    load_env_vars()

    # Resolve effective connection params
    effective_host = args.host or "http://localhost:3000"
    effective_pk = args.public_key or os.environ.get("LANGFUSE_PUBLIC_KEY")
    effective_sk = args.secret_key or os.environ.get("LANGFUSE_SECRET_KEY")

    required_env = [
        ("LANGFUSE_PUBLIC_KEY", effective_pk),
        ("LANGFUSE_SECRET_KEY", effective_sk),
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

    if args.dry_run:
        print("[DRY RUN] Would connect to Langfuse at:")
        print(f"  LANGFUSE_HOST={effective_host}")
        print(f"  LANGFUSE_PUBLIC_KEY={mask_key(effective_pk)}")
        print(f"  LANGFUSE_SECRET_KEY={mask_key(effective_sk)}")
        print(f"  Organization={target_org}")
        print(f"  Project={target_project}")

    if args.dry_run:
        langfuse = None
    else:
        # Initialize client explicitly with effective params to avoid relying on global env
        langfuse = Langfuse(public_key=effective_pk, secret_key=effective_sk, host=effective_host)

    # Auto-discover prompt files
    prompt_files = get_prompt_files()
    
    if not prompt_files:
        print(f"[INFO] No prompt files found in {PROMPTS_DIR}")
        print("[INFO] Create .txt files in backend/scripts/prompts/ to ingest them.")
        return 0

    print(f"[INFO] Found {len(prompt_files)} prompt files to ingest:")
    for pf in prompt_files:
        print(f"  - {pf.name}")

    success_count = 0
    for prompt_path in prompt_files:
        if not prompt_path.exists():
            print(f"[WARN] Prompt file not found: {prompt_path}")
            continue

        prompt_text = prompt_path.read_text(encoding="utf-8").strip()
        if not prompt_text:
            print(f"[WARN] Prompt file is empty: {prompt_path}")
            continue

        prompt_name = kebab_case(prompt_path.name)

        print(f"Processing prompt '{prompt_name}' from '{prompt_path}' with label '{args.label}'")

        if args.dry_run:
            print(f"[DRY RUN] Would ingest prompt '{prompt_name}'")
            success_count += 1
            continue

        try:
            # Check if prompt already exists with the target label
            existing_archived = False
            if not args.dry_run:
                existing_archived = archive_existing_prompt(langfuse, prompt_name, args.label)
            
            # Create the new prompt version
            langfuse.create_prompt(
                name=prompt_name,
                type="text",
                prompt=prompt_text,
                labels=[args.label],
                config={
                    "model": args.model,
                    "temperature": args.temperature,
                    "supported_languages": ["en"],
                },
            )
            
            if existing_archived:
                print(f"[SUCCESS] Updated prompt '{prompt_name}' - previous version archived")
            else:
                print(f"[SUCCESS] Created new prompt '{prompt_name}'")
            
            success_count += 1
            
        except Exception as e:  # pragma: no cover
            print(f"[ERROR] Failed to create/update prompt '{prompt_name}': {e}")

    print(f"Done. Ingested {success_count}/{len(prompt_files)} prompts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



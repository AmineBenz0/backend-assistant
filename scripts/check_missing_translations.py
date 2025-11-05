#!/usr/bin/env python3
"""
Check which prompts are missing Italian translations.
"""

from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EN_DIR = SCRIPT_DIR / "prompts" / "dpac" / "en"
IT_DIR = SCRIPT_DIR / "prompts" / "dpac" / "it"


def main():
    """Check for missing Italian translations."""
    
    if not EN_DIR.exists():
        print(f"[ERROR] English prompts directory not found: {EN_DIR}")
        return 1
    
    if not IT_DIR.exists():
        print(f"[ERROR] Italian prompts directory not found: {IT_DIR}")
        return 1
    
    # Get all English prompt files
    en_files = set(f.name for f in EN_DIR.glob("*.txt"))
    
    # Get all Italian prompt files
    it_files = set(f.name for f in IT_DIR.glob("*.txt"))
    
    # Find missing translations
    missing = en_files - it_files
    
    if not missing:
        print("[SUCCESS] All English prompts have Italian translations!")
        return 0
    
    print(f"[INFO] Found {len(missing)} prompts missing Italian translations:\n")
    
    for filename in sorted(missing):
        en_path = EN_DIR / filename
        it_path = IT_DIR / filename
        
        print(f"  - {filename}")
        print(f"    EN: {en_path}")
        print(f"    IT: {it_path} (missing)")
        print()
    
    print(f"\n[ACTION] To create Italian versions:")
    print(f"  1. Copy English files to Italian directory:")
    print(f"     cp scripts/prompts/dpac/en/<file>.txt scripts/prompts/dpac/it/<file>.txt")
    print(f"  2. Translate the content to Italian")
    print(f"  3. Run: python scripts/ingest_langfuse_prompts.py --language it")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

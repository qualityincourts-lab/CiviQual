"""Inject the exported public key into license_manager.py.

Usage:
    python scripts/update_pubkey.py <path_to_public_key.pem>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_pubkey.py <public_key.pem>")
        sys.exit(1)

    pub_path = Path(sys.argv[1])
    if not pub_path.exists():
        print(f"Public key file not found: {pub_path}")
        sys.exit(1)

    pub_pem = pub_path.read_text(encoding="utf-8").strip()

    repo_root = Path(__file__).resolve().parent.parent
    target = repo_root / "license_manager.py"
    source = target.read_text(encoding="utf-8")

    pattern = re.compile(
        r'(PUBLIC_KEY_PEM: bytes = b""")(.*?)(""")',
        re.DOTALL,
    )
    replacement = f'PUBLIC_KEY_PEM: bytes = b"""\n{pub_pem}\n"""'
    if not pattern.search(source):
        print("Could not locate PUBLIC_KEY_PEM block in license_manager.py.")
        sys.exit(2)

    new_source = pattern.sub(lambda m: replacement, source, count=1)
    target.write_text(new_source, encoding="utf-8")
    print(f"Updated PUBLIC_KEY_PEM in {target}")


if __name__ == "__main__":
    main()

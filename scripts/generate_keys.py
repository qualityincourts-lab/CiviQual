"""Generate RSA keys and sign CiviQual Stats Pro license files.

Usage:
    python generate_keys.py --generate-keys
    python generate_keys.py --sign --licensee "Jane Doe" --expires 2027-12-31

Keys are stored in %USERPROFILE%\\.civiqual_keys by default. The public key is
printed to stdout in a format that can be pasted into license_manager.py.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import uuid
from datetime import date
from pathlib import Path

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
except ImportError:
    raise SystemExit(
        "The 'cryptography' package is required. "
        "Install it with: pip install cryptography"
    )


KEYS_DIR = Path(os.path.expanduser("~")) / ".civiqual_keys"
PRIVATE_KEY = KEYS_DIR / "civiqual_private.pem"
PUBLIC_KEY = KEYS_DIR / "civiqual_public.pem"


def generate_keys() -> None:
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    priv_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pub_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    PRIVATE_KEY.write_bytes(priv_pem)
    PUBLIC_KEY.write_bytes(pub_pem)
    print(f"Private key written to: {PRIVATE_KEY}")
    print(f"Public key written to:  {PUBLIC_KEY}")
    print()
    print("Paste the following into license_manager.py as PUBLIC_KEY_PEM:")
    print("-" * 72)
    print(pub_pem.decode("ascii"))


def sign_license(licensee: str, expires: str | None, out: Path) -> None:
    if not PRIVATE_KEY.exists():
        raise SystemExit(f"Private key not found at {PRIVATE_KEY}. "
                         "Run --generate-keys first.")
    payload = {
        "licensee": licensee,
        "edition": "pro",
        "issued": date.today().isoformat(),
        "expires": expires,
        "license_id": str(uuid.uuid4()),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    priv_key = serialization.load_pem_private_key(PRIVATE_KEY.read_bytes(), password=None)
    signature = priv_key.sign(
        canonical,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    payload["signature"] = base64.b64encode(signature).decode("ascii")
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"License written to: {out}")
    print(f"Licensee: {licensee}")
    print(f"Expires:  {expires or 'never'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate keys and sign CiviQual licenses.")
    parser.add_argument("--generate-keys", action="store_true",
                        help="Generate a new 3072-bit RSA key pair.")
    parser.add_argument("--sign", action="store_true",
                        help="Sign a Pro license file.")
    parser.add_argument("--licensee", type=str, help="Licensee name.")
    parser.add_argument("--expires", type=str, default=None,
                        help="Expiry date (YYYY-MM-DD). Omit for perpetual.")
    parser.add_argument("--out", type=Path, default=Path("license.json"),
                        help="Output license file path.")
    args = parser.parse_args()

    if args.generate_keys:
        generate_keys()
        return
    if args.sign:
        if not args.licensee:
            raise SystemExit("--sign requires --licensee")
        sign_license(args.licensee, args.expires, args.out)
        return
    parser.print_help()


if __name__ == "__main__":
    main()

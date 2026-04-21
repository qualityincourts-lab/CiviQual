"""License manager for CiviQual Stats Pro.

Implements RSA-PSS signature verification of license files. The public key is
embedded in this module; the corresponding private key is held only by the
publisher and is used to sign license tokens.

License file format (JSON):
    {
        "licensee": "<name or email>",
        "edition": "pro",
        "issued": "YYYY-MM-DD",
        "expires": "YYYY-MM-DD" | null,
        "license_id": "<uuid>",
        "signature": "<base64 RSA-PSS signature over the canonicalized payload>"
    }
"""

from __future__ import annotations

import base64
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# The cryptography package is optional. If it is not installed, the license
# manager falls back to a fail-closed "Free only" state.
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa  # noqa: F401
    from cryptography.exceptions import InvalidSignature
    _CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CRYPTO_AVAILABLE = False


# ---------------------------------------------------------------------------
# Embedded public key
# ---------------------------------------------------------------------------
# Replace the placeholder below with the production public key exported by
# scripts/generate_keys.py. The PEM content must remain inside the triple-
# quoted string.
PUBLIC_KEY_PEM: bytes = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvQIDAQAB
-----END PUBLIC KEY-----
"""


def _canonical_payload(data: dict) -> bytes:
    """Return a stable JSON byte string used for signature verification."""
    payload = {k: v for k, v in data.items() if k != "signature"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _default_license_path() -> Path:
    """Return the default license file path for the current OS user."""
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "CiviQualStats" / "license.json"


class LicenseManager:
    """Validate a Pro license file and expose an ``is_pro`` flag."""

    def __init__(self, license_path: Optional[Path] = None):
        self._path = Path(license_path) if license_path else _default_license_path()
        self._licensee: Optional[str] = None
        self._edition: str = "free"
        self._issued: Optional[date] = None
        self._expires: Optional[date] = None
        self._license_id: Optional[str] = None
        self._error: Optional[str] = None
        self._is_pro: bool = False
        self._load()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------
    @property
    def is_pro(self) -> bool:
        return self._is_pro

    @property
    def edition(self) -> str:
        return "Pro" if self._is_pro else "Free"

    @property
    def licensee(self) -> Optional[str]:
        return self._licensee

    @property
    def expires(self) -> Optional[date]:
        return self._expires

    @property
    def license_path(self) -> Path:
        return self._path

    @property
    def error(self) -> Optional[str]:
        return self._error

    # ------------------------------------------------------------------
    # Loading and verification
    # ------------------------------------------------------------------
    def _load(self) -> None:
        if not self._path.exists():
            self._error = "No license file found; running in Free mode."
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception as exc:
            self._error = f"License file could not be parsed: {exc}"
            return

        if not _CRYPTO_AVAILABLE:
            self._error = (
                "The 'cryptography' package is not installed; "
                "signature verification is disabled. Running in Free mode."
            )
            return

        signature_b64 = data.get("signature")
        if not signature_b64:
            self._error = "License file is missing a signature."
            return

        try:
            public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)
            signature = base64.b64decode(signature_b64)
            payload = _canonical_payload(data)
            public_key.verify(
                signature,
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        except InvalidSignature:
            self._error = "License signature is invalid."
            return
        except Exception as exc:
            self._error = f"License verification failed: {exc}"
            return

        # Signature is valid; populate fields.
        self._licensee = data.get("licensee")
        self._edition = data.get("edition", "free").lower()
        self._license_id = data.get("license_id")

        issued = data.get("issued")
        expires = data.get("expires")
        try:
            if issued:
                self._issued = datetime.strptime(issued, "%Y-%m-%d").date()
            if expires:
                self._expires = datetime.strptime(expires, "%Y-%m-%d").date()
        except ValueError:
            self._error = "License dates are malformed."
            return

        if self._expires and self._expires < date.today():
            self._error = f"License expired on {self._expires.isoformat()}."
            return

        if self._edition != "pro":
            self._error = "License edition is not Pro."
            return

        self._is_pro = True
        self._error = None

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------
    def status_text(self) -> str:
        if self._is_pro:
            details = f"Licensed to: {self._licensee or 'unnamed'}"
            if self._expires:
                details += f"  |  Expires: {self._expires.isoformat()}"
            return details
        return self._error or "Free mode"

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Optional

from botocore.exceptions import ClientError

try:
    import boto3
except ImportError:  # allow local dev without boto3
    boto3 = None  # type: ignore


class SecretManager:
    def __init__(self) -> None:
        self.mode = os.getenv("ENVIRONMENT", "local")
        self.client = None

        if self.mode == "production":
            if boto3 is None:
                raise RuntimeError("boto3 is required in production mode")
            try:
                self.client = boto3.client("secretsmanager", region_name="us-east-1")
            except Exception as exc:
                raise RuntimeError(
                    f"AWS Secrets Manager client init failed: {exc}"
                ) from exc

    @lru_cache(maxsize=50)
    def get_secret(self, secret_name: str, key_override: Optional[str] = None) -> str:
        if self.mode != "production":
            env_key = key_override or secret_name.upper().replace("-", "_")
            value = os.environ.get(env_key)
            if value is None:
                raise RuntimeError(f"Missing env var {env_key}")
            return value

        if not self.client:
            raise RuntimeError("Secrets Manager client not initialized")

        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            raw = response.get("SecretString")
            if not raw:
                raise RuntimeError(f"Secret {secret_name} contained no string payload")

            parsed: Dict[str, str] = json.loads(raw)
            key = key_override or "default"
            if key not in parsed:
                raise RuntimeError(f"Secret {secret_name} missing key '{key}'")
            return parsed[key]
        except ClientError as exc:
            raise RuntimeError(f"Failed to retrieve secret {secret_name}: {exc}") from exc


secrets = SecretManager()

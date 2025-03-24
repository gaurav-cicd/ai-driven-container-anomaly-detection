import os
import hvac
from typing import Dict, Any, Optional

class VaultConfig:
    def __init__(self):
        """Initialize Vault client with environment variables."""
        self.client = hvac.Client(
            url=os.getenv('VAULT_URL'),
            token=os.getenv('VAULT_TOKEN'),
            verify=os.getenv('VAULT_VERIFY_SSL', 'True').lower() == 'true'
        )
        self.secret_path = os.getenv('VAULT_SECRET_PATH', 'secret/container-anomaly-detection')

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret from Vault."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=self.secret_path
            )
            return response['data']['data'].get(key)
        except Exception as e:
            print(f"Error retrieving secret {key} from Vault: {str(e)}")
            return None

    def get_all_secrets(self) -> Dict[str, Any]:
        """Retrieve all secrets from the configured path."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=self.secret_path
            )
            return response['data']['data']
        except Exception as e:
            print(f"Error retrieving secrets from Vault: {str(e)}")
            return {}

    def set_secret(self, key: str, value: str) -> bool:
        """Set a secret in Vault."""
        try:
            current_secrets = self.get_all_secrets()
            current_secrets[key] = value
            self.client.secrets.kv.v2.create_or_update_secret(
                path=self.secret_path,
                secret=current_secrets
            )
            return True
        except Exception as e:
            print(f"Error setting secret {key} in Vault: {str(e)}")
            return False

    def delete_secret(self, key: str) -> bool:
        """Delete a secret from Vault."""
        try:
            current_secrets = self.get_all_secrets()
            if key in current_secrets:
                del current_secrets[key]
                self.client.secrets.kv.v2.create_or_update_secret(
                    path=self.secret_path,
                    secret=current_secrets
                )
            return True
        except Exception as e:
            print(f"Error deleting secret {key} from Vault: {str(e)}")
            return False 
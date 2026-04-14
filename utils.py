from keycloak import KeycloakOpenID
from filip.models.base import FiwareHeader
import time
from pydantic import computed_field, ConfigDict, model_validator, PrivateAttr

AVAILABLE_SERVICES = (
    "n5geh_demo",
    "entirety"
)
CREDENTIALS = {
    "user_name": "n5geh_demo",
    "password": "n5geh_demo",
    "client_id": "n5geh_demo",
    "client_secret": "LZXaIGtD6Ida4X9Z2Zex491sq4in9Wzv"
}

class KeycloakTokenManager:
    def __init__(self, fiware_service: str):
        if fiware_service not in AVAILABLE_SERVICES:
            raise ValueError(f"Service {fiware_service} not recognized.")
        self.client = KeycloakOpenID(
            server_url="https://sso.eonerc.rwth-aachen.de",
            client_id=CREDENTIALS["client_id"],
            realm_name="EBC-Dev",
            client_secret_key=CREDENTIALS["client_secret"]
        )
        self._token_data = None
        self._expiry_time = 0

    def get_access_token(self):
        if not self._token_data or time.time() >= (self._expiry_time - 10):
            print(f"Fetching new token for service...")
            self._token_data = self.client.token(
                username=CREDENTIALS["user_name"],
                password=CREDENTIALS["password"])
            self._expiry_time = time.time() + self._token_data['expires_in']
        return self._token_data['access_token']


class FiwareHeaderSecure(FiwareHeader):
    # 1. Allow custom types in the model
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # 2. Use a Private Attribute so it's hidden from JSON/Exports
    _token_manager: KeycloakTokenManager = PrivateAttr()

    @model_validator(mode='after')
    def initialize_manager(self) -> 'FiwareHeaderSecure':
        """
        Runs automatically after 'service' and 'service_path' are validated.
        We use self.service (from the base FiwareHeader) to init the manager.
        """
        self._token_manager = KeycloakTokenManager(fiware_service=self.service)
        return self

    @computed_field
    @property
    def Authorization(self) -> str:
        """Dynamically fetched when model_dump() or model_dump_json() is called"""
        return f"Bearer {self._token_manager.get_access_token()}"


if __name__ == '__main__':
    # Notice we no longer pass the manager here!
    header = FiwareHeaderSecure(
        service="n5geh_demo",
        service_path='/'
    )

    # The Authorization field will trigger the token fetch automatically
    print(header.model_dump_json(indent=2))

if __name__ == '__main__':
    # Notice we no longer pass the manager here!
    header = FiwareHeaderSecure(
        service="n5geh_demo",
        service_path='/'
    )

    # The Authorization field will trigger the token fetch automatically
    print(header.model_dump_json(indent=2))

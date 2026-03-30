from keycloak import KeycloakOpenID
import time


AVAILABLE_SERVICES = {
    "n5geh_demo": "GLSjpaYJy3uBc9X01E4BpVrJW4u1BcuO"
}


class KeycloakTokenManager:
    def __init__(self,
                 fiware_service: str,
                 ):
        assert fiware_service in AVAILABLE_SERVICES.keys()
        self.client = KeycloakOpenID(
                server_url="https://sso.eonerc.rwth-aachen.de",  # Remove /auth/ for newer Quarkus versions
                client_id=f"{fiware_service}-admin",
                realm_name="EBC-Dev",
                client_secret_key=AVAILABLE_SERVICES[fiware_service]  # Only if client is confidential
            )
        self._token_data = None
        self._expiry_time = 0

    def get_access_token(self):
        # Buffer of 10 seconds to account for network latency
        if not self._token_data or time.time() >= (self._expiry_time - 10):
            print("Token expired or missing. Fetching new token...")
            self._token_data = self.client.token(grant_type='client_credentials')
            # Calculate absolute expiry timestamp
            self._expiry_time = time.time() + self._token_data['expires_in']

        return self._token_data['access_token']


# TODO use FIWARE secure header
if __name__ == '__main__':
    from filip.models.base import FiwareHeaderSecure
    fiware_service = "n5geh_demo"
    manager = KeycloakTokenManager(fiware_service=fiware_service)
    header = FiwareHeaderSecure(
        service=fiware_service,
        service_path='/',
        authorization=f"Bearer {manager.get_access_token()}",
    )
    print(header.model_dump_json(indent=2))

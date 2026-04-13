import requests
import json  # Used for error handling


class SparqlResult:
    """
    A helper class to parse a raw SPARQL JSON response and
    mimic the rdflib.query.Result object's .bindings attribute.

    It is initialized with the raw JSON dictionary from the request.
    """

    def __init__(self, json_response: dict):
        """
        Initializes the result object by parsing the raw JSON response.

        Args:
            json_response (dict): The complete JSON dictionary
                                  returned from the SPARQL endpoint.
        """
        self.bindings = self._parse_bindings(json_response)

    def __len__(self):
        """Allows you to call len() on the result."""
        return len(self.bindings)

    def __iter__(self):
        """Allows you to loop over the result (e.g., for room_entry in room_results)."""
        return iter(self.bindings)

    def _parse_bindings(self, json_response: dict) -> list:
        """
        Parses the complex SPARQL JSON result into a simple
        list of dictionaries, as expected by the notebook.

        From: {'results': {'bindings': [ {'var': {'type': 'uri', 'value': '...'} } ]}}
        To:   [ {'var': '...'} ]
        """
        try:
            # Get the list of bindings from the JSON
            raw_bindings = json_response['results']['bindings']
            simplified_bindings = []

            for raw_binding in raw_bindings:
                simple_binding = {}
                # Iterate over each variable in the binding (e.g., 'room', 'sensor')
                for var_name, details in raw_binding.items():
                    # Just extract the 'value' field. This is what the
                    # notebook logic (e.g., room_entry['room']) expects.
                    simple_binding[var_name] = details.get('value', None)
                simplified_bindings.append(simple_binding)

            return simplified_bindings

        except KeyError:
            # This handles cases where the JSON is empty or not in the expected format
            # (e.g., no 'results' or 'bindings' key from an error or empty query)
            return []
        except Exception as e:
            print(f"  -> Error parsing SPARQL bindings: {e}")
            return []


class SparqlApiClient:
    """
    A client to interact with an RDF4J REST API endpoint
    using the 'requests' library.
    """

    def __init__(self, endpoint_url: str, credential_path: str = None):
        """
        Initializes the client.

        Args:
            endpoint_url (str): The full URL to the repository.
                e.g., "http://.../repositories/MyRepo"
        """
        if not endpoint_url or not endpoint_url.startswith("http"):
            raise ValueError("A valid HTTP/HTTPS endpoint_url is required.")

        if credential_path:
            # read username and password from the json file
            with open(credential_path, 'r') as cred_file:
                credentials = json.load(cred_file)
                self.username = credentials.get('username', None)
                self.password = credentials.get('password', None)
        else:
            self.username = None
            self.password = None


        # set basic auth if credentials are provided
        if self.username and self.password:
            self.auth = (self.username, self.password)
        else:
            self.auth = None

        # bind the auth with requests session
        self.session = requests.Session()
        if self.auth:
            self.session.auth = self.auth

        self.endpoint_url = endpoint_url

        # Set the headers as per the example
        self.headers = {
            'Content-Type': 'application/sparql-query',
            'Accept': 'application/sparql-results+json'
        }

        print(f"SparqlApiClient (requests-based) initialized. Pointing to: {self.endpoint_url}")

    def query(self, query_string: str):
        """
        Executes a SPARQL SELECT query against the remote endpoint.

        Args:
            query_string (str): The SPARQL query to execute.

        Returns:
            A SparqlResult object, which contains the parsed bindings.
        """
        try:
            # Use POST, sending the query string as the payload (data)
            response = self.session.request("POST",
                                        self.endpoint_url,
                                        headers=self.headers,
                                        data=query_string)

            # Check for HTTP errors (e.g., 404, 500)
            response.raise_for_status()

            # Parse the JSON response
            json_data = response.json()

            # Pass the raw JSON to the SparqlResult class for parsing
            return SparqlResult(json_data)

        except requests.exceptions.HTTPError as http_err:
            print(f"  -> HTTP Error: {http_err}")
            print(f"  -> Response Text: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"  -> Connection Error: {conn_err}")
            print(f"  -> Is the endpoint '{self.endpoint_url}' correct and running?")
        except json.JSONDecodeError:
            print("  -> Failed to decode JSON from response.")
            print(f"  -> Response Text: {response.text}")
        except Exception as e:
            print(f"  -> An unexpected error occurred: {e}")

        # If any error occurs, return an empty result
        # by passing an empty dict to the constructor.
        return SparqlResult({})


if __name__ == '__main__':
    graphdb_url = "http://137.226.248.187:7200/repositories/InteroperabilityWorkshop"
    client = SparqlApiClient(endpoint_url=graphdb_url)
    test_query = """
    PREFIX rec: <https://w3id.org/rec#>
    SELECT DISTINCT ?room
    WHERE {
        ?room a rec:Room
    }
    """
    results = client.query(test_query)
    print(f"Number of rooms found: {len(results)}")
    for room_entry in results:
        print(f"  Room URI: {room_entry['room']}")
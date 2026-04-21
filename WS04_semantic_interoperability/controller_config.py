import yaml
from rdf4j_client import SparqlApiClient

# SPARQL queries (with <room_uri> placeholders that we'll fill in via Python string
# formatting)
query_rooms = """
    PREFIX rec: <https://w3id.org/rec#>
    SELECT DISTINCT ?room
    WHERE {
        ?room a rec:Room
    }
"""

query_ventilation_devices = """
    PREFIX rec:    <https://w3id.org/rec#>
    PREFIX brick:  <https://brickschema.org/schema/Brick#>
    PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?device ?actuation ?actuation_access
    WHERE {
      <room_uri> a rec:Room .

      ?device a brick:Air_System .
      ?actuation brick:isPointOf ?device .

      OPTIONAL {
        ?actuation a ?actuation_type ;
                   rdf:value ?actuation_access .
        VALUES ?actuation_type { brick:Setpoint brick:Command }
      }

      ?actuation (brick:isPointOf|brick:hasLocation|brick:isPartOf)* <room_uri> .
    }
"""

query_co2_sensor_availability = """
    PREFIX rec: <https://w3id.org/rec#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?sensor ?sensor_access
    WHERE {
        <room_uri> a rec:Room .
        ?sensor a brick:CO2_Sensor . 
        ?sensor rdf:value ?sensor_access .                                                
        ?sensor (brick:isPointOf|brick:hasLocation|brick:isPartOf)* <room_uri>.
    }
"""

query_presence_sensor_availability = """
    PREFIX rec: <https://w3id.org/rec#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?sensor ?sensor_access
    WHERE {
        <room_uri> a rec:Room .
        ?sensor a brick:Occupancy_Count_Sensor .
        ?sensor rdf:value ?sensor_access .
        ?sensor (brick:isPointOf|brick:hasLocation|brick:isPartOf)* <room_uri>.
    }
"""

class ControllerConfiguration:
    def __init__(self,
                 api_client: SparqlApiClient
                 ):
        """
        Initialize the Controller configuration class using an active API client.

        Args:
            api_client (SparqlApiClient): An initialized client pointing to a SPARQL endpoint.
        """
        self.client = api_client  # Use the passed-in client

    def generate_configuration(self):
        """
        Main logic:
          1. Fetch all rooms from the remote endpoint.
          2. For each room, check if it has ventilation devices.
          3. If yes, check for CO2 sensors, otherwise presence sensors,
             otherwise use timetable-based control.
          4. Assemble the configuration data structure.
        """
        configuration_list = []

        print("\n--- Starting Configuration Generation ---")
        # Use our client to query the remote graph
        room_results = self.client.query(query_rooms)

        if not room_results:
            print("Query for rooms failed. Aborting.")
            return

        # We can still iterate over the result, as our class has __iter__
        room_list = list(room_results)
        print(f"Found {len(room_list)} rooms. Processing...")

        for room_entry in room_list:
            # room_entry is a simple dict like {'room': 'http://...'}
            room_uri = room_entry['room']
            print(f"\nProcessing Room: {room_uri.split('#')[-1]}")

            # 1) Find ventilation devices for current room
            devices_query = query_ventilation_devices.replace("<room_uri>", f"<{room_uri}>")
            device_results = self.client.query(devices_query)

            # We can still check .bindings, as our class sets this attribute
            if not device_results or not device_results.bindings:
                print("  -> No ventilation devices found. Skipping room.")
                continue

            # For simplicity, we take the first device's actuation_access found
            actuation_access = device_results.bindings[0].get('actuation_access', None)
            if not actuation_access:
                print("  -> Found ventilation device, but no Setpoint/Command access point. Skipping room.")
                continue

            print(f"  -> Found Actuator: {actuation_access}")

            # 2) Determine control logic based on sensors
            #    a) Check CO2 sensor
            co2_query = query_co2_sensor_availability.replace("<room_uri>", f"<{room_uri}>")
            co2_sensors = self.client.query(co2_query)

            if co2_sensors and co2_sensors.bindings:
                # If found CO2 sensor(s), pick the first for demonstration
                sensor_access = co2_sensors.bindings[0].get('sensor_access', None)
                controller_mode = "co2"
                print(f"  -> Found CO2 Sensor: {sensor_access}")

            else:
                # b) Check presence sensor
                presence_query = query_presence_sensor_availability.replace("<room_uri>", f"<{room_uri}>")
                presence_sensors = self.client.query(presence_query)

                if presence_sensors and presence_sensors.bindings:
                    # Pick the first presence sensor
                    sensor_access = presence_sensors.bindings[0].get('sensor_access', None)
                    controller_mode = "presence"
                    print(f"  -> No CO2 sensor. Found Presence Sensor: {sensor_access}")
                else:
                    # c) Fall back to timetable-based control
                    sensor_access = None
                    controller_mode = "timetable"
                    print("  -> No CO2 or Presence sensor. Defaulting to 'timetable' mode.")

            # 3) Build one configuration entry per room
            config_entry = {
                "controller_function": "Ventilation",
                "controller_mode": controller_mode,
                "inputs": {
                    "sensor_access": str(sensor_access) if sensor_access else "None"
                },
                "outputs": {
                    "actuation_access": str(actuation_access) if actuation_access else "None"
                }
            }
            configuration_list.append(config_entry)
        return configuration_list


if __name__ == '__main__':
    graphdb_url = "http://137.226.248.187:7200/repositories/InteroperabilityWorkshop"
    query_client = SparqlApiClient(endpoint_url=graphdb_url)

    configurator = ControllerConfiguration(
        api_client=query_client,
    )
    configuration = configurator.generate_configuration()
    # View the generated configuration
    print(f"\n--- Generation Complete ---")
    print(f"Configuration for {len(configuration)} controllers:")
    print(yaml.dump(configuration, sort_keys=False))
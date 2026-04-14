from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion


class N5gehMQTTClient:
    def __init__(self, host:str=None, port:int=None, username:str=None, password:str=None):
        self.client = Client(
            callback_api_version=CallbackAPIVersion.VERSION2)
        if host is None:
            self.host = "mqtt.n5geh.eonerc.rwth-aachen.de"
        else:
            self.host = host
        if port is None:
            self.port = 8883
        else:
            self.port = port
        if username is not None and password is not None:
            self.client.username_pw_set(username=username, password=password)
        else:
            self.client.username_pw_set(
                username="n5geh_demo",
                password="n5geh_demo")
        self.setup()

    def setup(self):
        self.client.tls_set()
        self.client.connect(
            host=self.host,
            port=self.port,
        )
        self.client.loop_start()

    def publish(self, topic:str, msg:str):
        self.client.publish(
            topic=topic,
            payload=msg,
        )
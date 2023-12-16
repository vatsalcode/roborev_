from confluent_kafka import Producer
from configparser import ConfigParser
import json

config_parser = ConfigParser()
config_parser.read('config.ini')
config = dict(config_parser['default'])

def sendToKafka(topic,keyId,info):
    producer = Producer(config)
    producer.produce(topic, key=json.dumps(keyId), value=json.dumps(info))
    producer.flush()

keyId = {"task_id": 4}
info = {
  "task_id": 4,
  "taskname": "collect",
  "start_timestamp": 1702641600000000,
  "end_timestamp": 1702679400000000,
  "current_status": "In Progress",
  "robot_id": 3
}
sendToKafka("roborev.tracking.taskworkinginfo",keyId,info)

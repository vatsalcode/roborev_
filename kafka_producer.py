from confluent_kafka import Producer
from configparser import ConfigParser
import json

config_parser = ConfigParser()
config_parser.read('config.ini')
config = dict(config_parser['default'])

def produce_kafka_message(topic,keyId,info):
    producer = Producer(config)
    producer.produce(topic, key=str(keyId), value=json.dumps(info))
    producer.flush()

# keyId = {"task_id": 4}
# info = {
#   "task_id": 4,
#   "taskname": "collect",
#   "start_timestamp": 1702641600000000,
#   "end_timestamp": 1702679400000000,
#   "current_status": "In Progress",
#   "robot_id": 3
# }

# robot_info = {
#   "robot_id": "1",
#   "robot_name": "Frank",
#   "status": "Available"
# }
# produce_kafka_message("update_robot",robot_info['robot_id'],robot_info)

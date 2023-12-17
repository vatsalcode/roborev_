from confluent_kafka import Consumer
from configparser import ConfigParser

config_parser = ConfigParser()
config_parser.read('config.ini')
config = dict(config_parser['default'])
config.update(config_parser['consumer'])   

#"roborev.tracking.robotinfo"
def get_data_from_kafka_topic(topic):
    consumer = Consumer(config)
    consumer.subscribe([topic])

    msg_list = []

    try:
        while True:
            msg = consumer.poll(1.0)
            # print(f'msg: {msg}')
            if msg is not None and msg.error() is None:
                # print("key = {key:12} value = {value:12}".format(key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))
                msg_list.append(msg)
            
            if len(msg_list) >=3:
                return msg_list
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

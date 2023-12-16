from flask import Flask, request, jsonify
from confluent_kafka import Producer
from datetime import datetime
import kafka_consumer

app = Flask(__name__)
IN_PROGRESS = 'In Progress'

# Kafka configuration
KAFKA_BROKER = 'your_kafka_broker_address'
KAFKA_TOPIC_ROBOT = 'roborev.tracking.robotinf'
KAFKA_TOPIC_TASK = 'roborev.tracking.taskworkinginfo'


## todo: This portion is a DUMMY version
# Function to produce messages to Kafka
def produce_kafka_message(topic, message):
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    producer.produce(topic, value=message)
    producer.flush()

# Function to check if a robot is available
def is_robot_available(robot_name):
    # 
    # replace this with actual logic to check robot availability
    return True


# Flask route to receive JSON data and process the task
@app.route('/process_task', methods=['POST'])
def process_task():
    try:
        data = request.get_json()

        # Extract data from JSON
        task_name = data['task_name']
        start_timestamp = data['start_timestamp']
        end_timestamp = data['end_timestamp']
        robot_name = data['robot_name']

        #get data from kafka topic "robot"

        # Check if the robot is available
        if is_robot_available(robot_name):
            # Assign the task to the robot
            task_message = {
                'task_name': task_name,
                'start_timestamp': start_timestamp,
                'end_timestamp': end_timestamp,
                'robot_name': robot_name,
                'current_status': IN_PROGRESS,
            }

            # Send a post request to Kafka topic "task"
            produce_kafka_message(KAFKA_TOPIC_TASK, task_message)

            #Send a post request to Kafka topic "robot" to update the robot status to busy
            produce_kafka_message(KAFKA_TOPIC_TASK, task_message)

            return jsonify({'message': 'Task assigned to the robot successfully.'})
        else:
            return jsonify({'message': 'Robot is busy.'})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

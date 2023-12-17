from flask import Flask, request, jsonify
from datetime import datetime
import kafka_consumer
import kafka_producer
import random
import time
import psycopg2
from psycopg2 import sql

app = Flask(__name__)
ASSIGNED = 'Assigned'

# Kafka configuration
KAFKA_SOURCE_TOPIC_ROBOT = 'roborev.tracking.robotinf'
KAFKA_SOURCE_TOPIC_TASK = 'roborev.tracking.taskworkinginfo'
BUSY_STATUS = 'Busy'
AVAILABLE_STATUS = 'Available'
robot_mapping = {
    1: 'Frank',
    2: 'Swayer',
    3: 'Panda'
}

# Connection parameters
db_params = {
    "host": "34.68.22.210",
    "database": "roborev",
    "user": "roboadmin",
    "password": "admin",
}
def generate_unique_id():
    # Generate a random 4-digit integer ID
    unique_id = random.randint(1000, 9999)
    return unique_id

def current_milli_time():
    return round(time.time() * 1000)

def update_table(db_params, query, data):
    try:
        # Establish a connection to the database
        connection = psycopg2.connect(**db_params)

        # Create a cursor object
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query, data)

        # Commit the transaction
        connection.commit()

        print("Data inserted successfully!")

    except psycopg2.Error as e:
        print("Error: Unable to insert data into the table")
        print(e)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
def is_task_done():
    task_list = kafka_consumer.get_data_from_kafka_topic(KAFKA_SOURCE_TOPIC_TASK)

    t = task_list[-1] #last task currently in topic
                
    t_value = t.value().decode('utf-8')

    current_time = current_milli_time()
    if t_value['end_timestamp'] <  current_time:
        robot_name = robot_mapping[t_value['robot_id']]

        updated_robot_info = {
            'robot_id':t_value['robot_id'],
            'robot_name': robot_name,
            'status' : AVAILABLE_STATUS 
            }

        update_query = sql.SQL("""
            UPDATE tracking.robotinfo
            SET status = %(status)s
            WHERE robot_id = %(robot_id)s
            """)
        
        update_table(db_params,update_query,updated_robot_info)
        #update the robot status to available
        # kafka_producer.produce_kafka_message(KAFKA_SOURCE_TOPIC_ROBOT,updated_robot_info['robot_id'], updated_robot_info)

        return 1
    
    return 0


# Function to check if a robot is available using kafka topic
def is_robot_available(robot_name):
    # 
    msg_list = kafka_consumer.get_data_from_kafka_topic(KAFKA_SOURCE_TOPIC_ROBOT)
    
    for obj in msg_list:
        value = obj.value().decode('utf-8')

        if value['robot_name'] == robot_name:
            if value['status'] == AVAILABLE_STATUS:
                return True, value
            elif value['status'] == BUSY_STATUS:
                flag = is_task_done()

                if flag ==1:
                    return True, value
                     
    return False,value


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

        task_id = generate_unique_id()

        #get data from kafka topic "robot"

        is_available, robot_info = is_robot_available(robot_name)

        # Check if the robot is available
        if is_available(robot_name):
            # Assign the task to the robot
            task_message = {
                'task_id':task_id,
                'task_name': task_name,
                'start_timestamp': start_timestamp,
                'end_timestamp': end_timestamp,
                'robot_name': robot_name,
                'current_status': ASSIGNED,
            }

            #set the robot status to busy
            robot_info['status'] = BUSY_STATUS

            # PostgreSQL query to insert data in task
            task_insert_query = sql.SQL("""
            INSERT INTO tracking.taskworkinginfo (
                task_id, taskname, start_timestamp, end_timestamp, current_status, robot_id
            ) VALUES (
                %(task_id)s, %(taskname)s, %(start_timestamp)s, %(end_timestamp)s, %(current_status)s, %(robot_id)s
            )
            """)

            update_query = sql.SQL("""
            UPDATE tracking.robotinfo
            SET status = %(status)s
            WHERE robot_id = %(robot_id)s
            """)

            update_table(db_params, task_insert_query, task_message)

            update_table(db_params,update_query,robot_info)

            # Send a post request to Kafka topic "task"
            # kafka_producer.produce_kafka_message(KAFKA_SOURCE_TOPIC_TASK,task_id, task_message)

            #Send a post request to Kafka topic "robot" to update the robot status to busy
            # kafka_producer.produce_kafka_message(KAFKA_SOURCE_TOPIC_ROBOT,robot_info['robot_id'], robot_info)

            return jsonify({'message': 'Task assigned to the robot: {robot_name} successfully.'})
        else:
            return jsonify({'message': 'Robot: {robot_name} is busy.'})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



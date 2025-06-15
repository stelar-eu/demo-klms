# 
# A simple tool that can be used to perform basic testing of tool execution
#
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import minio
import requests


def run(*, input={}, minio={}, output={}, parameters={}, signature_verified=False):
    # This function simulates a task execution based on the provided arguments.
    # It can be replaced with any logic that processes the arguments.
    logging.info("Running task with inputs: %s", input)
    logging.info("MinIO Endpoint: %s", minio['endpoint_url'])
    logging.info("MinIO Access Key: %s", minio['id'])
    logging.info("MinIO Secret Key: %s", minio['key'])
    logging.info("MinIO Session Key: <hidden> exists=%s", "skey" in minio)

    logging.info("Executing task with outputs: %s", output)
    logging.info("Execution with parameters: %s", parameters)
    logging.info("Signature verified: %s", signature_verified)

    # Create metrics and outputs as directed from parameters
    metrics = parameters.get("report_metrics", {})
    outputs = {}

    for oname, ourl in output.items():
        logging.info("Output %s will be stored at %s", oname, ourl)
        outputs[oname] = ourl

    return {
        'metrics': metrics,
        'output': outputs,
        'message': 'Task executed successfully, all parameters processed.',
        'status': 'succeeded',
    }

if __name__ == "__main__":
    # Get the four command line arguments
    import sys

    logging.error("Logging this message to stderr")
    print("Printing this message to stderr", file=sys.stderr)
    logging.info("Starting simple_tool.py")
    print("Starting simple_tool.py", flush=True)
    # Check if the correct number of arguments is provided

    if len(sys.argv) != 5:
        print("Usage: simple_tool.py <token> <endpoint> <taskid> <signature>")
        sys.exit(1)
    
    args = list(sys.argv)
    args[1] = "<token redacted>"

    logging.info("Arguments received: %s", sys.argv)

    token, endpoint, taskid, signature = sys.argv[1:5]

    response = requests.get(f"{endpoint}api/v2/task/{taskid}/{signature}/input", 
                            headers={'Authorization': token})
    try:
        response.raise_for_status()  # Raise an error for bad responses
    except Exception as e:
        print(f"Error fetching task input: {e}")
        logging.error("Error fetching task input: %s", e)
        logging.error("Sleeping for 10000 seconds")
        time.sleep(10000)  # Wait for a second before retrying
        logging.error("Continuing after 10000 seconds")


    if not response.json()['success']:
        logging.error("Error: Task not found or not successful.")
        print(response.json(), file=sys.stderr)
        logging.error("Exiting with status code 1")
        sys.exit(1)

    taskargs = response.json()['result']

    try:
        # Execute and get the exit data
        exit_data = run(** taskargs)
        exit_data = {
            'message': 'Task completed successfully', 
            'status': 'succeeded', 
            'output':{}, 
            'metrics': {}} | (exit_data if exit_data else {})
        
    except Exception as e:
        logging.exception("Exception thrown during task execution")
        exit_data = {'message': str(e), 'status': 'failed'}

    requests.post(
        f"{endpoint}api/v2/task/{taskid}/{signature}/output",
        json=exit_data,
        headers={'Authorization': token}
    ).raise_for_status()  # Raise an error for bad responses

    logging.info("Task output posted successfully: %s", exit_data)

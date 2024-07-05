import zmq
import time
import pandas as pd

#The path to the CSV file is specified, and the file is read into a DataFrame using pandas.
csv_file_path = "cordinats data.csv"
df = pd.read_csv(csv_file_path)

# Initialize ZeroMQ context and socket for publishing
# A ZeroMQ context and a publishing socket (zmq.PUB) are created.
# The socket is bound to the TCP port 1132, meaning it will listen for subscribers on this port.

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind('tcp://*:1132')

# Group the DataFrame rows based on the TIME column
# Grouping data by TIME allows you to logically segment the data.
# Each group represents a unique time period, making it easier to manage and analyze data related to specific times.
groups = df.groupby('TIME')

# Infinite loop to continuously publish the data
while True:
    # Iterate over the groups and publish the data
    for time_value, group_df in groups:
        # he group DataFrame (group_df) is converted to a CSV string format.
        group_csv_data = group_df.to_csv(index=False)
        # A message is created combining the TIME value and the CSV data of the group.
        message = f'{time_value} {group_csv_data}'
        print(message)
        # The message is sent via the ZeroMQ publishing socket.
        pub_socket.send_string(message)

        # Add some delay
        time.sleep(1)

    # Reset the DataFrame iterator when reaching the end
    groups = df.groupby('TIME')

# Close the ZeroMQ socket and context
# These lines are intended to close the ZeroMQ socket and terminate the context, but they are not reached due to the infinite loop.
# If the loop were to be interrupted (e.g., via a keyboard interrupt), these lines would clean up the resources.
pub_socket.close()
context.term()

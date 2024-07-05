**ZMQ Publisher-Subscriber for Real-time Data Visualization in QGIS**

This project demonstrates a system for visualizing real-time data updates in QGIS using ZeroMQ for communication.

ZeroMQ is a high-performance messaging library that enables efficient communication between applications. In this project, it facilitates the real-time exchange of data between the publisher and subscriber.

How it works:
Publisher: The publisher script continuously sends data segments (grouped by time) from a CSV file as messages over a ZeroMQ socket (TCP port 1132).
Subscriber: The subscriber script receives these messages, extracts the relevant information (time and CSV data), and processes it further.

QGIS is a free and open-source Geographic Information System (GIS) software. In this project, QGIS provides the platform for visualizing the real-time data updates.

How it works: The subscriber script dynamically creates and updates a point layer within QGIS based on the extracted data (latitude, longitude, identity, and time). This layer represents the real-time data points on the map canvas.

**Functionality**

* The publisher continuously reads data (grouped by time) from a CSV file (`cordinats data.csv`).
* The publisher sends the grouped data (time and CSV string) as messages over a ZeroMQ socket (TCP port 1132).
* The subscriber receives the messages, parses the data (extracts time and CSV data), and converts the CSV data into a pandas DataFrame.
* The subscriber extracts relevant information (latitude, longitude, identity, and time) from the DataFrame.
* The subscriber plots the extracted points as a new point layer in QGIS.
* The QGIS map canvas is refreshed to display the updated point layer.

**Requirements**

* Python 3.x
* ZeroMQ library (`pip install pyzmq`)
* pandas library (`pip install pandas`)
* PyQt5 (`pip install PyQt5`)
* QGIS 3.x ([https://qgis.org/en/site/forusers/download.html](https://qgis.org/en/site/forusers/download.html))

**Running the Project**

1. Ensure you have the required libraries installed.
2. Replace `"shapefile.shp"` with the path to your desired background shapefile.
3. Modify `"cordinats data.csv"` if your CSV file has a different name or location.
4. Run the `ZMQ_PUBLISHER.py` script to start the publisher.
5. Run the `ZMQ_SUBSCRIBER.py` script to start the subscriber and QGIS visualization.

**Notes**

* The `ZMQ_PUBLISHER.py` script runs continuously due to the infinite loop. Terminate it manually (e.g., Ctrl+C) when finished.
* The subscriber script uses a timer to update the QGIS map canvas every second. Adjust the timer interval (`timer.start(1000)`) as needed.

This project provides a basic example of using ZeroMQ for real-time data communication and visualization in QGIS. You can extend it to suit your specific data format, visualization requirements, and communication needs.

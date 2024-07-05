import zmq  # Import ZeroMQ for message passing
from qgis.PyQt.QtWidgets import QApplication  # Import QApplication for GUI application management
from qgis.core import QgsApplication, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField, QgsFields, QgsMessageLog, Qgis  # Import core QGIS classes and functions
from qgis.gui import QgsMapCanvas  # Import QgsMapCanvas for displaying map layers
from qgis.PyQt.QtCore import Qt, QTimer, QVariant  # Import Qt for various Qt constants and QTimer for creating timers
import pandas as pd  # Import pandas for data manipulation
import io  # Import io for handling input/output operations
import sys  # Import sys for system-specific parameters and functions


"""The plot_points function is essential for updating the point layer with new data received from the ZeroMQ socket, 
and the update_canvas function ensures that the canvas is refreshed to display these updates.
"""

def plot_points(random_points, point_layer, canvas):
    """
    Plot points on the given point layer in the QGIS map canvas.

    This function performs the following steps:
    1. Initializes an empty list to store features.
    2. Loops through each coordinate tuple in random_points.
    3. Creates a new feature with the same fields as the point_layer.
    4. Sets the 'Longitude', 'Latitude', 'Identity', and 'Time' attributes of the feature.
    5. Creates a point geometry from the coordinates and assigns it to the feature.
    6. Appends the feature to the list.
    7. Adds all features to the point_layer.

    Parameters:
    random_points (list of tuples): A list of tuples, each containing longitude, latitude, identity, and time information.
    point_layer (QgsVectorLayer): The point layer to update with new features.
    canvas (QgsMapCanvas): The map canvas to refresh after updating the point layer.
    """
    # Initialize an empty list to store features
    feats = []
    # Loop through each coordinate tuple in random_points
    # This line starts a loop that iterates over each tuple in the random_points list. Each tuple contains four elements: longitude, latitude, identity, and time.
    for coords in random_points:
        # Create a new feature with the same fields as point_layer
        #This ensures that the new feature will have the same attribute structure as the layer.
        feat = QgsFeature(point_layer.fields())
        # These lines set the values of the 'Longitude', 'Latitude', 'Identity', and 'Time' attributes of the feature using the corresponding elements from the coords tuple.
        # Set the 'Longitude' attribute of the feature
        feat.setAttribute('Longitude', coords[0])
        # Set the 'Latitude' attribute of the feature
        feat.setAttribute('Latitude', coords[1])
        # Set the 'Identity' attribute of the feature
        feat.setAttribute('Identity', coords[2])
        # Set the 'Time' attribute of the feature
        feat.setAttribute('Time', coords[3])
        # Create a point geometry from the coordinates and set it for the feature
        # These lines create a QgsGeometry object representing a point using the longitude and latitude values from the coords tuple.
        # The geometry is then assigned to the feature.
        point = QgsGeometry.fromPointXY(QgsPointXY(coords[0], coords[1]))
        feat.setGeometry(point)
        # Append the feature to the list
        feats.append(feat)
    # Add the features to the point_layer
    point_layer.dataProvider().addFeatures(feats)

def update_canvas(point_layer, canvas):
    """
    Update the QGIS map canvas with new points received via a ZeroMQ socket.

    This function performs the following steps:
    1. Deletes all existing features from the specified point layer.
    2. Receives a new message from a ZeroMQ socket.
    3. Parses the received message to extract the timestamp and CSV data.
    4. Reads the CSV data into a pandas DataFrame.
    5. Extracts latitude, longitude, identity, and time information from the DataFrame.
    6. Plots the new points on the specified point layer.
    7. Refreshes the map canvas to reflect the updates.

    Parameters:
    point_layer (QgsVectorLayer): The point layer to update with new features.
    canvas (QgsMapCanvas): The map canvas to refresh after updating the point layer.
    """
    # Retrieve and store the IDs of all features in point_layer
    feature_ids = [feature.id() for feature in point_layer.getFeatures()]
    # Delete all features in point_layer using their IDs
    point_layer.dataProvider().deleteFeatures(feature_ids)
    # Receive a message from the ZeroMQ socket
    message = socket.recv_string()
    print(message)
    # Split the message into time_value and group_csv_data
    time_value, group_csv_data = message.split(' ', 1)
    # Read the CSV data into a DataFrame
    df = pd.read_csv(io.StringIO(group_csv_data))
    # Extract latitude, longitude, identity, and time from each row in the DataFrame
    random_points = [(row['long'], row['lat'], row['Identity'], row['TIME']) for _, row in df.iterrows()]
    # Plot the new points on the point_layer
    plot_points(random_points, point_layer, canvas)
    # Refresh the map canvas to display the changes
    canvas.refresh()

if __name__ == '__main__':
    # Create a ZeroMQ context
    context = zmq.Context()
    # Create a ZeroMQ subscriber socket
    socket = context.socket(zmq.SUB)
    # Connect the socket to the publisher at localhost on port 1132
    socket.connect("tcp://localhost:1132")
    # Subscribe to all messages (empty string subscription)
    socket.subscribe(b"")

    # Set the QGIS application prefix path and initialize QGIS
    QgsApplication.setPrefixPath('/usr', True)
    app = QApplication(sys.argv)
    QgsApplication.initQgis()

    # Create and set up the map canvas
    canvas = QgsMapCanvas()
    canvas.setCanvasColor(Qt.black)
    canvas.show()

    # Load an example vector layer from a shapefile
    layer_path = "C:/Users/uzair/Downloads/7424/POCs Demo/shapefiles/Map_real_poc.shp"
    vlayer = QgsVectorLayer(layer_path, "Shape File", "ogr")
    # Set the color of the vector layer to green
    vlayer.renderer().symbol().setColor(Qt.green)

    point_layer = QgsVectorLayer("Point?crs=epsg:4326&field=Identity:int&field=Longitude:double&field=Latitude:double&field=Time:int&index=yes", "Moving Points", "memory")
    # # Set the color of the point layer to red
    point_layer.renderer().symbol().setColor(Qt.red)
    point_layer.updateFields()

    # Set the canvas extent to the extent of the vector layer
    canvas.setExtent(vlayer.extent())
    # Set the map canvas layer set to include the vector and point layers
    canvas.setLayers([vlayer, point_layer])
    canvas.refresh()

    # Create a QTimer to trigger the canvas update every 1 second
    timer = QTimer()
    timer.timeout.connect(lambda: update_canvas(point_layer, canvas))
    timer.start(1000)  # Set the timer to trigger every 1000 milliseconds (1 second)

    # Start the application event loop
    sys.exit(app.exec_())

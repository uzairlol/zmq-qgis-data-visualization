Sure! Here is a detailed README file for your ZMQ publisher and subscriber code:

---

# ZMQ Publisher and Subscriber with QGIS Integration

This repository contains example code for a ZeroMQ (ZMQ) publisher and subscriber, with the subscriber visualizing data points on a QGIS map canvas.

## Files

- `publisher.py`: The publisher script that reads data from a CSV file and publishes it via ZeroMQ.
- `subscriber.py`: The subscriber script that receives data from the publisher, parses it, and visualizes it on a QGIS map canvas.

## Requirements

- Python
- ZeroMQ (`pyzmq` package)
- Pandas
- QGIS with Python bindings (`qgis` package)
- PyQt5

## Installation

1. **Install Python packages**:
   ```sh
   pip install pyzmq pandas pyqt5
   ```

2. **Install QGIS**:
   Follow the instructions on the [QGIS download page](https://qgis.org/en/site/forusers/download.html) to install QGIS on your system.

## Usage

### Publisher

1. **Set the path to your CSV file** in `publisher.py`:
   ```python
   csv_file_path = "selected_rows.csv"
   ```

2. **Run the publisher**:
   ```sh
   python publisher.py
   ```

### Subscriber

1. **Set the path to your shapefile** in `subscriber.py`:
   ```python
   layer_path = "shapefiles.shp"
   ```

2. **Run the subscriber**:
   ```sh
   python subscriber.py
   ```

### Example Publisher Code (`publisher.py`)
```python
import zmq
import time
import pandas as pd

csv_file_path = "selected_rows.csv"
df = pd.read_csv(csv_file_path)

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind('tcp://*:1132')

groups = df.groupby('TIME')

while True:
    for time_value, group_df in groups:
        group_csv_data = group_df.to_csv(index=False)
        message = f'{time_value} {group_csv_data}'
        print(message)
        pub_socket.send_string(message)
        time.sleep(1)

    groups = df.groupby('TIME')

pub_socket.close()
context.term()
```

### Example Subscriber Code (`subscriber.py`)
```python
import zmq
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsApplication, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField, QgsFields, QgsMessageLog, Qgis
from qgis.gui import QgsMapCanvas
from qgis.PyQt.QtCore import Qt, QTimer, QVariant
import pandas as pd
import io
import sys

def plot_points(random_points, point_layer, canvas):
    feats = []
    for coords in random_points:
        feat = QgsFeature(point_layer.fields())
        feat.setAttribute('Longitude', coords[0])
        feat.setAttribute('Latitude', coords[1])
        feat.setAttribute('Identity', coords[2])
        feat.setAttribute('Time', coords[3])
        point = QgsGeometry.fromPointXY(QgsPointXY(coords[0], coords[1]))
        feat.setGeometry(point)
        feats.append(feat)
    point_layer.dataProvider().addFeatures(feats)

def update_canvas(point_layer, canvas):
    feature_ids = [feature.id() for feature in point_layer.getFeatures()]
    point_layer.dataProvider().deleteFeatures(feature_ids)
    message = socket.recv_string()
    print(message)
    time_value, group_csv_data = message.split(' ', 1)
    df = pd.read_csv(io.StringIO(group_csv_data))
    random_points = [(row['long'], row['lat'], row['Identity'], row['TIME']) for _, row in df.iterrows()]
    plot_points(random_points, point_layer, canvas)
    canvas.refresh()

if __name__ == '__main__':
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:1132")
    socket.subscribe(b"")

    QgsApplication.setPrefixPath('/usr', True)
    app = QApplication(sys.argv)
    QgsApplication.initQgis()

    canvas = QgsMapCanvas()
    canvas.setCanvasColor(Qt.black)
    canvas.show()

    layer_path = "shapefiles.shp"
    vlayer = QgsVectorLayer(layer_path, "Shape File", "ogr")
    vlayer.renderer().symbol().setColor(Qt.green)

    point_layer = QgsVectorLayer("Point?crs=epsg:4326&field=Identity:int&field=Longitude:double&field=Latitude:double&field=Time:int&index=yes", "Moving Points", "memory")
    point_layer.renderer().symbol().setColor(Qt.red)
    point_layer.updateFields()

    canvas.setExtent(vlayer.extent())
    canvas.setLayers([vlayer, point_layer])
    canvas.refresh()

    timer = QTimer()
    timer.timeout.connect(lambda: update_canvas(point_layer, canvas))
    timer.start(1000)

    sys.exit(app.exec_())
`''

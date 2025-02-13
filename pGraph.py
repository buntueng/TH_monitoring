import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mariadb
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

ticker.Locator.MAXTICKS = 2000  # Increase the limit

# Database Configuration
DB_CONFIG = {
    "user": "rpscada",
    "password": "0820216694",
    "host": "localhost",
    "database": "sensor_databases"
}

temperature_nodes = ['Airflow', 'Cooler_Ambient', 'Cooler_Discharge']
humidity_nodes = ['Airflow', 'Cooler_Ambient', 'Cooler_Discharge']

# Connect to MariaDB
def connect_database():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error connecting to database: {e}")
        sys.exit(1)

# Fetch the last record for each sensor type
def fetch_data():
    conn = connect_database()
    cursor = conn.cursor()
    
    humidity_data = []
    temperature_data = []

    for node in humidity_nodes:
        sql_cmd = "SELECT dTime, humidity FROM humidity WHERE node = '" + node + "' ORDER BY dTime DESC LIMIT 1"
        cursor.execute(sql_cmd)
        data = cursor.fetchone()
        if data is None:
            continue
        else:
            # convert datetime to int
            # humidity_data.append(int(time.mktime(data[0].timetuple())))
            humidity_data.append(data[0])
            humidity_data.append(data[1])

    for node in temperature_nodes:
        sql_cmd = "SELECT dTime, temperature FROM temperature WHERE node = '" + node + "' ORDER BY dTime DESC LIMIT 1"
        cursor.execute(sql_cmd)
        data = cursor.fetchone()
        if data is None:
            continue
        else:
            # convert datetime to int
            temperature_data.append(data[0])
            temperature_data.append(data[1])
    conn.close()
    
    return humidity_data, temperature_data

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Temperature and Humidity Plotter")
        # Data initialization
        self.temperature1 = []
        self.temperature2 = []
        self.temperature3 = []
        self.temperature1_time = []
        self.temperature2_time = []
        self.temperature3_time = []
        
        self.humidity1 = []
        self.humidity2 = []
        self.humidity3 = []
        self.humidity1_time = []
        self.humidity2_time = []
        self.humidity3_time = []

        # Create Matplotlib figures and canvases
        self.fig_temp = Figure()
        self.canvas_temp = FigureCanvas(self.fig_temp)
        self.ax_temp = self.fig_temp.add_subplot(111)

        self.fig_humidity = Figure()
        self.canvas_humidity = FigureCanvas(self.fig_humidity)
        self.ax_humidity = self.fig_humidity.add_subplot(111)


        # Layout
        v_layout = QVBoxLayout()

        temp_layout = QVBoxLayout()
        temp_layout.addWidget(self.canvas_temp)

        humidity_layout = QVBoxLayout()
        humidity_layout.addWidget(self.canvas_humidity)

        v_layout.addLayout(temp_layout)
        v_layout.addLayout(humidity_layout)

        self.setLayout(v_layout)

        # Initialize plots
        self.line_temp1, = self.ax_temp.plot([], [], label='Airflow')
        self.line_temp2, = self.ax_temp.plot([], [], label='Cooler-Ambient')
        self.line_temp3, = self.ax_temp.plot([], [], label='Cooler-Discharge')


        self.line_humidity1, = self.ax_humidity.plot([], [], label='Airflow')
        self.line_humidity2, = self.ax_humidity.plot([], [], label='Cooler-Ambient')
        self.line_humidity3, = self.ax_humidity.plot([], [], label='Cooler-Discharge')


        # self.ax_temp.set_xlabel("Time")
        self.ax_temp.set_ylabel("Temperature")
        self.ax_temp.legend()
        self.ax_temp.legend(loc='upper right')

        # self.ax_humidity.set_xlabel("Time")
        self.ax_humidity.set_ylabel("Humidity")
        self.ax_humidity.legend()
        # set legend on top of the plot
        self.ax_humidity.legend(loc='upper right')
        

        self.timer = self.startTimer(20000)  # Update every 10 seconds

        # Adjust plot margins
        self.fig_temp.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.9)
        self.fig_humidity.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.9)

        self.generate_data()
        self.update_plots()

        self.resize(1800, 900)
        self.show()

    def timerEvent(self, event):
        self.generate_data()
        self.update_plots()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.canvas_temp.draw_idle()
        self.canvas_humidity.draw_idle()

    def generate_data(self):
        # get data from the database
        humidity_data, temperature_data = fetch_data()
        
        # check condition if the data is empty do nothing
        if len(humidity_data) == 6:
            if self.humidity1 == [] and self.humidity2 == [] and self.humidity3 == []:
                self.humidity1.append(humidity_data[1])
                self.humidity1_time.append(humidity_data[0])
                self.humidity2.append(humidity_data[3])
                self.humidity2_time.append(humidity_data[2])
                self.humidity3.append(humidity_data[5])
                self.humidity3_time.append(humidity_data[4])
            else:
                # append the data to the list
                if humidity_data[0] != self.humidity1_time[-1]:
                    self.humidity1.append(humidity_data[1])
                    self.humidity1_time.append(humidity_data[0])
                if humidity_data[2] != self.humidity2_time[-1]:
                    self.humidity2.append(humidity_data[3])
                    self.humidity2_time.append(humidity_data[2])
                if humidity_data[4] != self.humidity3_time[-1]:
                    self.humidity3.append(humidity_data[5])
                    self.humidity3_time.append(humidity_data[4])
                    
        if len(temperature_data) == 6:
            if self.temperature1 == [] and self.temperature2 == [] and self.temperature3 == []:
                self.temperature1.append(temperature_data[1])
                self.temperature1_time.append(temperature_data[0])
                self.temperature2.append(temperature_data[3])
                self.temperature2_time.append(temperature_data[2])
                self.temperature3.append(temperature_data[5])
                self.temperature3_time.append(temperature_data[4])
            else:
                # append the data to the list
                if temperature_data[0] != self.temperature1_time[-1]:
                    self.temperature1.append(temperature_data[1])
                    self.temperature1_time.append(temperature_data[0])
                if temperature_data[2] != self.temperature2_time[-1]:
                    self.temperature2.append(temperature_data[3])
                    self.temperature2_time.append(temperature_data[2])
                if temperature_data[4] != self.temperature3_time[-1]:
                    self.temperature3.append(temperature_data[5])
                    self.temperature3_time.append(temperature_data[4])

        # Limit data points to 20
        self.temperature1 = self.temperature1[-10:]
        self.temperature2 = self.temperature2[-10:]
        self.temperature3 = self.temperature3[-10:]
        
        self.temperature1_time = self.temperature1_time[-10:]
        self.temperature2_time = self.temperature2_time[-10:]
        self.temperature3_time = self.temperature3_time[-10:]
        
        self.humidity1 = self.humidity1[-10:]
        self.humidity2 = self.humidity2[-10:]
        self.humidity3 = self.humidity3[-10:]

        self.humidity1_time = self.humidity1_time[-10:]
        self.humidity2_time = self.humidity2_time[-10:]
        self.humidity3_time = self.humidity3_time[-10:]

    def update_plots(self):
        formatter = mdates.DateFormatter('%H:%M')  # Specify the HH:MM:SS format
        # Update temperature plot
        # xdata = np.arange(len(self.temperature1))  # Use a common x-axis
        self.line_temp1.set_data(self.temperature1_time, self.temperature1)
        self.line_temp2.set_data(self.temperature2_time, self.temperature2)
        self.line_temp3.set_data(self.temperature3_time, self.temperature3)
        self.ax_temp.xaxis.set_major_formatter(formatter)
        self.ax_temp.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))

        self.ax_temp.relim()
        self.ax_temp.autoscale_view()

        # Update humidity plot
        self.line_humidity1.set_data(self.humidity1_time, self.humidity1)
        self.line_humidity2.set_data(self.humidity2_time, self.humidity2)
        self.line_humidity3.set_data(self.humidity3_time, self.humidity3)
        
        # Format the x-axis to show HH:MM:SS
        self.ax_humidity.xaxis.set_major_formatter(formatter)

        # Set the tick locator to control the frequency of ticks (optional)
        self.ax_humidity.xaxis.set_major_locator(mdates.MinuteLocator(interval=1)) # Or MinuteLocator, HourLocator, etc.


        
        self.ax_humidity.relim()
        self.ax_humidity.autoscale_view()

        self.canvas_temp.draw()
        self.canvas_humidity.draw()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

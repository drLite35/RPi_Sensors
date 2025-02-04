import gi
import time
import board
import adafruit_dht
import adafruit_hcsr04
import digitalio

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton

class RPiSensorActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.max_participants = 1

        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        self.show_all()

        self.setup_sensors()
        self.create_gui()
        GLib.timeout_add_seconds(2, self.update_readings)

    def setup_sensors(self):
        self.dht_sensor = adafruit_dht.DHT11(board.D4)
        self.distance_sensor = adafruit_hcsr04.HCSR04(trigger_pin=board.D5, echo_pin=board.D6)
        self.pir_sensor = digitalio.DigitalInOut(board.D7)
        self.pir_sensor.direction = digitalio.Direction.INPUT

    def create_gui(self):
        # Main container with gradient background
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        self.main_box.set_margin_start(40)
        self.main_box.set_margin_end(40)
        self.main_box.set_margin_top(40)
        self.main_box.set_margin_bottom(40)
        self.set_canvas(self.main_box)

        # Title
        title_label = Gtk.Label(label="Raspberry Pi Sensor Dashboard")
        title_label.set_markup("<span font='20' weight='bold'>Raspberry Pi Sensor Dashboard</span>")
        self.main_box.pack_start(title_label, False, False, 10)

        # Grid for sensor cards
        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(20)
        grid.set_halign(Gtk.Align.CENTER)

        # Create sensor cards
        self.humidity_card = self.create_sensor_card("Humidity", "#4a90e2")
        self.distance_card = self.create_sensor_card("Distance", "#2ecc71")
        self.motion_card = self.create_sensor_card("Motion", "#9b59b6")

        # Add cards to grid
        grid.attach(self.humidity_card, 0, 0, 1, 1)
        grid.attach(self.distance_card, 1, 0, 1, 1)
        grid.attach(self.motion_card, 2, 0, 1, 1)

        self.main_box.pack_start(grid, True, True, 0)
        self.load_css()
        self.main_box.show_all()

    def create_sensor_card(self, title, color):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.set_size_request(200, 150)
        
        # Title
        title_label = Gtk.Label(label=title)
        title_label.get_style_context().add_class("card-title")
        card.pack_start(title_label, False, False, 0)
        
        # Value
        value_label = Gtk.Label(label="Loading...")
        value_label.get_style_context().add_class("card-value")
        card.pack_start(value_label, True, True, 0)
        
        # Add custom CSS class with color
        card.get_style_context().add_class("sensor-card")
        card.get_style_context().add_class(f"card-{title.lower()}")
        
        return card

    def load_css(self):
        css = b"""
        .sensor-card {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 200ms ease;
        }
        
        .sensor-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        
        .card-title {
            font-size: 18px;
            font-weight: bold;
            color: #333333;
        }
        
        .card-value {
            font-family: monospace;
            font-size: 24px;
            color: #ffffff;
        }
        
        .card-humidity {
            background: linear-gradient(135deg, #4a90e2, #357abd);
        }
        
        .card-distance {
            background: linear-gradient(135deg, #2ecc71, #27ae60);
        }
        
        .card-motion {
            background: linear-gradient(135deg, #9b59b6, #8e44ad);
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def update_readings(self):
        try:
            humidity = self.dht_sensor.humidity
            if humidity is not None:
                self.humidity_card.get_children()[1].set_text(f"{humidity:.1f} %")
        except RuntimeError as e:
            self.humidity_card.get_children()[1].set_text("Error")

        try:
            distance = self.distance_sensor.distance
            self.distance_card.get_children()[1].set_text(f"{distance:.1f} cm")
        except RuntimeError as e:
            self.distance_card.get_children()[1].set_text("Error")

        try:
            motion = self.pir_sensor.value
            self.motion_card.get_children()[1].set_text('Detected' if motion else 'Not detected')
        except RuntimeError as e:
            self.motion_card.get_children()[1].set_text("Error")

        return True

if __name__ == "__main__":
    activity = RPiSensorActivity(None)
    Gtk.main()
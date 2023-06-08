import gi
import psutil
import threading
import time
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class HelloWorldWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="CPU Information")
        self.set_default_size(400, 200)

        self.vbox = Gtk.VBox(spacing=10)
        self.add(self.vbox)

        self.cpu_cores = psutil.cpu_count()

        self.core_labels = []
        self.core_progress_bars = []
        for i in range(self.cpu_cores):
            label = Gtk.Label()
            label.set_text("Core " + str(i+1) + " usage:")
            self.vbox.pack_start(label, True, True, 0)
            self.core_labels.append(label)

            progress_bar = Gtk.ProgressBar()
            self.vbox.pack_start(progress_bar, True, True, 0)
            self.core_progress_bars.append(progress_bar)

        self.ram_label = Gtk.Label()
        self.vbox.pack_start(self.ram_label, True, True, 0)

        self.button = Gtk.Button(label="Start Stress Test")
        self.button.connect("clicked", self.on_button_clicked)

        self.button_box = Gtk.Box()
        self.button_box.pack_start(self.button, False, False, 0)

        alignment = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0, yscale=0)
        alignment.add(self.button_box)

        self.vbox.pack_start(alignment, False, False, 0)

        self.update_cpu_usage()

    def on_button_clicked(self, widget):
        # This command will create a stress test on one CPU core for 60 seconds
        stress_command = ["stress", "--cpu", "1", "--timeout", "60"]
        subprocess.Popen(stress_command)

    def update_cpu_usage(self):
        def cpu_monitor():
            while True:
                usages = psutil.cpu_percent(percpu=True)
                for i, usage in enumerate(usages):
                    color = "green" if usage < 50 else "red"
                    text = f'<span foreground="{color}">Core {i + 1} usage: {usage}%</span>'
                    GLib.idle_add(self.core_labels[i].set_markup, text)
                    GLib.idle_add(self.core_progress_bars[i].set_fraction, usage / 100)

                # update RAM usage
                ram = psutil.virtual_memory()
                GLib.idle_add(self.ram_label.set_text, f'RAM: {ram.percent}% of {round(ram.total / (1024.0 ** 3))}GB')
                time.sleep(1)

        threading.Thread(target=cpu_monitor).start()

win = HelloWorldWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

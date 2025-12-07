import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

# =============================================================================
# List of US time zones with friendly names (including common abbreviations)
# =============================================================================
US_TIMEZONES = {
    "Eastern (EST/EDT)":     "US/Eastern",
    "Central (CST/CDT)":     "US/Central",
    "Mountain (MST/MDT)":    "US/Mountain",
    "Pacific (PST/PDT)":     "US/Pacific",
    "Arizona (MST)":         "US/Arizona",      # No DST
}

TBILISI_TZ = "Asia/Tbilisi"

# =============================================================================
# Helper functions
# =============================================================================
def get_current_time(tz_str: str) -> str:
    """Return formatted time like '03:45:27 PM' for given timezone"""
    tz = pytz.timezone(tz_str)
    now = datetime.now(tz)
    return now.strftime("%I:%M:%S %p")   # 12-hour + AM/PM

def get_city_timezone(city_name: str):
    """Return IANA timezone string for a US city (e.g. 'America/Chicago')"""
    geolocator = Nominatim(user_agent="usa_timezone_app_v1")
    try:
        location = geolocator.geocode(city_name + ", USA", timeout=10)
        if not location:
            return None
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        return tz_str
    except Exception:
        return None

# =============================================================================
# Main Tkinter App
# =============================================================================
class TimeZoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USA + Tbilisi Live Clock")
        self.root.geometry("520x620")
        self.root.configure(bg="#f0f0f0")

        # Title
        title = tk.Label(root, text="Live Time Zones", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        title.pack(pady=10)

        # === USA Time Zones Frame ===
        usa_frame = tk.LabelFrame(root, text=" United States Time Zones ", font=("Arial", 12, "bold"), padx=10, pady=10)
        usa_frame.pack(padx=20, pady=10, fill="x")

        self.usa_labels = {}
        for name, tz in US_TIMEZONES.items():
            row = tk.Frame(usa_frame)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{name}:", width=22, anchor="w", font=("Courier", 11)).pack(side="left")
            time_lbl = tk.Label(row, text="Loading...", font=("Courier", 11, "bold"))
            time_lbl.pack(side="left")
            self.usa_labels[name] = time_lbl

        # === Tbilisi ===
        tbilisi_frame = tk.LabelFrame(root, text=" Georgia ", font=("Arial", 12, "bold"), padx=10, pady=8)
        tbilisi_frame.pack(padx=20, pady=10, fill="x")
        self.tbilisi_label = tk.Label(tbilisi_frame, text="Tbilisi: Loading...", font=("Courier", 13, "bold"))
        self.tbilisi_label.pack()

        # === Search + Controls ===
        control_frame = tk.Frame(root, bg="#f0f0f0")
        control_frame.pack(pady=15)

        tk.Label(control_frame, text="Search US City:", bg="#f0f0f0", font=("Arial", 10)).pack(side="left")
        self.city_entry = tk.Entry(control_frame, width=22, font=("Arial", 10))
        self.city_entry.pack(side="left", padx=8)
        self.city_entry.bind("<Return>", lambda event: self.search_city_time())  # Enter key works too

        tk.Button(control_frame, text="Search", bg="#2196F3", fg="white",
                  command=self.search_city_time).pack(side="left", padx=5)

        tk.Button(control_frame, text="Refresh Now", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                  command=self.manual_refresh).pack(side="left", padx=12)

        # === Search Result ===
        self.result_label = tk.Label(root, text="", font=("Arial", 11, "italic"), fg="#0066cc", bg="#f0f0f0")
        self.result_label.pack(pady=8)

        # Start auto-update
        self.update_times()
        self.root.after(60000, self.update_times)  # every minute

    # -------------------------------------------------------------------------
    def update_times(self):
        """Update all fixed time zones (USA + Tbilisi)"""
        for name, tz in US_TIMEZONES.items():
            self.usa_labels[name].config(text=get_current_time(tz))

        self.tbilisi_label.config(text=f"Tbilisi: {get_current_time(TBILISI_TZ)}")

        # Schedule next auto-update
        self.root.after(60000, self.update_times)

    # -------------------------------------------------------------------------
    def search_city_time(self):
        """Called by Search button or Enter key"""
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input needed", "Please type a city name")
            return

        tz_str = get_city_timezone(city)
        if tz_str:
            time_str = get_current_time(tz_str)
            self.result_label.config(
                text=f"{city.title()}: {time_str}  →  {tz_str}",
                fg="#006400"
            )
        else:
            messagebox.showerror("Not found", f"Could not find timezone for '{city}'.\nMake sure it's a city in the USA.")

    # -------------------------------------------------------------------------
    def manual_refresh(self):
        """Refresh everything immediately when user clicks the button"""
        self.update_times()
        if self.city_entry.get().strip():      # if there is something in the box → refresh it too
            self.search_city_time()

# =============================================================================
# Run the app
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = TimeZoneApp(root)
    root.mainloop()
# =============================================================================
# CLEAN FINAL VERSION – NO EXAMPLE TEXT
# Perfect from Tbilisi – ZIP codes + misspellings + real timezones
# =============================================================================

import tkinter as tk
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import re
import us  # pip install us

geolocator = Nominatim(user_agent="tbilisi_clock_clean")
tf = TimezoneFinder()

CITY_ALIASES = {
    "massachusetts": "Boston", "massachussets": "Boston", "massachusets": "Boston",
    "masachusetts": "Boston", "masachusets": "Boston",
    "newyork": "New York", "ny": "New York", "nyc": "New York",
    "la": "Los Angeles", "losangeles": "Los Angeles",
    "sf": "San Francisco", "sanfrancisco": "San Francisco",
    "vegas": "Las Vegas", "lasvegas": "Las Vegas",
    "miami": "Miami", "chicago": "Chicago", "houston": "Houston",
    "dallas": "Dallas", "atlanta": "Atlanta", "seattle": "Seattle",
    "phoenix": "Phoenix",
}

US_TIMEZONES = {
    "Eastern":   "US/Eastern",
    "Central":   "US/Central",
    "Mountain":  "US/Mountain",
    "Pacific":   "US/Pacific",
    "Alaska":    "US/Alaska",
    "Hawaii":    "US/Hawaii",
    "Arizona":   "US/Arizona",
}

TBILISI_TZ = "Asia/Tbilisi"

def get_current_time(tz_str: str) -> str:
    try:
        return datetime.now(pytz.timezone(tz_str)).strftime("%H:%M")
    except:
        return "--:--"

def get_real_tz_name(iana: str) -> str:
    try:
        tz = pytz.timezone(iana)
        now = datetime.now(tz)
        names = {
            "US/Eastern":   "EDT" if now.dst() else "EST",
            "US/Central":   "CDT" if now.dst() else "CST",
            "US/Mountain":  "MDT" if now.dst() else "MST",
            "US/Pacific":   "PDT" if now.dst() else "PST",
            # "US/Alaska":    "AKDT" if now.dst() else "AKST",
            # "US/Hawaii":    "HST",
            "US/Arizona":   "MST",
            "Europe/London": "BST" if now.dst() else "GMT",
            "Europe/Paris": "CEST" if now.dst() else "CET",
            "Asia/Dubai":   "+04",
            "Asia/Tbilisi": "+04",
            "Asia/Tokyo":   "JST",
        }
        return names.get(iana, tz.localize(datetime.now()).tzname())
    except:
        return "???"

def zip_to_city(zip_code: str):
    try:
        z = us.lookup(zip_code.strip())
        return f"{z.city}, {z.state}" if z else None
    except:
        return None

def smart_search(query: str):
    q = query.lower().strip()

    # ZIP code
    if re.match(r"^\d{5}$", q):
        city_state = zip_to_city(q)
        if city_state:
            return ("zip", city_state, q)

    # Alias
    if q in CITY_ALIASES:
        q = CITY_ALIASES[q]

    # Geocode
    try:
        loc = geolocator.geocode(q, exactly_one=True, timeout=12)
        if loc:
            tz = tf.timezone_at(lng=loc.longitude, lat=loc.latitude)
            city = loc.address.split(",")[0].strip()
            return ("city", city, tz)
    except:
        pass
    return None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("World Clock")
        self.root.geometry("620x760")
        self.root.configure(bg="#0d1117")

        tk.Label(root, text="World Clock", font=("Segoe UI", 15, "bold"), fg="#58a6ff", bg="#0d1117").pack(pady=10)

        # US zones
        us_frame = tk.LabelFrame(root, text=" United States ", font=("Arial", 14, "bold"), fg="#79c0ff", bg="#161b22", padx=20, pady=15)
        us_frame.pack(padx=20, pady=10, fill="x")
        self.us_labels = {}
        for name, tz in US_TIMEZONES.items():
            row = tk.Frame(us_frame, bg="#161b22")
            row.pack(fill="x", pady=6)
            tk.Label(row, text=f"{name:10}", fg="#8b949e", bg="#161b22", font=("Consolas", 13), anchor="w").pack(side="left")
            time_lbl = tk.Label(row, text="--:--", fg="#ffa657", bg="#161b22", font=("Consolas", 18, "bold"), width=8)
            time_lbl.pack(side="left")
            tz_lbl = tk.Label(row, text="---", fg="#ff7b72", bg="#161b22", font=("Consolas", 12))
            tz_lbl.pack(side="left", padx=15)
            self.us_labels[name] = (time_lbl, tz_lbl)

        # Tbilisi
        tb_frame = tk.LabelFrame(root, text=" Georgia ", font=("Arial", 12, "bold"), fg="#f85149", bg="#161b22")
        tb_frame.pack(padx=20, pady=15, fill="x")
        self.tbilisi_time = tk.Label(tb_frame, text="--:--", fg="#ff6b6b", bg="#161b22", font=("Consolas", 26, "bold"))
        self.tbilisi_time.pack(side="left", padx=40)
        tk.Label(tb_frame, text="+04", fg="#ffaaf0", bg="#161b22", font=("Consolas", 18)).pack(side="left")

        # Search
        search_frame = tk.Frame(root, bg="#0d1117")
        search_frame.pack(pady=35)
        tk.Label(search_frame, text="City or ZIP:", fg="#ffffff", bg="#0d1117", font=("Arial", 13)).pack(side="left")
        self.entry = tk.Entry(search_frame, width=30, font=("Arial", 13), bg="#21262d", fg="white", insertbackground="white")
        self.entry.pack(side="left", padx=12)
        self.entry.bind("<Return>", lambda e: self.search())
        tk.Button(search_frame, text="Search", bg="#238636", fg="white", font=("Arial", 12, "bold"), command=self.search).pack(side="left", padx=8)

        # Result – empty at start
        self.result = tk.Label(root, text="", font=("Consolas", 16, "bold"), fg="#a5d6ff", bg="#0d1117")
        self.result.pack(pady=30)

        self.update_clocks()
        self.root.after(1000, self.auto_update)

    def auto_update(self):
        self.update_clocks()
        self.root.after(1000, self.auto_update)

    def update_clocks(self):
        for name, tz in US_TIMEZONES.items():
            t = get_current_time(tz)
            n = get_real_tz_name(tz)
            self.us_labels[name][0].config(text=t)
            self.us_labels[name][1].config(text=n)
        self.tbilisi_time.config(text=get_current_time(TBILISI_TZ))

    def search(self):
        query = self.entry.get().strip()
        if not query:
            self.result.config(text="")
            return

        res = smart_search(query)
        if not res:
            self.result.config(text="Not found", fg="#ff6b6b")
            return

        kind = res[0]
        if kind == "zip":
            city_state, zip_code = res[1], res[2]
            loc = geolocator.geocode(city_state, timeout=12)
            if loc:
                tz = tf.timezone_at(lng=loc.longitude, lat=loc.latitude)
                self.result.config(text=f"{city_state} ({zip_code}):  {get_current_time(tz)}  -  {get_real_tz_name(tz)}", fg="#a5d6ff")
            else:
                self.result.config(text="Location error", fg="#ffa657")
        else:  # city
            city_name, tz = res[1], res[2]
            self.result.config(text=f"{city_name}:  {get_current_time(tz)}  -  {get_real_tz_name(tz)}", fg="#a5d6ff")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
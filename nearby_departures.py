from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import json
import os
from datetime import datetime
import math
from collections import defaultdict

app = Flask(__name__)

# Settings file path
SETTINGS_FILE = 'settings.json'

# Default settings
default_settings = {
    'address': '',
    'latitude': None,
    'longitude': None,
    'max_walk_minutes': 10,  # minutes
    'max_departures_per_station': 30,
    'min_minutes': 2,
    'max_minutes': 30,
    'show_platform': True,
    'selected_stations': [],  # List of selected station IDs
    'language': 'de'  # Default to German
}

def load_settings():
    """Load settings from file or return defaults"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                saved_settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                settings = default_settings.copy()
                settings.update(saved_settings)
                return settings
    except Exception:
        pass
    return default_settings.copy()

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass

# Load settings on startup
settings = load_settings()

# Translations
translations = {
    'de': {
        'nearby_departures': 'Abfahrten in der Nähe',
        'direction': 'Richtung',
        'line': 'Linie',
        'station': 'Bahnhof',
        'departure_in': 'Abfahrt in',
        'platform': 'Gleis',
        'leave_in': 'Losgehen in',
        'next_departures': 'Nächste Abfahrten',
        'now': 'jetzt',
        'min': 'Min',
        'setup': 'Einstellungen',
        'station_selection': 'Stationsauswahl',
        'address_berlin': 'Adresse in Berlin',
        'max_walk_time': 'Maximale Gehzeit (Minuten)',
        'continue_step2': 'Weiter zu Schritt 2',
        'save_params': 'Parameter speichern & Stationen neu laden',
        'select_all': 'Alle',
        'select_none': 'Keine',
        'save_stations': 'Stationen speichern & zu Abfahrten',
        'back_to_departures': 'Zurück zu Abfahrten',
        'back_to_step1': 'Zurück zu Schritt 1',
        'step2_title': 'Schritt 2: Stationen & Parameter',
        'set_parameters': 'Parameter einstellen',
        'select_stations': 'Stationen auswählen',
        'select_stations_desc': 'Wählen Sie die Stationen aus, die auf der Abfahrtstafel angezeigt werden sollen:',
        'walk_time': 'Gehzeit',
        'air_distance': 'Luftlinie',
        'loading_stations': 'Lade Stationen...',
        'next_update': 'Nächste Aktualisierung in:',
        'seconds': 'Sekunden',
        'updating': 'aktualisiert...',
        'departures_per_station': 'Abfahrten pro Haltestelle',
        'min_minutes_departure': 'Mindest-Minuten bis Abfahrt',
        'max_minutes_departure': 'Maximal-Minuten bis Abfahrt',
        'show_platform_column': 'Gleis-Spalte anzeigen',
        'location': 'Standort',
        'address_placeholder': 'z.B. Alexanderplatz 1, Berlin',
        'address_tooltip': 'Geben Sie Ihre Berliner Adresse ein',
        'walk_time_tooltip': 'Wie weit sind Sie bereit zu gehen?',
        'info_text': 'Diese App findet automatisch alle Haltestellen in Ihrer Nähe und zeigt nur Abfahrten an, die Sie zu Fuß noch erreichen können. Geben Sie Ihre Adresse in Berlin ein.',
        'params_saved': 'Parameter gespeichert! Stationen werden neu geladen...',
        'how_it_works': 'Funktionsweise:',
        'how_it_works_list': [
            'Die App ermittelt Koordinaten aus Ihrer Adresse',
            'Findet alle Haltestellen in der angegebenen Gehentfernung',
            'Berechnet Gehzeit zu jeder Haltestelle (~80m/min)',
            'Zeigt nur Abfahrten, die Sie noch erreichen können (Gehzeit + 2min Puffer)',
            'Sortiert nach Abfahrtszeit'
        ],
        'no_departures_available': 'Keine Abfahrten verfügbar'
    },
    'en': {
        'nearby_departures': 'Nearby Departures',
        'direction': 'Direction',
        'line': 'Line',
        'station': 'Station',
        'departure_in': 'Departure in',
        'platform': 'Platform',
        'leave_in': 'Leave in',
        'next_departures': 'Next Departures',
        'now': 'now',
        'min': 'min',
        'setup': 'Settings',
        'station_selection': 'Station Selection',
        'address_berlin': 'Address in Berlin',
        'max_walk_time': 'Maximum walking time (minutes)',
        'continue_step2': 'Continue to Step 2',
        'save_params': 'Save parameters & reload stations',
        'select_all': 'All',
        'select_none': 'None',
        'save_stations': 'Save stations & go to departures',
        'back_to_departures': 'Back to departures',
        'back_to_step1': 'Back to Step 1',
        'step2_title': 'Step 2: Stations & Parameters',
        'set_parameters': 'Set parameters',
        'select_stations': 'Select stations',
        'select_stations_desc': 'Choose the stations to display on the departure board:',
        'walk_time': 'Walk time',
        'air_distance': 'Air distance',
        'loading_stations': 'Loading stations...',
        'next_update': 'Next update in:',
        'seconds': 'seconds',
        'updating': 'updating...',
        'departures_per_station': 'Departures per station',
        'min_minutes_departure': 'Minimum minutes until departure',
        'max_minutes_departure': 'Maximum minutes until departure',
        'show_platform_column': 'Show platform column',
        'location': 'Location',
        'address_placeholder': 'e.g. Alexanderplatz 1, Berlin',
        'address_tooltip': 'Enter your Berlin address',
        'walk_time_tooltip': 'How far are you willing to walk?',
        'info_text': 'This app automatically finds all nearby stations and shows only departures you can still reach on foot. Enter your address in Berlin.',
        'params_saved': 'Parameters saved! Stations are being reloaded...',
        'how_it_works': 'How it works:',
        'how_it_works_list': [
            'The app determines coordinates from your address',
            'Finds all stations within the specified walking distance',
            'Calculates walking time to each station (~80m/min)',
            'Shows only departures you can still reach (walking time + 2min buffer)',
            'Sorts by departure time'
        ],
        'no_departures_available': 'No departures available'
    }
}

def t(key):
    """Translation helper function"""
    return translations[settings['language']].get(key, key)

def get_coordinates_from_address(address):
    """Get coordinates from address using Nominatim"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{address}, Berlin, Germany",
            'format': 'json',
            'limit': 1
        }
        headers = {'User-Agent': 'BVG-Departure-Board/1.0'}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
        return None, None
    except Exception:
        return None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in meters"""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon/2) * math.sin(delta_lon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def find_nearby_stations(lat, lon, radius=1000):
    """Find stations near coordinates"""
    try:
        url = "https://v6.vbb.transport.rest/locations/nearby"
        params = {
            'latitude': lat,
            'longitude': lon,
            'distance': radius,
            'results': 50
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
        return []
    except Exception as e:
        pass
        return []

def get_line_type(line_name, line_product=None):
    """Determine BVG line type"""
    if not line_name or line_name == 'N/A':
        return 'bus'
    
    line_name = str(line_name).upper().replace(' ', '')
    
    if line_product:
        product = str(line_product).lower()
        if 'tram' in product:
            return 'tram'
        elif 'bus' in product:
            return 'bus'
        elif 'subway' in product or 'metro' in product:
            return line_name.lower() if line_name.startswith('U') else 'u'
        elif 'suburban' in product:
            return line_name.lower() if line_name.startswith('S') else 's'
    
    if line_name.startswith('S'):
        return line_name.lower()
    elif line_name.startswith('U'):
        return line_name.lower()
    elif line_name.startswith(('RE', 'RB', 'IC', 'ICE')):
        return 'regional'
    else:
        return 'bus'

def get_station_departures(station_id, limit=30):
    """Get departures for a station"""
    try:
        url = f"https://v6.vbb.transport.rest/stops/{station_id}/departures"
        params = {'results': limit, 'duration': 120}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'departures' in data:
                departures = data['departures']
                return departures if isinstance(departures, list) else []
            elif isinstance(data, list):
                return data
            return []
        else:
            pass
        return []
    except Exception as e:
        pass
        return []

def group_by_direction_area(direction):
    """Group directions by area for better organization"""
    direction = direction.lower()
    
    # Central areas
    if any(area in direction for area in ['mitte', 'alexanderplatz', 'potsdamer platz', 'friedrichstr']):
        return 'Berlin Mitte'
    
    # West
    if any(area in direction for area in ['charlottenburg', 'wilmersdorf', 'schöneberg', 'steglitz', 'zehlendorf', 'spandau']):
        return 'West Berlin'
    
    # East
    if any(area in direction for area in ['friedrichshain', 'kreuzberg', 'prenzlauer berg', 'lichtenberg', 'marzahn', 'hellersdorf']):
        return 'East Berlin'
    
    # North
    if any(area in direction for area in ['wedding', 'reinickendorf', 'pankow', 'weißensee']):
        return 'North Berlin'
    
    # South
    if any(area in direction for area in ['tempelhof', 'neukölln', 'treptow', 'köpenick']):
        return 'South Berlin'
    
    # Brandenburg/Outskirts
    if any(area in direction for area in ['potsdam', 'oranienburg', 'strausberg', 'königs wusterhausen', 'flughafen']):
        return 'Brandenburg'
    
    return 'Other Destinations'

@app.route('/')
def index():
    """Main departure board grouped by destination areas"""
    if not settings['latitude'] or not settings['longitude']:
        return redirect(url_for('setup'))
    
    try:
        search_radius = settings['max_walk_minutes'] * 80
        stations = find_nearby_stations(settings['latitude'], settings['longitude'], search_radius)
        departures_by_destination = defaultdict(list)
        
        for station in stations:
            if not isinstance(station, dict) or 'id' not in station:
                continue
            if settings['selected_stations'] and station['id'] not in settings['selected_stations']:
                continue
            station_lat = station.get('location', {}).get('latitude')
            station_lon = station.get('location', {}).get('longitude')
            
            if station_lat and station_lon:
                distance = calculate_distance(
                    settings['latitude'], settings['longitude'],
                    station_lat, station_lon
                )
                
                actual_walking_distance = distance * 1.3
                walk_time = int(actual_walking_distance / 80)
                
                if walk_time <= settings['max_walk_minutes']:
                    departures = get_station_departures(station['id'], settings['max_departures_per_station'])
                    
                    # Group departures by line and direction to get next 3 times
                    line_direction_groups = defaultdict(list)
                    
                    for dep in departures:
                        if dep.get('when'):
                            try:
                                dep_time = datetime.fromisoformat(dep['when'].replace('Z', '+00:00'))
                                now = datetime.now(dep_time.tzinfo)
                                minutes_until = int((dep_time - now).total_seconds() / 60)
                                
                                time_ok = settings['min_minutes'] <= minutes_until <= settings['max_minutes']
                                reachable = minutes_until >= walk_time
                                
                                if time_ok and reachable:
                                    line_name = dep.get('line', {}).get('name', 'N/A')
                                    direction = dep.get('direction', 'N/A')
                                    
                                    # Calculate delay
                                    delay = 0
                                    if dep.get('delay'):
                                        delay = int(dep['delay'] / 60)  # Convert seconds to minutes
                                    
                                    # Adjust minutes_until for delay
                                    actual_minutes_until = minutes_until + delay
                                    
                                    key = f"{line_name}|{direction}"
                                    line_direction_groups[key].append({
                                        'minutes_until': actual_minutes_until,
                                        'delay': delay,
                                        'platform': dep.get('platform') or '',
                                        'line_product': dep.get('line', {}).get('product', None)
                                    })
                            except Exception:
                                pass
                    
                    # Process grouped departures
                    for key, group_deps in line_direction_groups.items():
                        if not group_deps:
                            continue
                            
                        line_name, direction = key.split('|', 1)
                        
                        # Sort by departure time and take first 3
                        group_deps.sort(key=lambda x: x['minutes_until'])
                        next_deps = group_deps[:3]
                        
                        first_dep = next_deps[0]
                        leave_in_minutes = first_dep['minutes_until'] - walk_time
                        leave_time = f"{leave_in_minutes} {t('min')}" if leave_in_minutes > 0 else t('now')
                        
                        # Determine urgency
                        if leave_in_minutes <= 0:
                            urgency = 'now'
                        elif leave_in_minutes <= 3:
                            urgency = 'soon'
                        else:
                            urgency = 'later'
                        
                        # Format display time
                        display_time = f"{first_dep['minutes_until']} {t('min')}" if first_dep['minutes_until'] <= 10 else f"{first_dep['minutes_until']} {t('min')}"
                        
                        # Format next times
                        next_times = ""
                        if len(next_deps) > 1:
                            next_times = ", ".join([f"{dep['minutes_until']}{t('min')}" for dep in next_deps[1:]])
                        
                        direction_area = group_by_direction_area(direction)
                        
                        departures_by_destination[direction_area].append({
                            'station_name': station['name'],
                            'line': line_name,
                            'line_type': get_line_type(line_name, first_dep['line_product']),
                            'direction': direction,
                            'minutes': display_time,
                            'next_times': next_times,
                            'platform': first_dep['platform'],
                            'leave_time': leave_time,
                            'urgency': urgency,
                            'leave_in_minutes': leave_in_minutes,
                            'delay': first_dep['delay'] if first_dep['delay'] > 0 else None
                        })
        
        # Sort departures within each destination group by leave time
        for destination_area in departures_by_destination:
            departures_by_destination[destination_area].sort(key=lambda x: x['leave_in_minutes'] if x['leave_in_minutes'] > 0 else -1)
        
        # Sort destination areas
        sorted_destinations = dict(sorted(departures_by_destination.items()))
        
        return render_template('nearby_departures.html', 
                             departures_by_destination=sorted_destinations, 
                             settings=settings, t=t)
        
    except Exception as e:
        return f"<h2>Error: {e}</h2><a href='/setup'>Setup</a>"

@app.route('/setup')
def setup():
    """Setup page for address input"""
    return render_template('setup.html', settings=settings, t=t)

@app.route('/debug')
def debug_stations():
    """Debug nearby stations"""
    if not settings['latitude'] or not settings['longitude']:
        return "No coordinates set. Go to <a href='/setup'>setup</a> first."
    
    try:
        search_radius = settings['max_walk_minutes'] * 80
        stations = find_nearby_stations(settings['latitude'], settings['longitude'], search_radius)
        
        result = f"<h2>Debug Info</h2>"
        result += f"<p>Coordinates: {settings['latitude']}, {settings['longitude']}</p>"
        result += f"<p>Search radius: {search_radius}m</p>"
        result += f"<p>Found {len(stations)} stations:</p><ul>"
        
        for station in stations[:10]:
            station_lat = station.get('location', {}).get('latitude')
            station_lon = station.get('location', {}).get('longitude')
            if station_lat and station_lon:
                distance = calculate_distance(settings['latitude'], settings['longitude'], station_lat, station_lon)
                walk_time = int(distance / 80)
                result += f"<li>{station['name']} - {int(distance)}m ({walk_time}min walk)</li>"
        
        result += "</ul><a href='/'>Back</a>"
        return result
    except Exception as e:
        return f"Error: {e}"

@app.route('/stations')
def select_stations():
    """Station selection page"""
    if not settings['latitude'] or not settings['longitude']:
        return redirect(url_for('setup'))
    
    search_radius = settings['max_walk_minutes'] * 80
    stations = find_nearby_stations(settings['latitude'], settings['longitude'], search_radius)
    
    # Add distance info to stations
    for station in stations:
        if not isinstance(station, dict):
            continue
        station_lat = station.get('location', {}).get('latitude')
        station_lon = station.get('location', {}).get('longitude')
        if station_lat and station_lon:
            distance = calculate_distance(settings['latitude'], settings['longitude'], station_lat, station_lon)
            actual_walking_distance = distance * 1.3
            station['walk_time'] = int(actual_walking_distance / 80)
            station['distance'] = int(distance)
    
    stations = [s for s in stations if s.get('walk_time', 999) <= settings['max_walk_minutes']]
    stations.sort(key=lambda x: x.get('walk_time', 999))
    
    return render_template('station_selection.html', stations=stations, settings=settings, t=t)

@app.route('/api/nearby_stations')
def api_nearby_stations():
    """API endpoint for nearby stations"""
    if not settings['latitude'] or not settings['longitude']:
        return jsonify([])
    
    search_radius = settings['max_walk_minutes'] * 80
    stations = find_nearby_stations(settings['latitude'], settings['longitude'], search_radius)
    
    for station in stations:
        if not isinstance(station, dict):
            continue
        station_lat = station.get('location', {}).get('latitude')
        station_lon = station.get('location', {}).get('longitude')
        if station_lat and station_lon:
            distance = calculate_distance(settings['latitude'], settings['longitude'], station_lat, station_lon)
            actual_walking_distance = distance * 1.3
            station['walk_time'] = int(actual_walking_distance / 80)
            station['distance'] = int(distance)
    
    stations = [s for s in stations if s.get('walk_time', 999) <= settings['max_walk_minutes']]
    stations.sort(key=lambda x: x.get('walk_time', 999))
    
    return jsonify(stations)

@app.route('/set_language/<lang>')
def set_language(lang):
    """Set specific language"""
    if lang in ['de', 'en']:
        settings['language'] = lang
        save_settings(settings)
    return redirect(request.referrer or url_for('index'))

@app.route('/update_stations', methods=['POST'])
def update_stations():
    """Update selected stations"""
    settings['selected_stations'] = request.form.getlist('selected_stations')
    save_settings(settings)
    return redirect(url_for('index'))

@app.route('/set_address', methods=['POST'])
def set_address():
    """Step 1: Set address only"""
    try:
        address = request.form.get('address', '')
        settings['address'] = address
        
        if address:
            lat, lon = get_coordinates_from_address(address)
            if lat and lon:
                settings['latitude'] = lat
                settings['longitude'] = lon
                save_settings(settings)
                return redirect(url_for('setup2'))
            else:
                return redirect(url_for('setup') + '?error=address_not_found')
        
        return redirect(url_for('setup'))
    except Exception as e:
        return redirect(url_for('setup') + f'?error={e}')

@app.route('/setup2')
def setup2():
    """Step 2: Station selection and parameters"""
    if not settings['latitude'] or not settings['longitude']:
        return redirect(url_for('setup'))
    return render_template('setup2.html', settings=settings, t=t)

@app.route('/update_location', methods=['POST'])
def update_location():
    """Update location settings and parameters"""
    try:
        settings['max_walk_minutes'] = int(request.form.get('max_walk_minutes', 8))
        settings['max_departures_per_station'] = int(request.form.get('max_departures_per_station', 5))
        settings['min_minutes'] = int(request.form.get('min_minutes', 2))
        settings['max_minutes'] = int(request.form.get('max_minutes', 30))
        settings['show_platform'] = 'show_platform' in request.form
        
        save_settings(settings)
        return redirect(url_for('setup2') + '?success=1')
    except Exception as e:
        return redirect(url_for('setup2') + f'?error={e}')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
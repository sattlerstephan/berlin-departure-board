# Changelog

## v1.0.0 - 2024-12-19

### 🎉 Initial Release

**Features:**
- Real-time Berlin public transport departure board
- Walking time-based filtering - only shows departures you can actually reach
- Bilingual support (German/English) with flag-based language switching
- Mobile-responsive design for all devices
- Color-coded urgency indicators (red = leave now, orange = leave soon, green = plenty of time)
- Station selection and filtering
- Customizable parameters (walking distance, time windows, departures per station)
- Raspberry Pi deployment ready with systemd service

**Technical:**
- Uses VBB Transport REST API v6 for real-time data
- Flask web framework
- Responsive CSS with mobile breakpoints
- Auto-refresh every 30 seconds
- Geolocation via OpenStreetMap Nominatim

**Deployment:**
- One-command setup with requirements.txt
- Systemd service for auto-start on Raspberry Pi
- Docker-ready configuration
- Comprehensive documentation

### 🚀 Getting Started
1. `pip install flask requests`
2. `python nearby_departures.py`
3. Open http://localhost:5001
4. Enter your Berlin address and enjoy!

Perfect for:
- Daily commuters in Berlin
- Raspberry Pi kiosk displays
- Mobile quick departure checks
- Anyone who wants to know exactly when to leave home
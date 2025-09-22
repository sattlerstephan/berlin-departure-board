# Berlin Departure Board

A real-time departure board for Berlin public transport that shows only departures you can actually reach by walking.

## Features

- 🚇 Real-time departures from nearby BVG stations
- 🚶 Shows only reachable departures based on walking time
- 🇩🇪🇬🇧 German/English language support
- ⏰ Color-coded urgency (red = leave now, orange = leave soon, green = plenty of time)
- 📱 Responsive web interface
- 🎯 Station selection and filtering

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install flask requests
   ```

2. **Run the app:**
   ```bash
   python nearby_departures.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5001
   ```

4. **Setup:**
   - Enter your Berlin address
   - Select nearby stations
   - Enjoy real-time departures!

## Raspberry Pi Deployment

1. **Copy files to Pi:**
   ```bash
   scp -r . pi@[PI_IP]:/home/pi/departure-board
   ```

2. **Install and run:**
   ```bash
   cd /home/pi/departure-board
   python3 -m venv venv
   source venv/bin/activate
   pip install flask requests
   python nearby_departures.py
   ```

3. **Auto-start service:**
   ```bash
   sudo cp departure-board.service /etc/systemd/system/
   sudo systemctl enable departure-board.service
   sudo systemctl start departure-board.service
   ```

## Configuration

- **Walking time:** Adjust max walking distance in settings
- **Update interval:** Departures refresh every 30 seconds
- **Station selection:** Choose which nearby stations to display
- **Language:** Toggle between German and English

## API

Uses the [VBB Transport REST API](https://v6.vbb.transport.rest/) for real-time Berlin public transport data.

## License

MIT License - feel free to use and modify!

## Screenshots

The app shows departures sorted by urgency - most urgent first, with color-coded indicators for when you need to leave.
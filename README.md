<h1 align="center">
  <img src="static/logo.png" />
</h1>

<p align="center">
  Cr4wler is a sophisticated web application dedicated to scanning IP ranges, extracting detailed information on open ports, services, and associated data, all seamlessly presented via an intuitive user interface. Powered by robust backend tools such as masscan and nmap, Cr4wler ensures comprehensive scanning capabilities and is crafted to deliver a seamless user experience.
</p>

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Scan IP ranges for open ports and services.
- Retrieve detailed information about discovered hosts including geolocation, OS, and reverse DNS, Ports and Services.
- Display results in an interactive and user-friendly web interface.
- Sort results by Country, Open-ports, Services, OS and more...
- Statistics and graphs based on geolocation and stats.

## Requirements

- Python 3.x
- Flask
- masscan
- nmap

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/TalMaIka/Cr4wler.git
    cd Cr4wler
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. Ensure `masscan` and `nmap` are installed on your system. Refer to their respective installation guides.

4. Start the Flask server:

    ```bash
    python app.py
    ```

## Usage

1. Start the Flask server:

    ```bash
    python app.py
    ```

2. Open your web browser and navigate to `http://localhost:5000`.

3. Click the "Fetch Hosts" button to retrieve and display the scanned data.

## API Endpoints

- **GET `/api/fetch`**: Fetches the scanned host data.

### Example Response

```json
[
    {
        "ip": "1.2.3.1",
        "geolocation": {
            "city": "San Diego",
            "region": "California",
            "country": "US",
            "loc": "37.25329,-121.78575"
        },
        "os_name": "Linux 2.4 (Slackware 10.2)",
        "rdns": "N/A",
        "timestamp": "2024-07-17T23:20:15Z",
        "ports": [
            {
                "port": 80,
                "service": "http",
                "product": "nginx"
            },
            {
                "port": 3306,
                "service": "mysql",
                "version": "5.5.62",
                "product": "MySQL"
            }
        ]
    }
]
```

## Project Structure

```
Cr4wler/
├── static/
│   ├── styles.css        # CSS file
|   |── main.js           # JS file  
│   └── logo.png          # Logo image
├── templates/
│   └── index.html        # Web interface
├── instance/
│   └── hosts.db          # SQLite Database.
├── requirements.txt      # Python dependencies
├── app.py                # Flask application
└── scanner.py            # Crawler bots.
```

## Contributing

We welcome contributions to enhance the Cr4wler project. Here are some ways you can contribute:

- Reporting bugs and issues
- Submitting feature requests
- Creating pull requests with enhancements

### Steps to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Enjoy using Cr4wler! Use it responsibly

---

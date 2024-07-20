let hostsData = [];
let currentPage = 1;
const resultsPerPage = 10;
let map;
let chart;

async function fetchHosts() {
    try {
        const response = await fetch('/api/fetch');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        hostsData = await response.json();
        displayHosts();
        showNotification('Data fetched successfully!');
    } catch (error) {
        console.error('Error fetching data:', error);
        alert('Failed to fetch data. Please try again later.');
    }
}

function displayHosts() {
    const output = document.getElementById('output');
    const searchQuery = document.getElementById('searchBar').value.trim();
    console.log('Search Query:', searchQuery);  // Debug line
    output.innerHTML = '';

    // Sorting data by timestamp in descending order
    hostsData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    // Parsing filters from search query
    const portsMatch = searchQuery.match(/port:(\d+(?:,\d+)*)/i);
    const servicesMatch = searchQuery.match(/service:([\w,]*)/i);
    const countryMatch = searchQuery.match(/country:([A-Z]{2,3})/i);  // Regex for 2 or 3 uppercase letters
    const osMatch = searchQuery.match(/os:([\w]*)/i);

    console.log('Country Match:', countryMatch);  // Debug line

    const filteredHosts = hostsData.filter(host => {
        let matches = true;

        // Check for ports
        if (portsMatch) {
            const ports = portsMatch[1].split(',').map(port => port.trim());
            matches = host.ports.some(port => ports.includes(port.port.toString()));
        }

        // Check for services
        if (servicesMatch) {
            const services = servicesMatch[1].split(',').map(service => service.trim().toLowerCase());
            matches = matches && host.ports.some(port => services.includes(port.service.toLowerCase()));
        }

        // Check for country
        if (countryMatch) {
            const country = host.geolocation.country ? host.geolocation.country.toLowerCase() : '';
            matches = matches && country === countryMatch[1].toLowerCase();
        }

        // Check for OS
        if (osMatch) {
            matches = matches && host.os_name.toLowerCase() === osMatch[1].toLowerCase();
        }

        return matches;
    });

    const totalPages = Math.ceil(filteredHosts.length / resultsPerPage);
    const start = (currentPage - 1) * resultsPerPage;
    const end = start + resultsPerPage;

    filteredHosts.slice(start, end).forEach(host => {
        const hostElement = document.createElement('div');
        hostElement.classList.add('host');

        let hostInfo = `
            <h3>IP: ${host.ip}</h3>
            <p>Location: ${host.geolocation.city}, ${host.geolocation.region}, ${host.geolocation.country}</p>
            <p>Coordinates: ${host.geolocation.loc}</p>
            <p>Reverse DNS: ${host.rdns}</p>
            <p>Timestamp: ${new Date(host.timestamp).toLocaleString()}</p>
        `;

        if (host.os_name !== "unknown") {
            hostInfo += `<p>OS: ${host.os_name}</p>`;
        }

        hostElement.innerHTML = hostInfo;

        const portsList = document.createElement('ul');
        portsList.classList.add('ports');
        host.ports.forEach(port => {
            let portText = `Port: ${port.port}, Service: ${port.service}`;
            if (port.version !== "unknown") {
                portText += `, Version: ${port.version}`;
            }
            if (port.product !== "unknown") {
                portText += `, Product: ${port.product}`;
            }
            const portItem = document.createElement('li');
            portItem.textContent = portText;
            portsList.appendChild(portItem);
        });

        hostElement.appendChild(portsList);
        output.appendChild(hostElement);
    });

    renderPagination(totalPages);
    updateMap(filteredHosts);
    updateChart(filteredHosts);
}

// Add this function to your existing script
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderPagination(totalPages) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';

    for (let i = 1; i <= totalPages; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.onclick = () => {
            currentPage = i;
            displayHosts();
            scrollToTop();  // Scroll to the top when a page button is clicked
        };

        if (i === currentPage) {
            pageButton.style.fontWeight = 'bold';
        }

        pagination.appendChild(pageButton);
    }
}

function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.add('show');

    // Remove the show class after the animation completes
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);  // 3000 milliseconds = 3 seconds
}

function updateMap(filteredHosts) {
    if (map) {
        map.remove();
    }

    map = L.map('map').setView([0, 0], 2);  // Initial view

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    filteredHosts.forEach(host => {
        if (host.geolocation.loc) {
            const [lat, lon] = host.geolocation.loc.split(',').map(Number);
            L.marker([lat, lon])
                .addTo(map)
                .bindPopup(`<strong>IP:</strong> ${host.ip}<br><strong>Location:</strong> ${host.geolocation.city}, ${host.geolocation.country}`);
        }
    });
}

function updateChart(filteredHosts) {
    const ctx = document.getElementById('statsChart').getContext('2d');

    const osCount = filteredHosts.reduce((acc, host) => {
        const os = host.os_name === "unknown" ? "Unknown" : host.os_name;
        acc[os] = (acc[os] || 0) + 1;
        return acc;
    }, {});

    const labels = Object.keys(osCount);
    const data = Object.values(osCount);

    if (chart) {
        chart.destroy();
    }

    chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#e94560', '#16213e', '#0f3460', '#e7dfdd'],
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,  // Allow resizing based on container size
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            return `${tooltipItem.label}: ${tooltipItem.raw}`;
                        }
                    }
                }
            }
        },
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const searchBar = document.getElementById('searchBar');
    searchBar.addEventListener('input', () => {
        currentPage = 1;
        displayHosts();
    });

    fetchHosts();
});
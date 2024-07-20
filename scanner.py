# Cr4wler - Network Live Hosts Analyzer.
# Version: 1.0.0
# Date: Jul 21, 2024
# Copyrights © Tal.M

import xml.etree.ElementTree as ET
import subprocess
import requests
from datetime import datetime
import os

# Function to check if Masscan is installed
def check_masscan():
    return os.path.exists('/usr/bin/masscan')

# Function to run Masscan
def run_masscan(ip_range, rate):
    masscan_cmd = f"/usr/bin/masscan -p21,22,23,25,53,80,110,143,443,445,3389,389,636,3306,5432 {ip_range} --rate {rate} --exclude 255.255.255.255 -oX masscan_output.xml"
    subprocess.run(masscan_cmd, shell=True)

# Function to run Nmap with extended scripts
def run_nmap(ip):
    nmap_cmd = f"nmap -v -O -sV -p 21,22,23,25,53,80,110,143,443,445,3389,389,636,3306,5432 --open -oX nmap_output_{ip}.xml {ip}"
    subprocess.run(nmap_cmd, shell=True)

# Function to parse Nmap XML output
def parse_nmap_output(xml_file):
    if not os.path.exists(xml_file):
        print(f"Error: {xml_file} not found.")
        return []

    tree = ET.parse(xml_file)
    root = tree.getroot()
    hosts = []

    for host in root.findall('host'):
        ip = host.find('address').attrib['addr']
        os_data = host.find('os/osmatch')
        os_name = os_data.attrib['name'] if os_data is not None else 'unknown'
        os_accuracy = os_data.attrib['accuracy'] if os_data is not None else 'unknown'
        ports = []

        for port in host.findall('ports/port'):
            port_id = port.attrib['portid']
            service = port.find('service').attrib.get('name', 'unknown')
            version = port.find('service').attrib.get('version', 'unknown')
            product = port.find('service').attrib.get('product', 'unknown')
            banner = port.find('script[@id="banner"]')
            banner_data = banner.find('output').text if banner is not None else 'N/A'
            http_title = port.find('script[@id="http-title"]')
            http_title_data = http_title.find('title').text if http_title is not None and http_title.find('title') is not None else 'N/A'
            ssl_cert = port.find('script[@id="ssl-cert"]')
            ssl_cert_data = ssl_cert.find('output').text if ssl_cert is not None else 'N/A'

            ports.append({
                'port': port_id,
                'service': service,
                'version': version,
                'product': product,
                'banner': banner_data,
                'http_title': http_title_data,
                'ssl_cert': ssl_cert_data
            })

        # Fetch additional data
        geo_data = fetch_geolocation(ip)
        rdns = fetch_rdns(host)
        whois = fetch_whois(host)
        timestamp = datetime.utcnow().isoformat()

        hosts.append({
            'ip': ip,
            'os_name': os_name,
            'os_accuracy': os_accuracy,
            'ports': ports,
            'geolocation': geo_data,
            'rdns': rdns,
            'whois': whois,
            'timestamp': timestamp
        })

    return hosts

# Function to fetch geolocation data
def fetch_geolocation(ip):
    try:
        response = requests.get(f'http://ipinfo.io/{ip}/json', timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching geolocation data: Status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Error fetching geolocation data: {e}")
    return {}

# Function to fetch reverse DNS data
def fetch_rdns(host):
    try:
        rdns = host.find("hostnames/hostname").attrib.get('name', 'N/A')
        return rdns
    except Exception as e:
        print(f"Error fetching reverse DNS data: {e}")
        return "N/A"

# Function to fetch WHOIS data
def fetch_whois(host):
    try:
        whois_info = {}
        for elem in host.findall(".//script[@id='whois-ip']/elem"):
            key = elem.attrib.get('key', 'N/A')
            value = elem.text
            whois_info[key] = value
        return whois_info
    except Exception as e:
        print(f"Error fetching WHOIS data: {e}")
        return {}

# Function to send data to Flask server
def send_data_to_server(data):
    try:
        url = 'http://localhost:5000/api/save'
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("Data successfully sent to the server")
        else:
            print(f"Failed to send data to the server: Status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to send data to the server: {e}")

# Main function
def main(ip_range, rate):
    if not check_masscan():
        print("Error: Masscan is not installed or not found in PATH.")
        return

    run_masscan(ip_range, rate)
    mas_output = 'masscan_output.xml'
    # Check if masscan_output.xml is empty
    if not os.path.exists(mas_output) or os.stat(mas_output).st_size == 0:
        print("No hosts found, Noting to proceed.")
        return
    masscan_tree = ET.parse('masscan_output.xml')
    masscan_root = masscan_tree.getroot()

    for host in masscan_root.findall('host'):
        ip = host.find('address').attrib['addr']
        run_nmap(ip)
        nmap_data = parse_nmap_output(f'nmap_output_{ip}.xml')
        #Nmap output file is no longer needed
        os.remove(f'nmap_output_{ip}.xml')
        send_data_to_server(nmap_data)
        print(f"Data sent for {ip}")

if __name__ == "__main__":
    main("0.0.0.0/0", 10000)

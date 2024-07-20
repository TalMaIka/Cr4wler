# Cr4wler - Network Live Hosts Analyzer.
# Version: 1.0.0
# Date: Jul 21, 2024
# Copyrights © Tal.M


from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hosts.db'
db = SQLAlchemy(app)

class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), unique=True, nullable=False)
    os_name = db.Column(db.String(100))
    os_accuracy = db.Column(db.String(10))
    geolocation = db.Column(db.JSON)
    rdns = db.Column(db.String(100))
    whois = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Port(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)
    port = db.Column(db.String(10))
    service = db.Column(db.String(50))
    version = db.Column(db.String(50))
    product = db.Column(db.String(50))
    banner = db.Column(db.String(255))
    http_title = db.Column(db.String(255))
    ssl_cert = db.Column(db.String(255))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/save', methods=['POST'])
def save_host_data():
    data = request.json
    saved_hosts = []
    rejected_hosts = []

    try:
        for host_data in data:
            ip = host_data['ip']

            # Check if host with this IP already exists
            existing_host = Host.query.filter_by(ip=ip).first()
            if existing_host:
                # Handle duplicate IP case (skip or update logic)
                # For simplicity, skipping duplicate hosts
                print(f"Skipping duplicate host with IP: {ip}")
                rejected_hosts.append(host_data)
                continue

            # Convert timestamp string to datetime
            timestamp_str = host_data['timestamp']
            timestamp = datetime.fromisoformat(timestamp_str)

            # Create new Host object
            host = Host(
                ip=ip,
                os_name=host_data['os_name'],
                os_accuracy=host_data['os_accuracy'],
                geolocation=host_data['geolocation'],
                rdns=host_data['rdns'],
                whois=host_data['whois'],
                timestamp=timestamp
            )
            db.session.add(host)
            db.session.commit()
            saved_hosts.append(host_data)

            # Add ports related to the host
            for port_data in host_data['ports']:
                port = Port(
                    host_id=host.id,
                    port=port_data['port'],
                    service=port_data['service'],
                    version=port_data['version'],
                    product=port_data['product'],
                    banner=port_data['banner'],
                    http_title=port_data['http_title'],
                    ssl_cert=port_data['ssl_cert']
                )
                db.session.add(port)
            db.session.commit()

        return jsonify({
            "message": "Data successfully saved.",
            "saved_hosts": saved_hosts,
            "rejected_hosts": rejected_hosts
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Error: Duplicate IP address encountered."}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

@app.route('/api/fetch', methods=['GET'])
def fetch_host_data():
    hosts = Host.query.all()
    data = []
    for host in hosts:
        host_data = {
            'ip': host.ip,
            'os_name': host.os_name,
            'os_accuracy': host.os_accuracy,
            'geolocation': host.geolocation,
            'rdns': host.rdns,
            'whois': host.whois,
            'timestamp': host.timestamp,
            'ports': []
        }
        ports = Port.query.filter_by(host_id=host.id).all()
        for port in ports:
            port_data = {
                'port': port.port,
                'service': port.service,
                'version': port.version,
                'product': port.product,
                'banner': port.banner,
                'http_title': port.http_title,
                'ssl_cert': port.ssl_cert
            }
            host_data['ports'].append(port_data)
        data.append(host_data)
    return jsonify(data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

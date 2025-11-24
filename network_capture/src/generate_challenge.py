#!/usr/bin/env python3

import os
import subprocess
import time
import shutil
from uuid import uuid4
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import socket
import tempfile

flag = os.environ.get('FLAG', 'ctf{test_flag}')
output_dir = '/app/output' if os.path.isdir('/app/output') else 'output'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Using output directory: {output_dir}")

# Generate password using uuid4().hex
archive_password = uuid4().hex
print(f"Generated password: {archive_password}")

# Create temp directory
temp_dir = tempfile.mkdtemp()

class SimpleHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Password received successfully')
        print(f"[HTTP] Received: {post_data.decode('utf-8')}")
    
    def log_message(self, format, *args):
        pass

def run_http_server():
    server = HTTPServer(('127.0.0.1', 8080), SimpleHTTPHandler)
    server.handle_request()

class SimpleFTPHandler:
    """Minimal FTP server for demonstration"""
    def __init__(self, port=21):
        self.port = port
        self.socket = None
        self.data_socket = None
        self.data_port = 21100
        
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('127.0.0.1', self.port))
        self.socket.listen(1)
        
        # Also prepare data socket for PASV mode
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.data_socket.bind(('127.0.0.1', self.data_port))
        self.data_socket.listen(1)
        
    def accept_connection(self):
        conn, addr = self.socket.accept()
        # Send welcome message
        conn.send(b'220 Simple FTP Server Ready\r\n')
        
        data_conn = None
        
        while True:
            data = conn.recv(1024)
            if not data:
                break
                
            command = data.decode('utf-8', errors='ignore').strip()
            print(f"[FTP] Command: {command}")
            
            if command.startswith('USER'):
                conn.send(b'331 Username OK, need password\r\n')
            elif command.startswith('PASS'):
                conn.send(b'230 Login successful\r\n')
            elif command.startswith('TYPE'):
                conn.send(b'200 Type set\r\n')
            elif command.startswith('PASV'):
                # Return passive mode with data port
                # Port 21100 = (82, 84) in FTP format
                conn.send(b'227 Entering Passive Mode (127,0,0,1,82,84)\r\n')
            elif command.startswith('STOR'):
                conn.send(b'150 Opening data connection\r\n')
                # Accept data connection and receive file data
                try:
                    data_conn, _ = self.data_socket.accept()
                    received_data = b''
                    while True:
                        chunk = data_conn.recv(4096)
                        if not chunk:
                            break
                        received_data += chunk
                    print(f"[FTP] Received {len(received_data)} bytes")
                    data_conn.close()
                    conn.send(b'226 Transfer complete\r\n')
                except Exception as e:
                    print(f"[FTP] Data transfer error: {e}")
                    conn.send(b'426 Connection closed; transfer aborted\r\n')
            elif command.startswith('QUIT'):
                conn.send(b'221 Goodbye\r\n')
                break
            else:
                conn.send(b'200 OK\r\n')
        
        conn.close()
        if data_conn:
            data_conn.close()
        
    def stop(self):
        if self.socket:
            self.socket.close()
        if self.data_socket:
            self.data_socket.close()

def generate_noise_traffic():
    """Generate background noise traffic to make analysis harder"""
    import random
    import string
    
    while True:
        try:
            # Random HTTP requests to random endpoints
            urls = [
                'http://127.0.0.1:9000/api/status',
                'http://127.0.0.1:9001/health',
                'http://127.0.0.1:9002/metrics',
                'http://127.0.0.1:9003/data',
            ]
            
            for _ in range(random.randint(2, 5)):
                try:
                    import urllib.request
                    url = random.choice(urls)
                    data = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(20, 100)))
                    req = urllib.request.Request(url, data=data.encode(), method='POST')
                    urllib.request.urlopen(req, timeout=0.5)
                except:
                    pass
                
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(random.uniform(0.5, 1.5))
        except:
            break

def create_challenge():
    # Install zip utility
    print("Installing zip utility...")
    subprocess.run(['apt-get', 'update'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(['apt-get', 'install', '-y', 'zip', 'curl'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Start tshark capture on loopback - NO PORT FILTER
    pcap_file = '/tmp/traffic.pcap'
    print("Starting tshark capture (all traffic)...")
    tshark_proc = subprocess.Popen(
        ['tshark', '-i', 'lo', '-w', pcap_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Wait for tshark to initialize
    
    # Start noise traffic generators
    print("Starting background noise traffic...")
    noise_threads = []
    for _ in range(3):
        noise_thread = Thread(target=generate_noise_traffic, daemon=True)
        noise_thread.start()
        noise_threads.append(noise_thread)
    
    time.sleep(1)
    
    # Start HTTP server in background thread
    print("Starting HTTP server...")
    http_thread = Thread(target=run_http_server, daemon=True)
    http_thread.start()
    
    time.sleep(1)
    
    # Start FTP server in background thread
    print("Starting FTP server...")
    ftp_server = SimpleFTPHandler()
    ftp_server.start()
    
    ftp_thread = Thread(target=ftp_server.accept_connection, daemon=True)
    ftp_thread.start()
    
    time.sleep(1)
    
    # Create flag file and archive
    print("Creating archive with flag...")
    flag_file = os.path.join(temp_dir, 'flag.txt')
    with open(flag_file, 'w') as f:
        f.write(flag)
    
    # Create password-protected zip
    archive_file = os.path.join(temp_dir, 'secret.zip')
    os.chdir(temp_dir)
    result = subprocess.run(
        ['zip', '-P', archive_password, 'secret.zip', 'flag.txt'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    if result.returncode == 0:
        print(f"Archive created successfully")
    else:
        print(f"Error creating archive: {result.stderr.decode()}")
    
    time.sleep(1)
    
    # Send HTTP POST with password
    print("Sending HTTP POST with password...")
    try:
        import urllib.request
        
        data = f"archive_password={archive_password}".encode('utf-8')
        req = urllib.request.Request('http://127.0.0.1:8080/submit_password', data=data)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"[HTTP] Response: {response.read().decode('utf-8')}")
    except Exception as e:
        print(f"[HTTP] Error: {e}")
    
    time.sleep(1)
    
    # Upload archive via FTP with REAL data transfer
    print("Uploading archive via FTP...")
    try:
        # Control connection
        ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ftp_socket.connect(('127.0.0.1', 21))
        
        # Receive welcome
        response = ftp_socket.recv(1024)
        print(f"[FTP] {response.decode('utf-8', errors='ignore').strip()}")
        
        # Login
        ftp_socket.send(b'USER anonymous\r\n')
        response = ftp_socket.recv(1024)
        print(f"[FTP] {response.decode('utf-8', errors='ignore').strip()}")
        
        ftp_socket.send(b'PASS anonymous@example.com\r\n')
        response = ftp_socket.recv(1024)
        print(f"[FTP] {response.decode('utf-8', errors='ignore').strip()}")
        
        # Set binary mode
        ftp_socket.send(b'TYPE I\r\n')
        response = ftp_socket.recv(1024)
        print(f"[FTP] {response.decode('utf-8', errors='ignore').strip()}")
        
        # Enter passive mode
        ftp_socket.send(b'PASV\r\n')
        response = ftp_socket.recv(1024)
        print(f"[FTP] {response.decode('utf-8', errors='ignore').strip()}")
        
        time.sleep(0.5)
        
        # Open data connection
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect(('127.0.0.1', 21100))
        
        # Send STOR command
        ftp_socket.send(b'STOR secret.zip\r\n')
        response = ftp_socket.recv(1024)
        print(f"[FTP] {response.decode('utf-8', errors='ignore').strip()}")
        
        # Send actual file data through data connection
        with open(archive_file, 'rb') as f:
            archive_data = f.read()
            data_socket.sendall(archive_data)
            print(f"[FTP] Sent {len(archive_data)} bytes of archive data")
        
        data_socket.close()
        time.sleep(0.5)
        
        # Get transfer complete response
        response = ftp_socket.recv(1024)
        print(f"[FTP] {response.decode('utf-8', errors='ignore').strip()}")
        
        # Quit
        ftp_socket.send(b'QUIT\r\n')
        response = ftp_socket.recv(1024)
        print(f"[FTP] {response.decode('utf-8', errors='ignore').strip()}")
        
        ftp_socket.close()
        print("[FTP] Upload completed successfully")
    except Exception as e:
        print(f"[FTP] Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Keep capture running to get all traffic including noise
    time.sleep(5)
    
    # Stop tshark
    print("Stopping tshark...")
    tshark_proc.terminate()
    try:
        tshark_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        tshark_proc.kill()
    
    # Stop FTP server
    ftp_server.stop()
    
    time.sleep(1)
    
    # Copy pcap file to output
    dest_pcap = os.path.join(output_dir, 'traffic.pcap')
    if os.path.exists(pcap_file):
        shutil.copy(pcap_file, dest_pcap)
        print(f"Traffic capture saved to {dest_pcap}")
        
        # Show file size
        size = os.path.getsize(dest_pcap)
        print(f"PCAP file size: {size} bytes")
    else:
        print("ERROR: pcap file not found!")
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    print("\n" + "="*50)
    print("Challenge generation completed!")
    print(f"Password (for testing): {archive_password}")
    print("="*50)

if __name__ == "__main__":
    create_challenge()


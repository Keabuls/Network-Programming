import os
import sys
import socket
import platform
import threading
import time
import struct
from datetime import datetime


# GLOBAL SETTINGS
class GlobalSettings:
    """Simple global socket settings"""
    def __init__(self):
        self.timeout = None
        self.send_buffer = 4096
        self.recv_buffer = 4096
        self.blocking = True
        self.log_file = None
    
    def log_setting(self, message):
        """Log setting changes to file"""
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if self.log_file:
            self.log_file.write(log_message + "\n")
            self.log_file.flush()

# Create global settings instance
g_settings = GlobalSettings()


# UTILITY FUNCTIONS
def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header():
    """Display main menu header"""
    print("=" * 50)
    print(" " * 15 + "MAIN MENU")
    print("=" * 50)
    print()

def display_menu():
    """Display main menu options"""
    print("Please select an option:")
    print()
    print("  [1] Module 1 - Machine Info")
    print("  [2] Module 2 - Echo Test")
    print("  [3] Module 3 - SNTP Time Check")
    print("  [4] Module 4 - Chat")
    print("  [5] Module 5 - Socket Settings")
    print("  [0] Exit Program")
    print()
    print("-" * 50)

def get_user_choice():
    """Get valid user choice"""
    while True:
        choice = input("Enter your choice (0-5): ").strip()
        if choice in ['0', '1', '2', '3', '4', '5']:
            return choice
        print("Invalid input! Please enter a number between 0 and 5.")

def apply_settings_to_socket(sock):
    """Apply global settings to a socket"""
    try:
        sock.settimeout(g_settings.timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, g_settings.send_buffer)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, g_settings.recv_buffer)
        sock.setblocking(g_settings.blocking)
        return True
    except socket.error as e:
        print(f"Error applying settings: {e}")
        return False

# MODULE 1: MACHINE INFORMATION
def module_1():
    clear_screen()
    print("\n>>> Running Module 1: Machine Info <<<\n")
    try:
        # Get hostname
        hostname = socket.gethostname()
        print(f"Host Name: {hostname}")
        # Get all IP addresses
        all_ips = socket.gethostbyname_ex(hostname)[2]
        print(f"All IP Addresses: {all_ips}")
        # Get system information
        print(f"System: {platform.system()}")
        print(f"Node: {platform.platform()}")
        # Get network interfaces (cross-platform compatible)
        print("Network Interfaces:")
        try:
            # Try socket.if_nameindex() first (Linux/Mac)
            interfaces = socket.if_nameindex()
            for idx, name in interfaces:
                print(f"  {idx}: {name}")
        except (AttributeError, OSError):
            # Fallback for Windows or systems where if_nameindex() is not available
            print("  (Interface listing not available on this system)")
            print(f"  Hostname: {hostname}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to return to main menu...")

# MODULE 2: ECHO TEST
def module_2():
    """Echo test - send data and receive it back"""
    clear_screen()

    print("\n>>> Running Module 2: Echo Test <<<\n")
    print(f"  Timeout: {g_settings.timeout if g_settings.timeout else 'None (Blocking)'}")
    print(f"  Send Buffer: {g_settings.send_buffer} bytes")
    print(f"  Receive Buffer: {g_settings.recv_buffer} bytes")
    print(f"  Mode: {'Blocking' if g_settings.blocking else 'Non-blocking'}\n")

    host = 'localhost'
    data_payload = 2048
    backlog = 5
    
    def echo_server(port):
        """Simple echo server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            apply_settings_to_socket(sock)
            
            sock.bind((host, port))
            sock.listen(backlog)
            print(f"Server listening on {host}:{port}")
            
            client, address = sock.accept()
            print(f"Client connected: {address}")
            
            # Receive data
            data = client.recv(data_payload)
            print(f"Received: {data.decode('utf-8')}")
            
            # Send data back
            client.send(data)
            print("Data echoed back to client")
            
            client.close()
            sock.close()
            
        except Exception as e:
            print(f"Server error: {e}")
    
    def echo_client(port):
        """Simple echo client"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            apply_settings_to_socket(sock)
            
            sock.connect((host, port))
            print(f"Connected to {host}:{port}")
            
            # Send message
            message = "Hello from client!"
            print(f"Sending: {message}")
            sock.sendall(message.encode('utf-8'))
            
            # Receive response
            response = sock.recv(data_payload).decode('utf-8')
            print(f"Received: {response}")
            
            # Check if they match
            if message == response:
                print("\n Connection successful, data matches!")
            else:
                print("\n Data mismatch!")
            
            sock.close()
            
        except Exception as e:
            print(f"Client error: {e}")
    
    try:
        port = int(input("Enter port number: "))
        if port < 1 or port > 65535:
            print("Invalid port!")
            input("\nPress Enter to return to main menu...")
            return
        
        # Start server in background
        print("\nStarting server...")
        server_thread = threading.Thread(target=echo_server, args=(port,), daemon=True)
        server_thread.start()
        time.sleep(1)
        
        # Start client
        print("Starting client...\n")
        echo_client(port)
        
        time.sleep(1)
        
    except ValueError:
        print("Invalid input!")
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to return to main menu...")


# MODULE 3: SNTP TIME CHECK
def module_3():

    clear_screen()
    print("\n>>> Running Module 3: SNTP Time Check <<<\n")
    
    NTP_SERVER = "0.uk.pool.ntp.org"
    TIME1970 = 2208988800
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        apply_settings_to_socket(sock)
        
        # Create NTP request
        data = b'\x1b' + 47 * b'\0'
        print(f"Requesting time from {NTP_SERVER}...")
        sock.sendto(data, (NTP_SERVER, 123))
        # Get response
        response, _ = sock.recvfrom(1024)

        # Extract time
        ntp_time = struct.unpack('!12I', response)[10]
        ntp_time -= TIME1970
        
        local_time = time.time()
        offset = local_time - ntp_time  
        
        print(f"\nNTP Time: {time.ctime(ntp_time)}")
        print(f"Local Time: {time.ctime(local_time)}")
        print(f"Offset: {offset:.2f} seconds")
        
        sock.close()
        
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to return to main menu...")


# MODULE 4: SIMPLE CHAT
def module_4():

    clear_screen()
    print("\n>>> Running Module 4: Chat <<<\n")
    
    class ChatServer:
        def __init__(self, host='localhost', port=5000):
            self.host = host
            self.port = port
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client = None
        
        def start(self):
            try:
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                apply_settings_to_socket(self.server)
                
                self.server.bind((self.host, self.port))
                self.server.listen(1)
                print(f"Server waiting on {self.host}:{self.port}")
                
                self.client, addr = self.server.accept()
                print(f"Client connected: {addr}\n")
                
                # Start threads for send/receive
                send_thread = threading.Thread(target=self.send_msg)
                recv_thread = threading.Thread(target=self.recv_msg)
                
                send_thread.daemon = True
                recv_thread.daemon = True

                send_thread.start()
                recv_thread.start()
                
                send_thread.join()
                recv_thread.join()
                
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                self.close()
        
        def send_msg(self):
            """Send message from server"""
            while True:
                try:
                    msg = input("Server: ")
                    if msg:
                        self.client.send(msg.encode('utf-8'))
                except:
                    break
        
        def recv_msg(self):
            """Receive message from client"""
            while True:
                try:
                    msg = self.client.recv(1024).decode('utf-8')
                    if msg:
                        print(f"Client: {msg}")
                    else:
                        break
                except:
                    break
        
        def close(self):
            if self.client:
                self.client.close()
            self.server.close()
    
    class ChatClient:
        def __init__(self, host='localhost', port=5000):
            self.host = host
            self.port = port
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.log_file = open(f"chat_log_{datetime.now().strftime('%H-%M-%S')}.txt", 'w')
        
        def start(self):
            try:
                apply_settings_to_socket(self.socket)
                self.socket.connect((self.host, self.port))
                print(f"Connected to {self.host}:{self.port}\n")
                
                send_thread = threading.Thread(target=self.send_msg)
                recv_thread = threading.Thread(target=self.recv_msg)
                
                send_thread.daemon = True
                recv_thread.daemon = True

                send_thread.start()
                recv_thread.start()
                
                send_thread.join()
                recv_thread.join()
                
            except Exception as e:
                print(f"Client error: {e}")
            finally:
                self.close()
        
        def send_msg(self):
            """Send message from client"""
            while True:
                try:
                    msg = input("Client: ")
                    if msg:
                        self.socket.send(msg.encode('utf-8'))
                        self.log_file.write(f"Client: {msg}\n")
                        self.log_file.flush()
                except:
                    break
        
        def recv_msg(self):
            """Receive message from server"""
            while True:
                try:
                    msg = self.socket.recv(1024).decode('utf-8')
                    if msg:
                        print(f"Server: {msg}")
                        self.log_file.write(f"Server: {msg}\n")
                        self.log_file.flush()
                    else:
                        break
                except:
                    break
        
        def close(self):
            self.socket.close()
            if self.log_file:
                self.log_file.close()
                print(f"\nChat saved to log file")
    
    try:
        mode = input("Choose mode (server/client): ").strip().lower()
        
        if mode == 'server':
            port = int(input("Port (default 5000): ") or "5000")
            server = ChatServer(port=port)
            server.start()
        elif mode == 'client':
            host = input("Host (default localhost): ").strip() or 'localhost'
            port = int(input("Port (default 5000): ") or "5000")
            client = ChatClient(host, port)
            client.start()
        else:
            print("Invalid mode!")
    except Exception as e:
        print(f"Error: {e}")
    
    input("\nPress Enter to return to main menu...")


# MODULE 5: SOCKET SETTINGS
def module_5():
    """Configure socket settings"""
    clear_screen()
    print("\n>>> Running Module 5: Socket Settings <<<\n")
    
    # Open log file
    log_filename = f"settings_log_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.txt"
    g_settings.log_file = open(log_filename, 'w')
    g_settings.log_setting(f"Settings log started - File: {log_filename}")
    g_settings.log_setting("=" * 50)
    
    while True:
        print("=" * 50)
        print("SOCKET SETTINGS")
        print("=" * 50)
        print(f"\nCurrent Settings:")
        print(f"  Timeout: {g_settings.timeout if g_settings.timeout else 'None (Blocking)'}")
        print(f"  Send Buffer: {g_settings.send_buffer} bytes")
        print(f"  Receive Buffer: {g_settings.recv_buffer} bytes")
        print(f"  Mode: {'Blocking' if g_settings.blocking else 'Non-blocking'}")
        print("\nOptions:")
        print("  [1] Set Timeout")
        print("  [2] Set Buffer Size")
        print("  [3] Set Blocking Mode")
        print("  [4] Test Connection")
        print("  [5] Reset to Default")
        print("  [0] Back")
        print("-" * 50)
        
        choice = input("Enter choice: ").strip()
        
        if choice == '0':
            break
        
        elif choice == '1':
            try:
                timeout_input = input("Enter timeout (seconds, 0 for blocking): ").strip()
                g_settings.timeout = float(timeout_input) if timeout_input != '0' else None
                timeout_display = g_settings.timeout if g_settings.timeout else "Blocking (None)"
                g_settings.log_setting(f"Timeout changed to: {timeout_display} seconds")
                print(" Timeout updated")
            except:
                print("Invalid input!")
        
        elif choice == '2':
            try:
                send = int(input("Send buffer size (1024-65536): ").strip())
                recv = int(input("Receive buffer size (1024-65536): ").strip())
                if 1024 <= send <= 65536 and 1024 <= recv <= 65536:
                    g_settings.send_buffer = send
                    g_settings.recv_buffer = recv
                    g_settings.log_setting(f"Buffer sizes changed - Send: {send} bytes, Receive: {recv} bytes")
                    print(" Buffer sizes updated")
                else:
                    print("Invalid range!")
            except:
                print("Invalid input!")
        
        elif choice == '3':
            mode = input("Blocking (true/false): ").strip().lower()
            g_settings.blocking = mode == 'true'
            mode_display = "Blocking" if g_settings.blocking else "Non-blocking"
            g_settings.log_setting(f"Mode changed to: {mode_display}")
            print(" Mode updated")
        
        elif choice == '4':
            try:
                host = input("Host (default localhost): ").strip() or 'localhost'
                port = int(input("Port (default 80): ").strip() or "80")
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                apply_settings_to_socket(sock)
                
                g_settings.log_setting(f"Testing connection to {host}:{port}")
                print(f"\nConnecting to {host}:{port}...")
                sock.connect((host, port))
                g_settings.log_setting(f"Connection successful to {host}:{port}")
                print(" Connection successful!")
                sock.close()
            except Exception as e:
                g_settings.log_setting(f"Connection failed to {host}:{port} - Error: {e}")
                print(f" Connection failed: {e}")
        
        elif choice == '5':
            g_settings.timeout = None
            g_settings.send_buffer = 4096
            g_settings.recv_buffer = 4096
            g_settings.blocking = True
            g_settings.log_setting("Settings reset to default values")
            print(" Settings reset to default")
        
        else:
            print("Invalid choice!")
        
        input("\nPress Enter to continue...")
        clear_screen()
    
    # Close log file
    if g_settings.log_file:
        g_settings.log_setting("=" * 50)
        g_settings.log_setting(f"Settings log ended")
        g_settings.log_file.close()
        print(f"\n Settings saved to: {log_filename}")
    
    input("\nPress Enter to return to main menu...")


# MAIN PROGRAM
def main():
    """Main menu loop"""
    menu_actions = {
        '1': module_1,
        '2': module_2,
        '3': module_3,
        '4': module_4,
        '5': module_5,
    }
    
    while True:
        clear_screen()
        display_header()
        display_menu()
        
        choice = get_user_choice()
        
        if choice == '0':
            clear_screen()
            print("\nThank you for using the program!")
            print("Exiting...\n")
            sys.exit(0)
        else:
            menu_actions[choice]()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\n\nProgram interrupted.")
        print("Exiting...\n")
        sys.exit(0)
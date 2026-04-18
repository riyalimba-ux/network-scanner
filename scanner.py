import socket
import threading
from queue import Queue

# Number of threads (increase for faster scan)
THREADS = 150

# Queue and Lock
queue = Queue()
lock = threading.Lock()


def scan_port(target_ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)

        result = sock.connect_ex((target_ip, port))

        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "Unknown"

            with lock:
                print(f"[OPEN] Port {port} ({service})")

        sock.close()

    except:
        pass


def worker(target_ip):
    while not queue.empty():
        port = queue.get()
        scan_port(target_ip, port)
        queue.task_done()


def main():
    # Get target
    target = input("Enter target (IP or domain): ").strip()

    if not target:
        print("❌ No input provided")
        return

    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print("❌ Invalid hostname or IP")
        return

    # Get port range
    try:
        start_port = int(input("Enter start port: "))
        end_port = int(input("Enter end port: "))
    except ValueError:
        print("❌ Ports must be numbers")
        return

    # Validate range
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("❌ Invalid port range (1–65535)")
        return

    print(f"\n🔍 Scanning Target: {target_ip}")
    print(f"📡 Port Range: {start_port} - {end_port}")
    print("Please wait...\n")

    # Add ports to queue
    for port in range(start_port, end_port + 1):
        queue.put(port)

    # Create threads
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(target_ip,))
        t.start()
        threads.append(t)

    # Wait for all tasks
    queue.join()

    print("\n✅ Scan Completed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Scan stopped by user")
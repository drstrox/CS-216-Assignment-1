
import streamlit as st
import socket
import threading

# Dictionary to keep track of peers that have sent us messages
active_peers = {}
port_number = None

# Streamlit UI
st.set_page_config(page_title="P2P Messaging App", layout="wide")
st.title("Peer-to-Peer Messaging")
st.sidebar.header("Configuration")
name = st.sidebar.text_input("Enter your name (Team Name):")
port_number = st.sidebar.number_input("Enter your port number:", min_value=1024, max_value=65535, step=1)

if st.sidebar.button("Start Server"):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except Exception:
        pass
    server_socket.bind(("0.0.0.0", port_number))
    server_socket.listen(5)
    st.session_state["server_socket"] = server_socket
    st.sidebar.success(f"Server started on port {port_number}")
    threading.Thread(target=receive_messages, args=(server_socket,), daemon=True).start()

def receive_messages(server_socket):
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            peer_ip, peer_port = client_address
            message = client_socket.recv(1024).decode().strip()
            if message == "Connection Request":
                active_peers[(peer_ip, peer_port)] = "Connected"
                client_socket.sendall("Connection Acknowledged".encode())
            elif message == "Connection Acknowledged":
                active_peers[(peer_ip, peer_port)] = "Connected"
            else:
                active_peers[(peer_ip, peer_port)] = "Connected"
            client_socket.close()
        except Exception as e:
            st.sidebar.error(f"Error receiving message: {e}")

def send_message(target_ip, target_port, message):
    global port_number
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception:
            pass
        client_socket.bind(("", port_number))
        client_socket.connect((target_ip, target_port))
        client_socket.sendall(message.encode())
        if message == "Connection Request":
            ack = client_socket.recv(1024).decode().strip()
            if ack == "Connection Acknowledged":
                active_peers[(target_ip, target_port)] = "Connected"
        client_socket.close()
    except Exception as e:
        st.error(f"Failed to send message to {target_ip}:{target_port} - {e}")

st.subheader("Send Message")
target_ip = st.text_input("Enter recipient's IP address:")
target_port = st.number_input("Enter recipient's port number:", min_value=1024, max_value=65535, step=1)
message = st.text_area("Enter your message:")
if st.button("Send Message"):
    send_message(target_ip, target_port, message)
    st.success("Message sent!")

st.subheader("Active Peers")
if active_peers:
    for (ip, port), status in active_peers.items():
        st.write(f"{ip}:{port} - {status}")
else:
    st.write("No active peers.")

import socket
import random

def random_address():
    private_ip_of_this_computer = socket.gethostbyname(socket.gethostname())
    
    # Function to find an unoccupied port
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((private_ip_of_this_computer, 0))  # Bind to an available port
            return s.getsockname()[1]  # Return the port number

    randomly_selected_free_port = find_free_port()
    return f'{private_ip_of_this_computer}:{randomly_selected_free_port}'
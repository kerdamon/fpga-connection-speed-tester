import socket
import multiprocessing

class FpgaMockup:
    def __init__(self, setup_ip = '127.0.0.1'):
        self.setup_ip = setup_ip
        self.setup_sock_12666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_14666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_15666 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.setup_sock_12666.bind((setup_ip, 12666))
        self.setup_sock_14666.bind((setup_ip, 14666))
        self.setup_sock_15666.bind((setup_ip, 15666))
        self.on = multiprocessing.Value('b', False)
        self.mode = b'11'
        self.padding = multiprocessing.Value('i', 0)
        self.number_of_test_packets = multiprocessing.Value('i', 10)

    def listening_on_12666(self):
        print("Listening on 12666...")
        data = self.setup_sock_12666.recvfrom(16)[0]
        print("Finished Listening on 12666.")

        print(f'Received setup, setup message: {data}')
        intiger = int.from_bytes(data, 'big')
        bits = "{0:b}".format(intiger)
        print(bits)
        self.mode = bits[-10:-8]            #[9:8]
        print(f'Mode set to: {self.mode}')
        print(bool(int(bits[-8:-7])))
        self.on.value = bool(int(bits[-8:-7]))

    def listening_on_14666(self):
        print("Listening on 14666...")
        data = self.setup_sock_14666.recvfrom(16)[0]
        print("Finished Listening on 14666.")

        print(f'Received setup, setup message: {data}')
        self.padding.value = int.from_bytes(data, 'big')
        print(f"Set padding to {self.padding.value}")

    def listening_on_15666(self):
        print("Listening on 15666...")
        data = self.setup_sock_15666.recvfrom(64)[0]
        print("Finished Listening on 15666.")

        print(f'Received setup, setup message: {data}')
        self.number_of_test_packets.value = int.from_bytes(data, 'big')
        print(f"Set number of packets to {self.number_of_test_packets.value}")

    def sending(self, speed_testing_ip = '127.0.0.2', speed_testing_udp_port = 5005):
        print(f'Sending {self.number_of_test_packets.value} packets')
        for _ in range(self.number_of_test_packets.value):
            self.setup_sock_12666.sendto(b'Speed test package',
                            (speed_testing_ip, speed_testing_udp_port))

if __name__ == "__main__":
    testing_fpga = FpgaMockup()
    while(testing_fpga.on.value == False):
        p1 = multiprocessing.Process(target=testing_fpga.listening_on_12666)
        p2 = multiprocessing.Process(target=testing_fpga.listening_on_14666)
        p3 = multiprocessing.Process(target=testing_fpga.listening_on_15666)

        p1.start()
        p2.start()
        p3.start()

        p1.join(1)
        p2.join(1)
        p3.join(1)

    testing_fpga.sending()
import time
import socket


class ClientError(Exception):
    pass


class Client:

    def __init__(self, host, port, timeout=15):
        self._host = host
        self._port = port
        self._timeout = timeout

    def do_request(self, query):
        with socket.create_connection((self._host, self._port), self._timeout) as sock:

            sock.sendall(query.encode())
            received = sock.recv(1024)

        return received.decode()

    def put(self, metric_name, metric_value, timestamp=int(time.time())):
        put_query = f"put {metric_name} {metric_value} {timestamp}\n"
        result = self.do_request(put_query)
        print("result: ", result)
        if result != "ok\n\n":
            raise ClientError

    def get(self, metric_name):

        if metric_name is "*":
            get_query = "get *\n"
        else:
            get_query = f"get {metric_name}\n"

        result = self.do_request(get_query)

        if not result.startswith("ok") or not result.endswith("\n\n"):
            raise ClientError

        if result == "ok\n\n":
            return {}

        # delete "ok\n" and return list of clear strings
        results = result[3:].splitlines()
        result_dict = {}
        for string in results:

            if string == '':
                continue

            elements = string.split()
            if elements[0] in result_dict:
                before_list = result_dict[elements[0]]
                before_list.append((int(elements[2]), float(elements[1])))
                after_list = sorted(before_list, key=lambda x: x[0])
                result_dict[elements[0]] = after_list
            else:
                result_dict[elements[0]] = [(int(elements[2]), float(elements[1]))]

        return result_dict


client = Client('127.0.0.1', 8888)
client.put("cpu", 2300, timestamp=10)
client.put("cpu", 2100, timestamp=13)
client.get("*")

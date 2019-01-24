import asyncio


class Storage:
    """Singleton class to store metrics"""

    __instance = None

    def __init__(self):
        if type(self).__instance:
            raise Exception("This class is a singleton!")
        self._storage = {}
        type(self).__instance = self

    @classmethod
    def get_instance(cls):
        return cls.__instance or Storage()

    def parse_put(self, query):

        query = query[4:len(query) - 1]  # delete put and \n
        elements = query.split()

        try:
            key_p = elements[0]
            value_p = float(elements[1])
            timestamp_p = int(elements[2])

            if key_p in self._storage:

                # if metric for this time exists, rewrite value
                for idx, (value, timestamp) in enumerate(self._storage[key_p]):
                    if timestamp == timestamp_p:
                        item = (value_p, timestamp_p)
                        self._storage[key_p][idx] = item
                        return "ok\n\n"

                # if metric for this time doesn't exist, append new one
                self._storage[key_p].append(
                    (value_p, timestamp_p)
                )

            else:
                self._storage[key_p] = [(value_p, timestamp_p)]

        except IndexError:
            answer = "error\nwrong command\n\n"
        except TypeError:
            answer = "error\nwrong command\n\n"
        else:
            answer = "ok\n\n"

        return answer

    def parse_get(self, query):
        mask = query[4:len(query) - 1]  # delete get and \n
        if mask == '':
            return "error\nwrong command\n\n"

        answer = "ok\n"
        if mask == "*":
            for key in self._storage:
                answer += self.get(key)
        else:
            answer += self.get(mask)

        answer += "\n"
        return answer

    def get(self, key):

        string = ''
        for value in self._storage[key]:
            string += f"{key} {value[0]} {value[1]}\n"

        return string


def run_server(host, port):

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_request, host, port, loop=loop)
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


async def handle_request(reader, writer):

    data = await reader.read(1024)
    message = data.decode()
    answer = parse_input(message)
    print("answer:", answer)
    writer.write(answer.encode())
    writer.close()


def parse_input(query):
    if query.startswith("put") and query.endswith("\n"):
        answer = Storage.get_instance().parse_put(query)

    elif query.startswith("get") and query.endswith("\n"):
        answer = Storage.get_instance().parse_get(query)

    else:
        answer = "error\nwrong command\n\n"

    return answer


if __name__ == "__main__":
    run_server("127.0.0.1", 8888)

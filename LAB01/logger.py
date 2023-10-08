from helper import Colors, printc


class Logger:
    """
    A logger that only actually logs when msg is different from last one.
    """

    colors = [Colors.BLUE, Colors.RED, Colors.GREEN, Colors.CYAN, Colors.YELLOW]

    state: str | tuple[str, ...] = "default"

    def log(self, payload: str | tuple[str, ...]):
        if payload == self.state:
            return
        log = ""

        if type(payload) == str:
            color = self.colors[hash(payload) % len(self.colors)]
            if type(self.state) != tuple or self.state[0] != payload:
                log = "[+] " + payload
                self.state = payload
        else:
            color = self.colors[hash(payload[0]) % len(self.colors)]
            if (type(self.state) != tuple and self.state != payload[0]) and payload[
                0
            ] != self.state[0]:
                log = f"[+] {payload[0]}"

            s = " ".join(payload[1:])
            if s:
                log += ("\n" if log else "") + "    " + s

            self.state = payload

        if log:
            printc(color, log)

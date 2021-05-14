import subprocess
import threading
import asyncio
import time
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.bot import CCBot


class AlreadyRunnning(Exception):
    def __init__(self):
        super().__init__("The MC Server is already running!")


class McClient:
    def __init__(self, path: str, bot: "CCBot"):
        self.bot = bot
        self.path = path

        self.proc: subprocess.Popen[str] = None

        self.outq: List[str] = []
        self.to_log: List[str] = []
        self.outq_read_thread: threading.Thread = None

    def _sender_thread(self):
        while True:
            time.sleep(3)
            to_send = "\n".join([lin.strip for lin in self.to_log])
            self.bot.logging_hook.send(to_send)

    def _out_reader(self):
        for line in iter(self.proc.stdout.readline, b""):
            line: str = line.decode()
            self.outq.append(line)
            self.to_log.append(line)
            print(line, end="")

    def launch(self):
        if self.proc:
            raise AlreadyRunnning()

        self.proc = subprocess.Popen(
            [f"cd {self.path} && ./bedrock_server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        self.outq_read_thread = threading.Thread(target=self._out_reader)
        self.outq_read_thread.start()

    def close(self):
        self.proc.terminate()
        self.outq_read_thread.join()
        self.proc = None
        self.outq_read_thread = None

    async def run_command(self, command_str: str) -> str:
        self.outq = []
        self.proc.stdin.write(bytes(command_str + "\n", "utf8"))
        self.proc.stdin.flush()
        await asyncio.sleep(0.5)
        return "".join(self.outq)

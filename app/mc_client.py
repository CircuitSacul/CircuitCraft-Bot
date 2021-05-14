import subprocess
import threading
import asyncio
from typing import List


class AlreadyRunnning(Exception):
    def __init__(self):
        super().__init__("The MC Server is already running!")


class McClient:
    def __init__(self):
        self.proc: subprocess.Popen[str] = None

        self.outq: List[str] = []
        self.outq_read_thread: threading.Thread = None

    def _out_reader(self):
        for line in iter(self.proc.stdout.readline, b""):
            line = line.decode()
            self.outq.append(line)
            print(line, end="")

    def launch(self):
        if self.proc:
            raise AlreadyRunnning()

        self.proc = subprocess.Popen(
            ["cd ~/circuitcraft && ./bedrock_server"],
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
        await asyncio.sleep(0.24)
        return "".join(self.outq)

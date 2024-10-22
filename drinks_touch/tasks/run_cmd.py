import subprocess

from tasks.base import BaseTask


class RunCmdTask(BaseTask):
    """
    Allows to run one or more shell commands.

    Subclass and override either:
    - `CMD` to run a single command
    - `CMDS` to run multiple commands
    """

    CMD = ["echo", "Hello, World!"]

    def run(self):
        for cmd in self.CMDS:
            if self.sig_killed:
                break
            self.logger.info(f"$ {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            while process.poll() is None:
                if self.sig_killed:
                    self.logger.info(f"Killing PID {process.pid}")
                    process.kill()
                    raise Exception("Process killed")
            for line in process.stdout.readlines():
                self.logger.info(line.decode().strip())
            if process.returncode != 0:
                raise Exception(process.returncode)

    @property
    def LABEL(self):
        cmd = "; ".join([" ".join(c) for c in self.CMDS])
        return f"$ {cmd}"

    @property
    def CMDS(self):
        return [self.CMD]


class GitFetchTask(RunCmdTask):
    CMDS = (
        ["git", "fetch"],
        [
            "git",
            "log",
            "-5",
            "--oneline",
            "--all",
            "--reverse",
            "--format=format:%h %<(6,trunc)%D %<(7,trunc)%an %<(28,trunc)%s",
        ],
    )

import subprocess

import config
from tasks.base import BaseTask


class RunCmdTask(BaseTask):
    """
    Allows to run one or more shell commands.

    Subclass and override either:
    - `CMD` to run a single command
    - `CMDS` to run multiple commands
    """

    CMD = ["echo", "Hello, World!"]
    PWD = None

    def run(self):
        for cmd in self.CMDS:
            if self.sig_killed:
                break
            self.logger.info(f"$ {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.PWD,
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
        ["git", "fetch", "-p"],
        [
            "git",
            "log",
            "-100",
            "--oneline",
            "--all",
            "--reverse",
            "--format=format:%h %<(6,trunc)%D %<(7,trunc)%an %<(28,trunc)%s",
        ],
    )


class UpdateAndRestartTask(RunCmdTask):
    ON_STARTUP = False
    PWD = config.REPO_PATH
    CMDS = (
        ["git", "checkout", "master"],
        ["git", "merge", "--ff-only", "origin/master"],
        ["sleep", "7"],
        ["sudo", "systemctl", "restart", "drinks-touch"],
    )


class RestartTask(RunCmdTask):
    ON_STARTUP = False
    PWD = config.REPO_PATH
    CMDS = (["sudo", "systemctl", "restart", "drinks-touch"],)


class CheckoutAndRestartTask(RunCmdTask):
    ON_STARTUP = False
    PWD = config.REPO_PATH

    def __init__(self, revision: str):
        self.revision = revision
        super().__init__()

    @property
    def CMDS(self):
        return (
            ["git", "checkout", self.revision],
            ["sleep", "7"],
            ["sudo", "systemctl", "restart", "drinks-touch"],
        )

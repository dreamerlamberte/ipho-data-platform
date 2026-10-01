"""Run fixed pipeline stages as a single background job with a captured log.

Only the stages defined here can run; no user input reaches the command line.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
from collections import deque
from datetime import UTC, datetime

from ipho_api.settings import (
    DBT_PROJECT,
    INGEST_SOURCE,
    LAKE_PATH,
    ROOT,
    SOURCE_DIR,
    WAREHOUSE_PATH,
)


def _dbt() -> str:
    return shutil.which("dbt") or os.path.join(os.path.dirname(sys.executable), "dbt")


STAGES: dict[str, list[list[str]]] = {
    "generate": [[sys.executable, "-m", "ipho_synth.generate", "--out", str(SOURCE_DIR)]],
    "ingest": [[sys.executable, "-m", "ipho_ingest.extract", "--source", INGEST_SOURCE,
                "--source-dir", str(SOURCE_DIR), "--lake", str(LAKE_PATH)]],
    "transform": [[_dbt(), "--no-use-colors", "build", "--project-dir", str(DBT_PROJECT),
                   "--profiles-dir", str(DBT_PROJECT)]],
}
STAGES["all"] = STAGES["generate"] + STAGES["ingest"] + STAGES["transform"]


class PipelineJob:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.log: deque[str] = deque(maxlen=400)
        self.stage: str | None = None
        self.state = "idle"  # idle | running | succeeded | failed
        self.started_at: str | None = None
        self.finished_at: str | None = None

    def status(self) -> dict:
        return {"stage": self.stage, "state": self.state, "started_at": self.started_at,
                "finished_at": self.finished_at, "log": list(self.log)}

    def start(self, stage: str) -> bool:
        with self._lock:
            if self.state == "running":
                return False
            self.stage, self.state = stage, "running"
            self.started_at = datetime.now(UTC).isoformat()
            self.finished_at = None
            self.log.clear()
        threading.Thread(target=self._run, args=(stage,), daemon=True).start()
        return True

    def _run(self, stage: str) -> None:
        env = {**os.environ,
               "PYTHONPATH": os.pathsep.join([str(ROOT / "generator"), str(ROOT / "ingestion")]),
               "LAKE_PATH": str(LAKE_PATH), "WAREHOUSE_PATH": str(WAREHOUSE_PATH)}
        env.setdefault("PII_HASH_SALT", "local-dev-salt-not-for-production")
        WAREHOUSE_PATH.parent.mkdir(parents=True, exist_ok=True)
        ok = True
        for cmd in STAGES[stage]:
            self.log.append(f"$ {os.path.basename(cmd[0])} {' '.join(cmd[1:3])} …")
            proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True)
            assert proc.stdout
            for line in proc.stdout:
                self.log.append(line.rstrip())
            if proc.wait() != 0:
                ok = False
                break
        self.state = "succeeded" if ok else "failed"
        self.finished_at = datetime.now(UTC).isoformat()


job = PipelineJob()

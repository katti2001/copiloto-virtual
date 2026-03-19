import time
from enum import Enum, auto
from typing import Dict, Optional, Tuple


class State(Enum):
    NORMAL = auto()
    RISK = auto()
    ALERT = auto()


class FatigueStateMachine:
    def __init__(self, cooldown_sec: int):
        self.state = State.NORMAL
        self.cooldown_sec = cooldown_sec
        self.last_alert_ts = 0.0
        self.pending_alert = False

    def update(self, signs: Dict[str, bool]) -> State:
        now = time.time()
        triggered = signs.get("eyes_closed") or signs.get("yawn") or signs.get("head_down")

        if self.state in (State.NORMAL, State.RISK):
            if triggered:
                self.state = State.RISK
                if now - self.last_alert_ts > self.cooldown_sec:
                    self.pending_alert = True
            else:
                self.state = State.NORMAL
                self.pending_alert = False
        elif self.state == State.ALERT:
            # Se gestiona externamente
            self.pending_alert = False
        return self.state

    def reset_after_alert(self):
        self.state = State.NORMAL
        self.last_alert_ts = time.time()
        self.pending_alert = False

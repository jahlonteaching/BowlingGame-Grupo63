from abc import ABC, abstractmethod
from dataclasses import dataclass

from bowlinggame.model.bowling_errors import FramePinsExceededError, ExtraRollWithOpenTenthFrameError, \
    RollWithGameCompletedError


@dataclass
class Roll:
    pins: int


class Frame(ABC):

    def __init__(self):
        self.rolls: list[Roll] = []
        self.next_frame: Frame | None = None

    def is_strike(self):
        return len(self.rolls) > 0 and self.rolls[0].pins == 10

    def is_spare(self):
        return len(self.rolls) == 2 and self.rolls[0].pins + self.rolls[1].pins == 10

    @property
    def total_pins(self):
        return sum(roll.pins for roll in self.rolls)

    @abstractmethod
    def add_roll(self, pins: int):
        raise NotImplementedError

    @abstractmethod
    def score(self) -> int:
        raise NotImplementedError

    def __str__(self) -> str:
        if len(self.rolls) == 0:
            return ""
        elif len(self.rolls) == 1:
            if self.is_strike():
                return "X"
            else:
                return f"{self.rolls[0].pins} | "
        elif len(self.rolls) == 2:
            if self.is_spare():
                return f"{self.rolls[0].pins} | /"
            else:
                return f"{self.rolls[0].pins} | {self.rolls[1].pins}"


class NormalFrame(Frame):

    def __init__(self):
        super().__init__()

    def add_roll(self, pins: int):
        if pins + self.total_pins > 10:
            raise FramePinsExceededError("A frame's rolls cannot exceed 10 pins")

        if len(self.rolls) < 2:
            self.rolls.append(Roll(pins))

    def score(self) -> int:
        points = self.total_pins
        if self.is_strike():
            if len(self.next_frame.rolls) == 2:
                points += self.next_frame.total_pins
            elif len(self.next_frame.rolls) == 1:
                points += self.next_frame.rolls[0].pins
                if self.next_frame.next_frame is not None and len(self.next_frame.next_frame.rolls) > 0:
                    points += self.next_frame.next_frame.rolls[0].pins
        elif self.is_spare():
            if len(self.next_frame.rolls) > 0:
                points += self.next_frame.rolls[0].pins
        return points


class TenthFrame(Frame):
    def __init__(self):
        super().__init__()
        self.extra_roll: Roll | None = None

    def add_roll(self, pins: int):
        if not self.is_strike() and not self.is_spare():
            if pins + self.total_pins > 10:
                raise FramePinsExceededError("A frame's rolls cannot exceed 10 pins")

        if len(self.rolls) < 2:
            self.rolls.append(Roll(pins))
        else:
            if self.is_strike() or self.is_spare():
                if self.extra_roll is None:
                    self.extra_roll = Roll(pins)
                else:
                    raise RollWithGameCompletedError("Can't throw a roll with a completed game")
            else:
                raise ExtraRollWithOpenTenthFrameError("Can't throw an extra roll with an open tenth frame")

    def score(self) -> int:
        points = self.total_pins
        if self.extra_roll is not None:
            points += self.extra_roll.pins
        return points


class BowlingGame:

    def __init__(self):
        self.frames: list[Frame] = []
        self._init_frames()
        self.current_frame_index: int = 0
        self.roll_count: int = 0

    def _init_frames(self):
        frame = NormalFrame()
        for i in range(9):
            if i < 8:
                next_frame = NormalFrame()
            else:
                next_frame = TenthFrame()
            frame.next_frame = next_frame
            self.frames.append(frame)
            frame = next_frame

        self.frames.append(frame)

    def restart(self):
        self.frames.clear()
        self._init_frames()
        self.current_frame_index = 0
        self.roll_count = 0

    def roll(self, pins: int):
        self.roll_count += 1
        current_frame: Frame = self.frames[self.current_frame_index]
        current_frame.add_roll(pins)
        if self.current_frame_index < 9 and (current_frame.is_strike() or len(current_frame.rolls) == 2):
            self.current_frame_index += 1

    def score(self) -> int:
        return sum(frame.score() for frame in self.frames)

    def __len__(self) -> int:
        return self.roll_count

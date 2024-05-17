class BowlingError(Exception):
    pass


class FramePinsExceededError(BowlingError):
    """
    Raised when the number the pins in a frame exceeds 10
    """
    pass


class ExtraRollWithOpenTenthFrameError(BowlingError):
    """
    Raised when an extra roll is added to an open tenth frame
    """
    pass
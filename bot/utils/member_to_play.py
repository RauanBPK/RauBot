from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from discord import Member


@dataclass
class MemberToPlay:
    member: Member
    time_to_play: Optional[datetime] = None

    def __str__(self):
        return str(self.to_dict())

    def __post_init__(self):
        if isinstance(self.time_to_play, str):
            try:
                self.time_to_play = datetime.strptime(self.time_to_play, "%H:%M")
            except (TypeError, ValueError):
                self.time_to_play = None

    @property
    def name_and_time(self):
        formatted_string = f"{self.display_name}"
        if self.time_to_play:
            formatted_string += f" ({self.time_to_play_str})"
        return formatted_string

    @property
    def mention_and_time(self):
        formatted_string = f"{self.mention}"
        if self.time_to_play:
            formatted_string += f" ({self.time_to_play_str})"
        return formatted_string

    @property
    def id(self):
        return self.member.id

    @property
    def name(self):
        return self.member.name

    @property
    def display_name(self):
        return self.member.display_name

    @property
    def mention(self):
        return self.member.mention

    @property
    def voice(self):
        return self.member.voice

    @property
    def move_to(self):
        return self.member.move_to

    @property
    def time_to_play_str(self):
        return self.time_to_play.strftime("%H:%M") if self.time_to_play else ""

    def to_dict(self):
        return {"member": self.member.id, "time_to_play": self.time_to_play_str}

    @classmethod
    def latest_play_hour(cls, members_to_play: List["MemberToPlay"]) -> Optional[datetime]:
        latest_play_hour = None
        for member_to_play in members_to_play:
            if member_to_play.time_to_play:
                if not latest_play_hour or member_to_play.time_to_play > latest_play_hour:
                    latest_play_hour = member_to_play.time_to_play
        return latest_play_hour

    @classmethod
    def from_dict(cls, data, ctx=None):
        member_id = data["member"]
        member = ctx.get_user(member_id) if ctx and member_id else None
        try:
            time_to_play = datetime.strptime(data["time_to_play"], "%H:%M") if data["time_to_play"] else None
        except ValueError:
            time_to_play = None  # Set to None in case of parsing error
        return cls(member=member, time_to_play=time_to_play)

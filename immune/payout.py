from enum import Enum


BLOCKCHAIN_PAYOUT_TITLES = ["Smart Contracts and Blockchain"]
WEBAPP_PAYOUT_TITLES = ["Web and Apps"]


class PayoutEnum(str, Enum):
    BLOCKCHAIN = "BLOCKCHAIN"
    WEB = "WEB"
    OTHER = "OTHER"

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_text(cls, text: str) -> "PayoutEnum":
        text = text.strip()
        btitles = [x.lower() for x in BLOCKCHAIN_PAYOUT_TITLES]
        if text.lower() in btitles:
            return PayoutEnum.BLOCKCHAIN
        wtitles = [x.lower() for x in WEBAPP_PAYOUT_TITLES]
        if text.lower() in wtitles:
            return PayoutEnum.WEB
        return PayoutEnum.OTHER


class Payout:
    def __init__(self, level, payout: str, type_: PayoutEnum, sort: int):
        self.level: str = level
        self.payout: str = payout
        self.type: PayoutEnum = type_
        self.sort: int = sort

    def to_dict(self):
        return {
            "payout": self.payout,
            "level": self.level,
            "type": self.type,
            "sort": self.sort,
        }

    def __repr__(self):
        return f"<Payout(level={self.level},payout={self.payout},type={self.type},sort={self.sort})>"

from enum import Enum


class AssetEnum(str, Enum):
    SMART_CONTRACT = "SMART_CONTRACT"
    WEB = "WEB"
    DAPP = "DAPP"
    OTHER = "OTHER"

    def __str__(self):
        return str(self.value)


class Asset:
    def __init__(self, type_: AssetEnum, target: str, name: str):
        self.type = type_
        self.target = target
        self.name = name

    def to_dict(self):
        return {"target": self.target, "type": self.type, "name": self.name}

    def __repr__(self):
        return f"<Asset(type={self.type},target={self.target},name={self.name})>"

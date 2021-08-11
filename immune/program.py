import json
from typing import List
from .payout import Payout
from .asset import Asset

IMMUNEFI_BASE_URL = "https://immunefi.com"
IMMUNEFI_PROJECT_PATH = "/bounty"


class Program:
    def __init__(self, payouts: List[Payout], assets: List[Asset]):
        self.payouts = payouts
        self.assets = assets

    def to_json(self):
        payouts = []
        assets = []
        for payout in self.payouts:
            payouts.append(payout.to_dict())
        for asset in self.assets:
            assets.append(asset.to_dict())
        return json.dumps({"payouts": payouts, "assets": assets})

    @classmethod
    def url_from_slug(cls, slug: str):
        return IMMUNEFI_BASE_URL + IMMUNEFI_PROJECT_PATH + "/" + slug

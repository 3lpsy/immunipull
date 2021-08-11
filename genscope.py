#!/usr/bin/env python3

from sys import exit, stderr
from argparse import ArgumentParser

from immune.asset import Asset, AssetEnum
from immune.payout import Payout, PayoutEnum
from immune.program import Program

try:
    import requests
except ImportError as e:
    print(
        "[!] Package 'requests' not installed or found. Please install: pip install requests"
    )
    exit(1)

from xml.etree.ElementTree import ElementTree, Element

try:
    from defusedxml.ElementTree import parse, fromstring
except ImportError as e:
    print(
        "[!] Package 'defusedxml' not installed or found. Please install: pip install defusedxml"
    )
    exit(1)


VERBOSE = 0
DEBUG = True


def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


def debug(*args, **kwargs):
    if VERBOSE > 1:
        verbose(*args, prefix="[**] ", **kwargs)


def verbose(msg, prefix="[*] ", *args, **kwargs):
    if VERBOSE > 0:
        msg = prefix + msg
        eprint(*args, **kwargs)


def ele_has_child(ele: Element, data: str, tag: str):
    data = data.replace(" ", "").replace("\n", "").lower()
    for child in ele:
        if child.tag.lower() == tag.lower():
            val = child.text
            if val:
                val = val.replace(" ", "").replace("\n", "").lower()
            if val and data in val:
                return True
    return False


def parse_payouts_from_section(section: Element):
    payouts = []
    # sections contain h3, p and divs
    current_type = PayoutEnum.OTHER

    for subsection in section:
        # find type which is a p sibling to the main div holding table
        if subsection.tag.lower() == "p":
            if len(subsection) == 1:
                if subsection[0].tag.lower() == "strong" and subsection[0].text:
                    current_type = PayoutEnum.from_text(subsection[0].text.lower())
        # match on next div holding table
        # may be more than one table for each type, but should be only divs
        if subsection.tag.lower() == "div":
            # browser parses diffrently, there'a  div wrapping abunch fo meta
            # stuff that needs to be avoided
            if len(subsection) > 0:
                if subsection[0].tag.lower() != "dl":
                    continue
            # dl holds two divs
            #  first is div with one dd (for level)
            #  second dt is just string "level", skip it
            #  second div holds payout amount
            #    get amt from first dd
            index = 0
            for payout_dl in subsection:
                if payout_dl.tag == "dl":
                    level = "Unknown"
                    amount = "Unknown"
                    if len(payout_dl) != 2:
                        eprint("Err on payout_dl length", len(payout_dl))
                        continue
                    else:
                        level_div = payout_dl[0]
                        if len(level_div) != 2:
                            eprint("Err on leve_div length")
                            continue
                        level_dd = level_div[0]
                        amt_div = payout_dl[1]
                        if len(amt_div) != 2:
                            eprint("Err on amt div")
                            continue
                        amt_dd = amt_div[0]

                        level = level_dd.text or amount
                        amount = amt_dd.text or amount
                        payouts.append(Payout(level, amount, current_type, index))
                        index += 1
    return payouts


def parse_assets_from_section(section: Element):
    assets = []
    if len(section) > 2:
        for asset_dl in section[2]:
            type_ = AssetEnum.OTHER
            name = "Generic"
            target = ""
            if len(asset_dl) != 2:
                eprint("Err on asset dl")
                continue
            target_div = asset_dl[0]
            if len(target_div) != 2:
                eprint("Err on asset target div")
                continue
            target_dd = target_div[0]
            if len(target_dd) != 1:
                eprint("Err on asset target dd")
                continue
            target = target_dd[0].text or ""

            type_div = asset_dl[1]
            if len(type_div) != 2:
                eprint("Err on asset type div")
                continue
            type_dd = type_div[0]
            type_str = type_dd.text or ""
            if type_str.lower().startswith("smart contract -"):
                type_ = AssetEnum.SMART_CONTRACT
                if "-" in type_str.lower():
                    name = type_str.lower().split("-", 1)[1].strip()
                else:
                    name = type_str.lower()
            if type_str.lower().startswith("web"):
                type_ = AssetEnum.WEB
                if "-" in type_str.lower():
                    name = type_str.lower().split("-", 1)[1].strip()
                else:
                    name = type_str.lower()
            asset = Asset(type_, target, name)
            assets.append(asset)
    return assets


SECTIONS_XPATH = ".//body/div/div/main/section/article/div/section"


def build_scope(slug: str, no_output):
    verbose("Downloading data from Immunefi")
    res = requests.get(Program.url_from_slug(slug))
    if res.status_code != 200:
        return 1
    tree: Element = fromstring(res.text)
    payouts = []
    assets = []
    for section in tree.iterfind(SECTIONS_XPATH):
        if ele_has_child(section, "Rewards by Threat Level", "h3"):
            payouts = parse_payouts_from_section(section)

        if ele_has_child(section, "Assets In Scope", "h3"):
            assets = parse_assets_from_section(section)

    program = Program(payouts, assets)
    data = program.to_json()
    if not no_output:
        print(data)


if __name__ == "__main__":
    primary = ArgumentParser()
    subs = primary.add_subparsers(dest="command")
    init = subs.add_parser("init")
    init.add_argument("-s", "--slug", required=True)
    init.add_argument("--no-output", action="store_true")
    args = primary.parse_args()
    if args.command == "init":
        exit(build_scope(args.slug, no_output=args.no_output))

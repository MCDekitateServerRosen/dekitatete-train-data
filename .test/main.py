import json
import pathlib
import logging
import rich.console
from rich.logging import RichHandler
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")
console = rich.console.Console()



with open(pathlib.Path(__file__).parent.parent/"data.json","r",encoding="utf-8")as f:
    data=json.load(f)

errors=[]
warnings=[]
def report(info):
    errors.append(info)
    log.error(info)

def warn(info):
    warnings.append(info)
    log.warning(info)

stations=dict(map(lambda elem:(elem["id"],elem),data["stations"]))

if tuple(data["companies"])!=tuple(data["company"].keys()):
    report("会社一覧に不整合があります。")

lines={}

for company,rosens in data["rosens"].items():
    lines[company]={}
    for rosen in rosens:
        lines[company][rosen["id"]]=rosen
        for sta in rosen["stations"]:
            if sta not in stations.keys():
                report(f"路線ID '{rosen['id']}' の駅一覧に不整合があります： ID={sta} の駅は存在しません。")

for id,station in stations.items():
    if tuple(station["rosens"])!=tuple(station["companies"]):
        report(f"駅ID '{id}' の企業一覧に不整合があります。")
    if len(station.get("position",[]))!=2:
        warn(f"駅ID '{id}' の座標は登録されていません。")
    for company,rosens in station["rosens"].items():
        for line in rosens:
            if line not in lines[company].keys():
                report(f"駅ID '{id}' の乗り入れ路線一覧に不整合があります： ID={line} の路線は存在しません。")
            elif line in lines[company][line].get("stations"):
                report(f"駅ID '{id}' の乗り入れ路線一覧に不整合があります： ID={line} の路線に該当の駅は存在しません。")
    

logging.info(f"{len(warnings)} warnings and {len(errors)} errors found!")

try:
    if len(errors)!=0: 
        raise (AssertionError(f"{len(errors)} errors found!"))
except:
    console.print_exception(extra_lines=2, show_locals=False)
    sys.exit(1)
    
#!/usr/bin/env python
# coding: utf-8
"""


"""

import os
import re
import io
import sys
import json
import requests
import requests_cache
import pandas as pd
from datetime import timedelta
from time import time

STATISTICS_URI = "https://api.climateactnow.com.au/api/statistic"
ELECTORATES_URI = "https://api.climateactnow.com.au/api/electorate"
ELECTION_RESULTS_URI = "https://results.aec.gov.au/24310/Website/Downloads/HouseTppByDivisionDownload-24310.csv"
OUTPUT_FILE = "src/vote_data.json"
OUTPUT_FILE_UPDATE = "src/update_data.json"

requests_cache.install_cache(".cache", expire_after=timedelta(hours=1))

req_stats = requests.get(STATISTICS_URI).json()["data"]
req_electorates = requests.get(ELECTORATES_URI).json()["data"]
req_election = requests.get(ELECTION_RESULTS_URI).text.split("\r\n", 1)[
    1
]  # weird hacky shit because AEC returns bad csv

stats = pd.DataFrame(req_stats["groupedByElectorates"].items(), columns=["id", "votes"])
electorates = pd.DataFrame(req_electorates,)
election2019 = pd.read_csv(io.StringIO(req_election))


def clean_social(v):
    if not v:
        return ""
    m = re.search(r"\.com\/(\w+)", v)
    if m:
        return m.group(1)
    return ""


def fix_names(name):
    if name == "Mcpherson":
        return "McPherson"
    if name == "Mcmahon":
        return "McMahon"
    if name == "Eden-monaro":
        return "Eden-Monaro"
    if name == "Mcewen":
        return "McEwen"
    if name == "O'connor":
        return "O'Connor"
    return name


def fix_parties(row):
    n = row["preferred_name"]
    if n == "Zali Steggall":
        return "IND"
    if n == "Adam Bandt":
        return "GRN"
    if n == "Rebekha Sharkie":
        return "IND"
    if n == "Helen Haines":
        return "IND"
    if n == "Andrew Wilkie":
        return "IND"
    return row["Party"]


def calculate_margin(row):
    if row["Party"] == "ALP":
        return row["ALP_Per"] - row["LNP_Per"]
    else:
        return row["LNP_Per"] - row["ALP_Per"]


def calculate_votediff(row):
    if row["Party"] == "ALP":
        return round(row["ALP_Votes"] - row["LNP_Votes"], 0)
    else:
        return round(row["LNP_Votes"] - row["ALP_Votes"], 0)


# clean stats
stats.set_index(stats.columns[0]).reset_index()

# clean electorates
electorates.set_index(electorates.columns[0]).reset_index()
electorates["fbook"] = electorates["fbook"].apply(clean_social)
electorates["twitter"] = electorates["twitter"].apply(clean_social)
electorates["electorate"] = electorates["electorate"].apply(fix_names)

# clean election data
election2019 = election2019.rename(
    columns={
        "DivisionNm": "electorate",
        "Liberal/National Coalition Votes": "LNP_Votes",
        "Liberal/National Coalition Percentage": "LNP_Per",
        "Australian Labor Party Votes": "ALP_Votes",
        "Australian Labor Party Percentage": "ALP_Per",
        "PartyAb": "Party",
    }
)
election2019["Margin"] = round(election2019.apply(calculate_margin, axis=1), 2)
election2019["Vote_diff"] = election2019.apply(calculate_votediff, axis=1)
election2019 = election2019.astype({"Vote_diff": "int32"})

# merges
electorate_stats = pd.merge(electorates, stats, left_index=True, right_index=True)
vote_stats = pd.merge(electorate_stats, election2019, how="left", on="electorate")

# clean up result
vote_stats["Participation"] = round(
    (vote_stats["votes"] / vote_stats["TotalVotes"]) * 100, 2
)
vote_stats["Party"] = vote_stats.apply(fix_parties, axis=1)

vote_stats.drop(
    [
        vote_stats.columns[0],
        "created_at",
        "updated_at",
        "DivisionID",
        "StateAb",
        "phone",
        "id_y",
        "LNP_Votes",
        "LNP_Per",
        "ALP_Votes",
        "ALP_Per",
        "TotalVotes",
    ],
    inplace=True,
    axis="columns",
)
vote_stats.drop(151, inplace=True)  # drop the "International" row

# sort columns
print(list(vote_stats.columns.values))

vote_stats = vote_stats[
    [
        "preferred_name",
        "electorate",
        "state",
        "Party",
        "twitter",
        "email",
        "fbook",
        # "Swing",
        "Margin",
        "Vote_diff",
        "votes",
        "Participation",
    ]
]

vote_stats.to_json(OUTPUT_FILE, orient="table", index=False)
print("Exported data to {}".format(OUTPUT_FILE))

with open(OUTPUT_FILE_UPDATE, "w") as fp:
    json.dump({"updated": int(time())}, fp)
# vote_stats.sort_values(by="votes", ascending=False).loc[vote_stats['Party'] == "LP"].head(100)
# vote_stats.to_csv("climate_action_vote_stats.csv", index=False)
# vote_stats = vote_stats.sort_values(by="votes", ascending=True)


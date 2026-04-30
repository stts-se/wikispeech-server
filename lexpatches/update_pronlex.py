#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.parse
import urllib.request
from typing import Optional

# NB:
# uv venv
# source .venv/bin/activate
# uv pip install pydantic

def ping_server(base_url):
    try:
        with urllib.request.urlopen(f"{base_url}/ping") as response:
            body = response.read().decode("utf-8")
            if body != "pronlex":
                sys.exit(f"Unexpected ping response from {base_url}: '{body}'")
    except urllib.error.HTTPError as exc:
        print(f"[ERROR] HTTP {exc.code} when calling ping: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"[ERROR] Could not reach server: {exc.reason}", file=sys.stderr)
        sys.exit(1)


        
def proc_line(server: str, url_prefix: str, lexicon: str, line: str):
    fs = line.split('\t')
    #print("Fields:", fs, file=sys.stderr)
    if len(fs) < 2:
        print(f"Too few fields, skipping '{line}'", file=sys.stderr)
        return
    cmd = fs[0]

    if func := COMMANDS.get(cmd):
        func(server, url_prefix, lexicon, line)
    else:
        print(f"Unknown command '{cmd}', skipping '{line}'", file=sys.stderr)
        

def set_preferred(server: str, url_prefix: str, lexicon: str, line: str) -> None:    
    #print(f"set_preferred: {line}")
    fs = line.split("\t")
    if len(fs) != 3:
        print(f"set_preferred: expected 3 fields, got {len(fs)}. Skipping line {line}")
        return None
    # if fs[0].strip() != "SET_PREFERRED":
    #     print(f"set_preferred: expected command SET_PREFERRED, got {fs[0]}. Skipping line {line}")
    #     return None

    word = fs[1].strip()
    trans = fs[2].strip()

        # --- 1. Look up the word ---
    entries = lookup_entries(server, url_prefix, lexicon, word)

    if not entries:
        print(f"[WARN] set_preferred(): No entries found for word '{word}' in lexicon '{lexicon}'.", file=sys.stderr)
        return None

    print(f"[INFO] set_preferred(): {len(entries)} entry/entries found.", file=sys.stderr)

    # --- 2. Find matching entry by first transcription ---
    matched = []
    for entry in entries:
        strn = first_transcription_strn(entry)
        if strn == trans:
            matched.append(entry)

    if not matched:
        print(
            f"[WARN] set_preferred(): No entry found whose first transcription matches '{trans}'.",
            file=sys.stderr
        )
        print("[INFO] set_preferred(): Available first transcriptions:", file=sys.stderr)
        for entry in entries:
            strn = first_transcription_strn(entry)
            print(f"         '{strn}'", file=sys.stderr)
        return None

    if len(matched) > 1:
        print(
            f"[WARN] set_preferred(): {len(matched)} entries share the same first transcription '{trans}'. "
            "Only the first match will be updated.",
            file=sys.stderr
        )
        matched = matched[:1]

    # --- 3. Update the (single) matched entry ---
    entry = matched[0]
    entry_id = entry.get("id", "<no id>")

    # Note: the Go Entry struct uses `json:"preferred,omitempty"`, which means
    # the field is absent from the JSON (not "false") when preferred is not set.
    # entry.get("preferred") therefore returns None for non-preferred entries,
    # so the `is True` check correctly distinguishes all three states.
    if entry.get("preferred") is True:
        print(f"[INFO] set_preferred(): Entry id={entry_id} is already preferred. Nothing to do.", file=sys.stderr)
        return None

    print(f"[INFO] set_preferred(): Setting preferred=true on entry id={entry_id} ...", file=sys.stderr)
    entry["preferred"] = True
    update_entry(server, url_prefix, entry)
    print(f"[OK]   Entry id={entry_id} updated successfully.", file=sys.stderr)



def delete(server: str, url_prefix: str, lexicon: str, line: str) -> None:    
    #print(f"delete: {line}")
    fs = line.split("\t")
    if len(fs) != 3:
        print(f"delete: expected 3 fields, got {len(fs)}. Skipping line {line}")
        return None
    # if fs[0].strip() != "DELETE":
    #     print(f"delete: expected command DELETE, got {fs[0]}. Skipping line {line}")
    #     return None
    
    word = fs[1].strip()
    trans = fs[2].strip()
    
    # --- 1. Look up the word ---
    entries = lookup_entries(server, url_prefix, lexicon, word)

    if not entries:
        print(f"[WARN] delete(): No entries found for word '{word}' in lexicon '{lexicon}'.", file=sys.stderr)
        return None
    
    print(f"[INFO] delete(): {len(entries)} entry/entries found.", file=sys.stderr)

    matched = []
    for entry in entries:
        strn = first_transcription_strn(entry)
        if strn == trans:
            matched.append(entry)
        
    if not matched:
        print(
            f"[WARN] delete(): No entry found whose first transcription matches '{trans}'.",
            file=sys.stderr,
        )
        print("[INFO] delete(): Available first transcriptions:", file=sys.stderr)
        for entry in entries:
            strn = first_transcription_strn(entry)
            print(f"         '{strn}'", file=sys.stderr)
        return None
        
    for entry in matched:
        entry_id = entry.get("id", "<NO ID>")
        
        # pronlex: /lexicon/delete_entry/{lexicon_name}/{entry_id}    
        url = f"{server.rstrip('/')}{url_prefix}/lexicon/delete_entry/{lexicon}/{entry_id}"    
        print(f"[INFO] DELETE: {word} {trans} {entry_id}", file=sys.stderr)
        print(f"[INFO] DELETE: {url}", file=sys.stderr)
        try:
            with urllib.request.urlopen(url) as response:
                body = response.read().decode("utf-8")
                print(f"[INFO] DELETE server response: {body}", file=sys.stderr)
        except urllib.error.HTTPError as exc:
            print(f"[ERROR]  delete(): HTTP {exc.code} when calling delete: {exc.reason}", file=sys.stderr)
            #return None #sys.exit(1)
        except urllib.error.URLError as exc:
            print(f"[ERROR]  delete(): Could not reach server: {exc.reason}", file=sys.stderr)
            #return None # sys.exit(1)


# Example entry "lök":
# http://localhost:8787/lexicon/lookup?lexicons=sv_se_braxen_lex:sv-se.braxen&words=l%C3%B6k
# [
#     {
#         id: 519151,
#         lexRef: {
#             dbRef: "sv_se_braxen_lex",
#             lexName: "sv-se.braxen"
#         },
#         strn: "lök",
#         language: "sv-se",
#         partOfSpeech: "NN UTR SIN IND NOM",
#         lemma: { },
#         transcriptions: [
#             {
#                 id: 519151,
#                 entryId: 519151,
#                 strn: "" l 2: k",
#                 sources: [
#                 "braxen"
#                 ]
#                 }
#                 ],
#                 status: {
#                 id: 519151,
#             name: "imported",
#             source: "braxen",
#             timestamp: "2026-04-10T20:24:59Z",
#             current: true
#             }
#             }
# ]

# HTTP request "addentry"

# /lexicon/addentry?lexicon_name=wikispeech_lexserver_testdb:sv&entry={
#     "strn": "flesk",
#     "language": "sv-se",
#     "partOfSpeech": "NN",
#     "morphology": "SIN-PLU|IND|NOM|NEU",
#     "wordParts": "flesk",
#     "lemma": {
# 	"strn": "flesk",
# 	"reading": "",
# 	"paradigm": "s7n-övriga ex träd"
#     },
#     "transcriptions": [
# 	{
# 	    "strn": "\" f l E s k",
# 	    "language": "sv-se"
# 	}
#     ]
# }

# // Minimal example (English)
# {
#    strn: "things",
#    transcriptions: [
#    {
#       strn: "' T I N z"
#    }
#    ]
# }

from pydantic import BaseModel, Field
from typing import Optional


# class LexRef(BaseModel):
#     db_ref: str = Field(default="", alias="dbRef")
#     lex_name: str = Field(default="", alias="lexName")

#     model_config = {"populate_by_name": True}


# class Lemma(BaseModel):
#     id: Optional[int] = Field(default=None, alias="id")
#     strn: str = Field(default="")
#     reading: str = Field(default="")
#     paradigm: str = Field(default="")

#     model_config = {"populate_by_name": True}


class Transcription(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    entry_id: Optional[int] = Field(default=None, alias="entryId")
    strn: str
    language: str = Field(default="")
    sources: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class EntryStatus(BaseModel):
    id: Optional[int] = Field(default=None, alias="id")
    name: str = Field(default="")
    source: str = Field(default="")
    #timestamp: str = Field(default="")
    current: bool = Field(default=False)

    model_config = {"populate_by_name": True}


# class EntryComment(BaseModel):
#     id: Optional[int] = Field(default=None, alias="id")
#     entry_id: Optional[int] = Field(default=None, alias="entryId")
#     source: str = Field(default="")
#     label: str = Field(default="")
#     comment: str = Field(default="")

#     model_config = {"populate_by_name": True}


# class EntryValidation(BaseModel):
#     id: Optional[int] = Field(default=None, alias="id")
#     level: str                                          # no omitempty in Go
#     rule_name: str = Field(alias="ruleName")
#     message: str = Field(alias="Message")              # note: capital M in Go JSON tag
#     timestamp: str

#     model_config = {"populate_by_name": True}


class Entry(BaseModel):
    # id: Optional[int] = Field(default=None, alias="id")
    # lex_ref: LexRef = Field(default_factory=LexRef, alias="lexRef")
    strn: str
    language: str = Field(default="")
    # part_of_speech: str = Field(default="", alias="partOfSpeech")
    # morphology: str = Field(default="")
    # word_parts: str = Field(default="", alias="wordParts")
    # lemma: Lemma = Field(default_factory=Lemma)
    transcriptions: list[Transcription] = Field(default_factory=list)
    status: EntryStatus = Field(default_factory=EntryStatus)
    # entry_validations: list[EntryValidation] = Field(default_factory=list, alias="entryValidations")
    preferred: bool = Field(default=False)
    # tag: str = Field(default="")
    # comments: list[EntryComment] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


# entry = Entry(
#     strn="hello",
#     language="eng",
#     preferred=True,
#     transcriptions=[
#         Transcription(
#             strn="hɛloʊ",
#             language="eng",
#         )
#     ],
#     status=EntryStatus(
#         name="unchecked",
#         source="MVP2_2026",
#         current=True,
#     ),
# )
    
def add_entry(server: str, url_prefix: str, lexicon: str, line: str) -> None:    
    #print(f"add_entry: {line}")
    fs = line.split("\t")
    if len(fs) != 6:
        print(f"delete: expected 6 fields, got {len(fs)}. Skipping line {line}")
        return None
    # if fs[0].strip() != "DELETE":
    #     print(f"delete: expected command DELETE, got {fs[0]}. Skipping line {line}")
    #     return None

    word = fs[1].strip()
    trans = fs[2].strip()
    lang = fs[3].strip() # "sv-se"
    status = fs[4].strip() # "unverified"
    src = fs[5].strip() # "mvp2_2026"
    entries = lookup_entries(server, url_prefix, lexicon, word)

    if not entries:
        print(f"[INFO] add_entry(): No entries found for word '{word}' in lexicon '{lexicon}'.", file=sys.stderr)

    
    print(f"[INFO] add_entry(): {len(entries)} entry/entries found.", file=sys.stderr)

    matched = []
    for entry in entries:
        strn = first_transcription_strn(entry)
        if strn == trans:
            matched.append(entry)
    

    if matched:
        print(f"[INFO] add_entry(): Matching entries already in lexicon ({len(entries)}), nothing to do.")
        return None
    
    entry = Entry(
        strn=word,
        language=lang,
        preferred=True,
        transcriptions=[
             Transcription(
                 strn=trans,
                 language=lang,
                 sources=[src],
             )
        ],
        status=EntryStatus(
            name=status,
            source=src,
            current=True,
        ),
     )

    json_str = entry.model_dump_json(by_alias=True, exclude_none=True, indent=2)
    #print("ADD_ENTRY:", json_str)

    #====================
    #/lexicon/addentry?lexicon_name=wikispeech_lexserver_testdb:sv&entry={...}
    url = f"{server.rstrip('/')}{url_prefix}/lexicon/addentry"
    
    payload = urllib.parse.urlencode({"lexicon_name": lexicon, "entry": json_str}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(payload)),
        },
    )

    print(f"[INFO] add_entry(): POST {url}", file=sys.stderr)

    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            print(f"[INFO] add_entry(): Server response: {body}", file=sys.stderr)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        print(f"[ERROR] add_entry(): HTTP {exc.code} when calling addentry: {exc.reason}", file=sys.stderr)
        print(f"[DEBUG] add_entry(): Response body: {body}", file=sys.stderr)
        return None
    except urllib.error.URLError as exc:
        print(f"[ERROR] add_entry(): Could not reach server: {exc.reason}", file=sys.stderr)
        return None


    
    
def lookup_entries(server: str, url_prefix: str, lexicon: str, word: str) -> list:
    """
    Call /lexicon/lookup on the pronlex server and return all matching entries.

    The endpoint accepts query parameters:
        lexicons  – colon-separated db:lexname reference
        words     – the orthographic word to look up
    """
    params = urllib.parse.urlencode({
        "lexicons": lexicon,
        "words": word,
    })
    url = f"{server.rstrip('/')}{url_prefix}/lexicon/lookup?{params}"

    print(f"[INFO] lookup_entries(): Looking up word '{word}' in lexicon '{lexicon}'", file=sys.stderr)
    print(f"[INFO] lookup_entries(): GET {url}", file=sys.stderr)

    try:
        with urllib.request.urlopen(url) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        print(f"[ERROR] lookup_entries(): HTTP {exc.code} when calling lookup: {exc.reason}", file=sys.stderr)
        return [] #sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"[ERROR] lookup_entries(): Could not reach server: {exc.reason}", file=sys.stderr)
        return [] # sys.exit(1)

    try:
        entries = json.loads(body)
    except json.JSONDecodeError as exc:
        print(f"[ERROR] lookup_entries(): Could not parse JSON response: {exc}", file=sys.stderr)
        print(f"[DEBUG] lookup_entries(): Raw response: {body}", file=sys.stderr)
        return [] #sys.exit(1)

    if not isinstance(entries, list):
        print(f"[ERROR] lookup_entries(): Expected a JSON list of entries, got: {type(entries)}", file=sys.stderr)
        return []# sys.exit(1)

    return entries


def update_entry(server: str, url_prefix: str, entry: dict) -> None:
    """
    POST a single entry to /lexicon/updateentry.

    The Go lexserver handler reads the entry from a URL-encoded form field
    named 'entry', whose value is the JSON-serialised Entry struct.

    Note: although 'preferred' is stored as an integer (0/1) in the underlying
    SQLite/MariaDB schema, the Go server's Entry struct maps it as a bool, so
    sending JSON `true` here is correct — the server handles the conversion.
    """
    url = f"{server.rstrip('/')}{url_prefix}/lexicon/updateentry"
    json_str = json.dumps(entry)

    payload = urllib.parse.urlencode({"entry": json_str}).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(payload)),
        },
    )

    print(f"[INFO] POST {url}")

    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            print(f"[INFO] Server response: {body}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        print(f"[ERROR] HTTP {exc.code} when calling updateentry: {exc.reason}", file=sys.stderr)
        print(f"[DEBUG] Response body: {body}", file=sys.stderr)
        return None
    except urllib.error.URLError as exc:
        print(f"[ERROR] Could not reach server: {exc.reason}", file=sys.stderr)
        return None


def first_transcription_strn(entry: dict) -> Optional[str]:
    """Return the strn of the first transcription in an entry, or None."""
    transcriptions = entry.get("transcriptions") or []
    if transcriptions:
        return transcriptions[0].get("strn")
    return None



# Commands that can be used on a line of the input file.
COMMANDS = {
    'SET_PREFERRED': set_preferred,
    'ADD_ENTRY': add_entry,
    'DELETE': delete,
    #'UPDATE_TRANSCRIPTION': update_tramscription
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update a running pronlex db from a lexicon patch file.\nExample: python update_pronlex.py lexicon_patch_file.txt"
    )
    parser.add_argument(
        "-s",
        "--server",
        default="http://localhost:8787",
        help="Base URL of the pronlex lexserver, e.g. http://localhost:8787",
    )
    parser.add_argument(
        "--url-prefix",
        default="",
        help=(
            "Optional URL path prefix inserted before /lexicon/..., e.g. /lexserver "
            "when the server sits behind a proxy. Default: empty (standalone server)."
        ),
    )
    parser.add_argument(
        "-l",
        "--lexicon",
        default="sv_se_braxen_lex:sv-se.braxen",
        help="Lexicon reference in 'db:lexname' format, e.g. sv_db:swe_lex",
    )
    # parser.add_argument(
    #     "--word",
    #     required=True,
    #     help="Orthographic word to look up (Entry.strn)",
    # )
    # parser.add_argument(
    #     "--transcription",
    #     required=True,
    #     help="Phonetic transcription string to match (first Transcription.strn)",
    # )

    # One or more file paths
    parser.add_argument("files", nargs="+", help="Fileformat: (ADD_ENTRY | SET_PREFERRED | DELETE | UPDATE_TRANSCRIPTION) <TAB> word <TAB> [...]")

    args = parser.parse_args()
    
    
    # Normalise the prefix: strip any trailing slash so we always get
    # exactly one slash before /lexicon/...
    url_prefix = args.url_prefix.rstrip("/")

    print("Server:", args.server, file=sys.stderr)
    print("Lexicon:", args.lexicon, file=sys.stderr)
    print("Filenames:", ", ".join(args.files), file=sys.stderr)
    
    
    ping_server(args.server)

    for fn in args.files:
        with open(fn) as f:
            lines = [line.rstrip() for line in f if line.strip() and not line.startswith("#")]
            for ln in lines:
                proc_line(args.server, url_prefix, args.lexicon, ln)
    


if __name__ == "__main__":
    main()

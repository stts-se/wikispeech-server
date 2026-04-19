## The Wikispeech server must be started before running this script.

# python run_text_file_for_proofing.py

# python run_text_file_for_proofing.py testdata/article_text_sv_medeltidens_mat.txt
# Point your browser to proofing/article_text_sv_medeltidens_mat.html

import requests
import argparse
import sys
from urllib.parse import urlparse
import shutil
from pathlib import Path
import json
import html
import os

def ping_server(client, base_url):
    try:
        response = client.get(f"{base_url}/ping", timeout=2)
        assert response.text == "wikispeech"
    except requests.exceptions.ConnectionError:
        sys.exit(f"Server not reachable at {base_url}/ping, is it running?")
    except requests.exceptions.Timeout:
        sys.exit(f"Server did not respond within 2 seconds")
        

def render_g2p_table(heading, rows):
    if not rows:
        return ""

    table_rows = []

    for orth, phonemes in rows:
        table_rows.append(f"""
        <tr>
            <td>{html.escape(orth)}</td>
            <td>{html.escape(phonemes)}</td>
        </tr>
        """)

    return f"""
    <div class="block">
        
        <table class="g2p-table">
            <tr>
                <th>{heading}</th>
                <th>Transcription</th>
            </tr>
            {"".join(table_rows)}
        </table>
    </div>
    """
        
def render(items):
    blocks = []

    for it in items:
        blocks.append(f"""
        <div class="item">
            <h3>{it['id']}</h3>

            <audio controls preload="metadata">
                <source src="{it['audio']}" type="audio/ogg">
            </audio>

            <div class="block text"><b>Input:</b><br>{html.escape(it['orths'])}</div>
            <div class="block"><b>Normalized:</b><br>{html.escape(it['words'])}</div>
            <div class="block"><b>After lexicon look up:</b><br>{html.escape(it['trans'])}</div>
            <div class="block"><b>To synthesis:</b><br>{html.escape(it['tts'])}</div>
            <div class="table-row">
               {render_g2p_table('In lexicon', it['lex'])} 
               {render_g2p_table('Out of vocabulary', it['g2p'])} 
            </div>
        </div>
        """)

    return "\n".join(blocks)
        
def run_article(client, base_url, lang, voice, file_path, output_dir):
    Path(output_dir).mkdir(exist_ok=True)

    text_name = os.path.basename(file_path)
    text_name = Path(text_name).stem
    text_name_html = f"{text_name}.html"
    
    out = Path(output_dir)
    audio_dir = out / "audio"
    audio_dir.mkdir(exist_ok=True)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    js_file = "play_sequential.js"
    shutil.copyfile(os.path.join(script_dir, js_file), os.path.join(output_dir, js_file))

    f_base = Path(file_path).stem
    items = []
    with open(file_path) as f:
        lines = [line.rstrip() for line in f if line.strip() and not line.startswith("#")]
        for i, l in enumerate(lines):
            i+=1
            id = '{:0>3}'.format(i)
            payload = {
                "lang": lang,
                "voice": voice,
                "input": l
            }
            response = client.post(f"{base_url}/", data=payload)
            #TODO Error handling
            #print(response.status_code)
            #print(response.text) # <- Downcase and look for error
            # response.text.lower().startswith("error")
            data = response.json()
            audio_uri = data["audio"]
            base = Path(urlparse(audio_uri).path).name
            audio_path = Path(__file__).parent / "tmp" / base
            local_audio = out / "audio" / f"{id}_{f_base}.opus"
            #print(output_dir, out, f_base)
            shutil.copy2(audio_path, local_audio)
            print(id, audio_path, file=sys.stderr)
            #print(l)
            #data_cpy = data
            #del data_cpy["audio_data"] 
            #print(json.dumps(data_cpy, indent=2, ensure_ascii=False))
            orths = []
            words = []
            trans = []
            tts_phonemes = []
            in_lexicon = []
            non_lex_phos = []
            seen_lex = set()
            seen_g2p = set()
            for t in data["tokens"]:
                orth = t["orth"]
                orths.append(orth)
                for w in t["words"]:
                    words.append(w["orth"])
                    if "trans" in w:
                        trans.append(w["trans"])
                        lex_item = (w["orth"], w["trans"])
                        if lex_item not in seen_lex:
                            seen_lex.add(lex_item)
                            in_lexicon.append(lex_item)
                    elif "tts_input" in w:
                        trans.append(w["tts_input"])
                    if "tts_phonemes" in w:
                        tts_phonemes.append(w["tts_phonemes"])
                    if "g2p_method" in w:
                        if w["g2p_method"] != "lexicon":
                            item = (w["orth"], w["tts_phonemes"])
                            if item not in seen_g2p:
                                seen_g2p.add(item)    
                                non_lex_phos.append(item) 
                            
                            
            items.append({
                "id": id,
                "audio": f"audio/{local_audio.name}",
                "orths": " ".join(orths),
                "words": " ".join(words),
                "trans": " ".join(trans),
                "tts": " ".join(tts_phonemes),
                "lex": in_lexicon,
                "g2p": non_lex_phos
            })

            
    html_doc = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    #playing {{
    background-color: yellow;
    }}
    body {{
    font-family: sans-serif;
    margin: 20px;
    }}
    .item {{
    border: 1px solid #ccc;
    padding: 12px;
    padding-top: 16px;
    margin-bottom: 16px;
    }}
    .block {{
    margin-top: 8px;
    }}
    audio {{
    display: block;
    width: 400px;
    max-width: 100%;
    margin-top: 8px;
    }}
    .toolbar {{
    position: sticky;
    top: 0;
    z-index: 1000;

    background: white;
    padding: 8px 0;
    border-bottom: 1px solid #ccc;
    }}
    .table-row {{
    display: flex;
    gap: 16px;
    align-items: flex-start;
    flex-wrap: wrap;
    }}
    .table-row > div {{
    flex: 0 0 auto;
    }}
    .g2p-table {{
    margin-top: 8px;
    border-collapse: collapse;
    width: auto;
    }}
    .g2p-table th,
    .g2p-table td {{
    border: 1px solid #ccc;
    padding: 4px 8px;
    text-align: left;
    vertical-align: top;
    white-space: nowrap;
    }}
    </style>
    </head>
    <body>
    <p><div class="toolbar">
    Autoscroll <input title="Autoscroll playing audio element into view" type="checkbox" name="autoscroll" id="autoscroll" value="autoscroll" checked> &nbsp;&nbsp;
    <button id="toggle" title="Press P to play/pause">Play All</button>
    <button id="stop">Stop/Reset</button></div>
    </p>
    {render(items)}
    </body>
    <script type="text/javascript" src="play_sequential.js"></script>
    </html>
    """

    (out / text_name_html).write_text(html_doc, encoding="utf-8")

    return text_name_html

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-l", "--language", default="sv")
    parser.add_argument("-v", "--voice", default="sv_vc_m2f")
    parser.add_argument("-o", "--output_dir", default="proofing")
    parser.add_argument("-u", "--url", default="http://localhost:10000")
    
    # One or more file paths
    parser.add_argument("files", nargs="+")
    
    args = parser.parse_args()
    
    print("Language:", args.language, file=sys.stderr)
    print("Voice:", args.voice, file=sys.stderr)
    print("Output directory:", args.output_dir, file=sys.stderr)
    #print(args.files, file=sys.stderr)

    
    session = requests.Session()
    ping_server(session, args.url)
    # run_article(client, base_url, lang, voice, file_path, output_dir)
    for f in args.files:
        output_html = run_article(session, args.url, args.language, args.voice, f, args.output_dir)
        print(f"{f} -> {output_html}", file=sys.stderr)
 
    
    
    
if __name__ == "__main__":
    main()
    


## The Wikispeech server must be started before running this script.

# python run_text_file_for_proofing.py

# python run_text_file_for_proofing.py testdata/article_text_sv_medeltidens_mat.txt
# Point your browser to proofing/index.html

import requests
import argparse
import sys
from urllib.parse import urlparse
import shutil
from pathlib import Path
import json
import html

def ping_server(client, base_url):
    try:
        response = client.get(f"{base_url}/ping", timeout=2)
        assert response.text == "wikispeech"
    except requests.exceptions.ConnectionError:
        sys.exit(f"Server not reachable at {base_url}/ping, is it running?")
    except requests.exceptions.Timeout:
        sys.exit(f"Server did not respond within 2 seconds")
        

def render(items):
    blocks = []

    for it in items:
        blocks.append(f"""
        <div class="item">
            <h3>{it['id']}</h3>

            <audio controls>
                <source src="{it['audio']}" type="audio/ogg">
            </audio>

            <div class="block"><b>Input:</b><br>{html.escape(it['orths'])}</div>
            <div class="block"><b>Normalized:</b><br>{html.escape(it['words'])}</div>
            <div class="block"><b>Trans:</b><br>{html.escape(it['trans'])}</div>
            <div class="block"><b>TTS:</b><br>{html.escape(it['tts'])}</div>
        </div>
        """)

    return "\n".join(blocks)
        
def run_article(client, base_url, lang, voice, file_path, output_dir):
    Path(output_dir).mkdir(exist_ok=True)
    
    out = Path(output_dir)
    audio_dir = out / "audio"
    audio_dir.mkdir(exist_ok=True)

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
            tts_input = []
            for t in data["tokens"]: 
                orth = t["orth"]
                orths.append(orth)
                for w in t["words"]:
                    words.append(w["orth"])
                    if "trans" in w:
                        trans.append(w["trans"])
                    if "tts_input" in w:
                        tts_input.append(w["tts_input"])

            items.append({
                "id": id,
                "audio": f"audio/{local_audio.name}",
                "orths": " ".join(orths),
                "words": " ".join(words),
                "trans": " ".join(trans),
                "tts": " ".join(tts_input),
            })

            # # --- build one HTML "card" ---
            # item_html = f"""
            # <div class="item">
            #     <h3>{id}</h3>

            #     <audio controls>
            #         <source src="{Path(local_audio).name}" type="audio/ogg">
            #         Your browser does not support audio.
            #     </audio>

            #     <div class="block"><b>Input text:</b><br>{html.escape(' '.join(orths))}</div>
            #     <div class="block"><b>Normalised text:</b><br>{html.escape(' '.join(words))}</div>
            #     <div class="block"><b>Input transcription:</b><br>{html.escape(' '.join(trans))}</div>
            #     <div class="block"><b>TTS transcription:</b><br>{html.escape(' '.join(tts_input))}</div>
            # </div>
            # """

            # items_html.append(item_html)
            # print("audio:", out / f"{id}_{f_base}.opus")
            # print("input text:", orths)
            # print("normalised text:", words)
            # print("input transcription", trans)
            # print("tts transcription", tts_input)
            # print()
            
    html_doc = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body {{
    font-family: sans-serif;
    margin: 20px;
    }}
    .item {{
    border: 1px solid #ccc;
    padding: 12px;
    margin-bottom: 16px;
    }}
    .block {{
    margin-top: 8px;
    white-space: pre-wrap;
    word-wrap: break-word;
    }}
    audio {{
    width: 100%;
    margin-top: 8px;
    }}
    </style>
    </head>
    <body>
    {render(items)}
    </body>
    </html>
    """

    (out / "index.html").write_text(html_doc, encoding="utf-8")
    # # --- final HTML document ---
    # html_doc = f"""
    # <html>
    # <head>
    #     <meta charset="utf-8">
    #     <style>
    #         body {{
    #             font-family: sans-serif;
    #             margin: 20px;
    #         }}
    #         .item {{
    #             border: 1px solid #ccc;
    #             padding: 15px;
    #             margin-bottom: 20px;
    #         }}
    #         .block {{
    #             margin-top: 10px;
    #             white-space: pre-wrap;
    #             word-wrap: break-word;
    #         }}
    #         audio {{
    #             margin-top: 10px;
    #             width: 100%;
    #         }}
    #     </style>
    # </head>
    # <body>
    #     {"".join(items_html)}
    # </body>
    # </html>
    # """

    # output_file = out / f"{f_base}.html"
    # output_file.write_text(html_doc, encoding="utf-8")






    
def test_medeltidens_mat(self, client, base_url, data_dir):
    self.run_article(client, base_url, data_dir, "sv", "sv_vc_m2f_p", "article_text_sv_medeltidens_mat.txt")
            
def test_nevermind(self, client, base_url, data_dir):
    self.run_article(client, base_url, data_dir, "sv", "sv_vc_m2f_p", "article_text_sv_nevermind.txt")



def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-l", "--language", default="sv")
    parser.add_argument("-v", "--voice", default="sv_vc_m2m_p")
    parser.add_argument("-o", "--output_dir", default="proofing")
    
    # One or more file paths
    parser.add_argument("files", nargs="+")
    
    args = parser.parse_args()
    
    print("Language:", args.language, file=sys.stderr)
    print("Voice:", args.voice, file=sys.stderr)
    print("Output directory:", args.output_dir, file=sys.stderr)
    #print(args.files, file=sys.stderr)

    
    base_url = "http://localhost:10000"
    session = requests.Session()
    ping_server(session, base_url)
    # run_article(client, base_url, lang, voice, file_path, output_dir)
    for f in args.files:
        run_article(session, base_url, args.language, args.voice, f, args.output_dir)
    
 
    
    
    
if __name__ == "__main__":
    main()
    


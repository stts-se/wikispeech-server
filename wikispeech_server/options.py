# -*- coding: utf-8 -*-

import wikispeech_server as ws

def getWikispeechOptions():

    wikispeech_options = {
        "GET": {
            "description": "Get speech from text",
            "parameters": {
                "input": {
                    "type": "string",
                    "description": "The text to be synthesised",
                    "required": True,
                    "default": None
                },
            "lang": {
                "type": "string",
                "description": "ISO 639-1 two-letter code for textprocessing and synthesis language",
                "required": True,
                "allowed": ws.wikispeech.getSupportedLanguages(),
                "default": None
            },
            "textprocessor": {
                "type": "string",
                "description": "name of a defined wikispeech textprocessor for this language",
                "required": False,
                "default": "The default textprocessor for this language"
            },
            "voice": {
                "type": "string",
                "description": "name of a defined wikispeech voice for this language",
                "required": False,
                "default": "The default voice for this language"
            },
            "input_type": {
                "type": "string",
                "description": "the type of the input, for instance with or without markup",
                "required": False,
                "allowed": ["text", "ssml"],
                "default": "text"
            },
            "output_type": {
                "type": "string",
                "description": "the type of the output, for instance with or without timing information",
                "required": False,
                "allowed": "json",
                "default": "json"
            }                
        },
        "examples": [
            {
                "input": "Det här är ett test",
                "lang": "sv"
            },
            {
                "input": "Det här är ett test",
                "lang": "sv",
                "textprocessor": "wikitextproc_sv",
                "voice": "stts_sv_nst-hsmm",
                "input_type": "text",
                "output_type": "json"
            }
        ]
            
        }
    }
                

    #Parameters for POST are the same as for GET. If they're not, "POST" needs to be defined separately!
    wikispeech_options["POST"] = wikispeech_options["GET"]
    return wikispeech_options





def getTextprocessingOptions():

    options = {
        "GET": {
            "description": "Get markup from text",
            "parameters": {
                "input": {
                    "type": "string",
                    "description": "The text to be processed",
                    "required": True,
                    "default": None
                },
                "lang": {
                    "type": "string",
                    "description": "ISO 639-1 two-letter code for textprocessing language",
                    "required": True,
                    "allowed": ws.wikispeech.textprocSupportedLanguages(),
                    "default": None
                },
                "textprocessor": {
                    "type": "string",
                    "description": "name of a defined wikispeech textprocessor for this language",
                    "required": False,
                    "default": "The default textprocessor for this language"
                },
                "input_type": {
                    "type": "string",
                    "description": "the type of the input, for instance with or without markup",
                    "required": False,
                    "allowed": ["text", "ssml"],
                    "default": "text"
                },
                "output_type": {
                    "type": "string",
                    "description": "the type of the output. Only json implemented so meaningless at the moment",
                    "required": False,
                    "allowed": "json",
                    "default": "json"
                }                
            },
            "examples": [
                {
                    "input": "Det här är ett test",
                    "lang": "sv"
                },
                {
                    "input": "Det här är ett test",
                    "lang": "sv",
                    "textprocessor": "wikitextproc_sv",
                    "input_type": "text",
                    "output_type": "json"
                }
            ]
            
        }
    }
                

    #Parameters for POST are the same as for GET. If they're not, "POST" needs to be defined separately!
    options["POST"] = options["GET"]

    return options



def getSynthesisOptions():

    options = {
        "GET": {
            "description": "Get speech from markup",
            "parameters": {
                "input": {
                    "type": "string",
                    "description": "The markup to be synthesised",
                    "required": True,
                    "default": None
                },
                "lang": {
                    "type": "string",
                    "description": "ISO 639-1 two-letter code for synthesis language",
                    "required": True,
                    "allowed": ws.wikispeech.synthesisSupportedLanguages(),
                    "default": None
                },
                "voice": {
                    "type": "string",
                    "description": "name of a defined wikispeech voice for this language",
                    "required": False,
                    "default": "The default voice for this language"
                },
                "input_type": {
                    "type": "string",
                    "description": "the type of the input. Only 'markup' implemented, so currently meaningless",
                    "required": False,
                    "allowed": "markup",
                    "default": "markup"
                },
                "output_type": {
                    "type": "string",
                    "description": "the type of the output, for instance with or without timing information",
                    "required": False,
                    "allowed": "json",
                    "default": "json"
                }                
            },
            "examples": [
                {
                    "input": {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"accent": "!H*", "children": [{"p": "t", "tag": "ph"}, {"p": "E", "tag": "ph"}, {"p": "s", "tag": "ph"}, {"p": "t", "tag": "ph"}], "ph": "t E s t", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "' t E s t", "pos": "NN", "tag": "t", "text": "test"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"},
                    "lang": "sv"
                },
                {
                    "input": {"children": [{"children": [{"children": [{"children": [{"accent": "!H*", "children": [{"accent": "!H*", "children": [{"p": "t", "tag": "ph"}, {"p": "E", "tag": "ph"}, {"p": "s", "tag": "ph"}, {"p": "t", "tag": "ph"}], "ph": "t E s t", "stress": "1", "tag": "syllable"}], "g2p_method": "lexicon", "ph": "' t E s t", "pos": "NN", "tag": "t", "text": "test"}, {"pos": ".", "tag": "t", "text": "."}, {"breakindex": "5", "tag": "boundary", "tone": "L-L%"}], "tag": "phrase"}], "tag": "s"}], "tag": "p"}], "tag": "utt"},
                    "lang": "sv",
                    "voice": "stts_sv_nst-hsmm",
                    "input_type": "markup",
                    "output_type": "json"
                }
            ]
            
        }
    }
                

    #Parameters for POST are the same as for GET. If they're not, "POST" needs to be defined separately!
    options["POST"] = options["GET"]

    return options

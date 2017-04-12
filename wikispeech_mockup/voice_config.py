

textprocessor_configs = [
    {"name":"wikitextproc_sv", "lang":"sv",
     "components":[
         {
             "module":"adapters.marytts_adapter",
             "call":"marytts_preproc",
             "mapper": {
                 "from":"sv-se_ws-sampa",
                 "to":"sv-se_sampa_mary"
             },
         },
         {
             #"module":"wikilex",
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"sv-se.nst"
         }
     ]
    }
    ,
    
    {"name":"wikitextproc_nb", "lang":"nb",
     "components":[
         {
             "module":"adapters.marytts_adapter",
             "call":"marytts_preproc"
#         },
#         {
#             "module":"wikilex",
#             "call":"lexLookup",
#             "lexicon":"no-nb.nst"
         }
     ]
    }
    ,


    {"name":"wikitextproc_en", "lang":"en",
     "components":[
         {
             "module":"adapters.marytts_adapter",
             "call":"marytts_preproc"
         },
         {
             "module":"wikilex",
             "call":"lexLookup",
             "lexicon":"en-us.cmu"
         }
     ]
    }
    ,


    {"name":"wikitextproc_ar", "lang":"ar",
     "components":[
         {
             "module":"adapters.marytts_adapter",
             "call":"marytts_preproc",
             "mapper": {
                 "from":"ar_ws-sampa",
                 "to":"ar_sampa_mary"
             },
         },
         {
             #"module":"wikilex",
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"ar-test"
         }
     ]
    }

]


voice_configs = [
    {
        "lang":"sv",
        "name":"stts_sv_nst-hsmm",
        "engine":"marytts",
        "adapter":"adapters.marytts_adapter",
        "mapper": {
            "from":"sv-se_ws-sampa",
            "to":"sv-se_sampa_mary"
            }
    }
    ,
    #TODO
    #{"lang":"sv", "name":"espeak_mbrola_sv1", "engine":"espeak", "adapter":"adapters.espeak_adapter", "espeak_mbrola_voice":"mb-sw1", "espeak_voice":"mb-sw1", "program":{"command":'espeak -v mb-sw1'}}
    #,

    {"lang":"nb", "name":"stts_no_nst-hsmm", "engine":"marytts", "adapter":"adapters.marytts_adapter", "marytts_locale":"no"}
    ,


    {"lang":"en", "name":"dfki-spike-hsmm", "engine":"marytts", "adapter":"adapters.marytts_adapter", "marytts_locale":"en_US"}
    ,
    {"lang":"en", "name":"cmu-slt-hsmm", "engine":"marytts", "adapter":"adapters.marytts_adapter", "marytts_locale":"en_US"}
    ,

    #{"lang":"en", "name":"cmu_slt_hts", "engine":"hts_engine", "adapter":"hts_engine_adapter", "voice_file":"voices/hts_engine/cmu_us_arctic_slt_demo.htsvoice"}
    #,

    #TODO
    {"lang":"en", "name":"cmu-slt-flite", "engine":"flite", "adapter":"adapters.flite_adapter", "flite_voice":"slt"}
    ,

    {
        "lang":"ar",
        "name":"ar-nah-hsmm",
        "engine":"marytts",
        "adapter":"adapters.marytts_adapter",
        "mapper": {
            "from":"ar_ws-sampa",
            "to":"ar_sampa_mary"
        }
    }    
]



textprocessor_configs = [
    {"name":"marytts_textproc_sv", "lang":"sv",
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
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"sv_se_nst_lex:sv-se.nst"
         }
     ]
    }
    ,
    {"name":"test_textproc_sv", "lang":"sv",
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
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"wikispeech_testdb:sv"
         }
     ]
    }
    ,        
    {"name":"marytts_textproc_nb", "lang":"nb",
     "components":[
         {
             "module":"adapters.marytts_adapter",
             "call":"marytts_preproc"
             ,
             "mapper": {
                 "from":"nb-no_ws-sampa",
                 "to":"nb-no_sampa_mary"
             },
         },
         {
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"no_nob_nst_lex:nb-no.nst"
         }
     ]
    }
    ,

    {"name":"marytts_textproc_nb", "lang":"nb",
     "components":[
         {
             "module":"adapters.marytts_adapter",
             "call":"marytts_preproc"
             ,
             "mapper": {
                 "from":"nb-no_ws-sampa",
                 "to":"nb-no_sampa_mary"
             },
         },
         {
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"wikispeech_testdb:nb"
         }
     ]
    }
    ,


    {"name":"marytts_textproc_en", "lang":"en",
     "components":[
         {
             "module":"adapters.marytts_adapter",
             "call":"marytts_preproc",
             "mapper": {
                 "from":"en-us_ws-sampa",
                 "to":"en-us_sampa_mary"
             },
         },
         {
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"en_am_cmu_lex:en-us.cmu"
         }
     ]
    }
    ,
    {"name":"test_textproc_en", "lang":"en",
     "components":[
         {
             "module":"adapters.marytts_adapter",
             "call":"marytts_preproc",
             "mapper": {
                 "from":"en-us_ws-sampa",
                 "to":"en-us_sampa_mary"
             },
         },
         {
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"wikispeech_testdb:enu"
         }
     ]
    }
    ,

    {
        "name":"ws_textproc_en",
        "lang":"en",
        "components":[
            {
                "module":"tokeniser",
                "call":"tokenise"
            },
            {
                "module":"adapters.lexicon_client",
                "call":"lexLookup",
                "lexicon":"wikispeech_testdb:enu"
            }
        ]
    }
    ,
    {
        "name":"basic_en",
        "lang":"en",
        "components":[
            {
                "module":"tokeniser",
                "call":"tokenise"
            }
        ]
    }
    ,


    {
        "name":"basic_eu",
        "lang":"eu",
        "components":[
            {
                "module":"tokeniser",
                "call":"tokenise"
            }
        ]
    }
    ,


    {"name":"marytts_textproc_ar", "lang":"ar",
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
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"ar_ar_tst_lex:ar-test" 
         }
     ]
    }
    ,


    {"name":"marytts_textproc_ar", "lang":"ar",
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
             "module":"adapters.lexicon_client",
             "call":"lexLookup",
             "lexicon":"wikispeech_testdb:ar" 
         }
     ]
    }

]


voice_configs = [

    # SWEDISH

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

    # NORWEGIAN

    {
        "lang":"nb",
        "name":"stts_no_nst-hsmm",
        "engine":"marytts",
        "adapter":"adapters.marytts_adapter",
        "marytts_locale":"no",
        "mapper": {
            "from":"nb-no_ws-sampa",
            "to":"nb-no_sampa_mary"
            }
    }
    ,

    # ENGLISH
    
    {
        "lang":"en",
        "name":"dfki-spike-hsmm",
        "engine":"marytts",
        "adapter":"adapters.marytts_adapter",
        "marytts_locale":"en_US",
        "mapper": {
            "from":"en-us_ws-sampa",
            "to":"en-us_sampa_mary"
        }
    }
    ,

    {
        "lang":"en",
        "name":"cmu-slt-hsmm",
        "engine":"marytts",
        "adapter":"adapters.marytts_adapter",
        "marytts_locale":"en_US",
        "mapper": {
            "from":"en-us_ws-sampa",
            "to":"en-us_sampa_mary"
        }
    }
    ,

    {
        "lang":"en",
        "name":"cmu-slt-flite",
        "engine":"flite",
        "adapter":"adapters.flite_adapter",
        "flite_voice":"slt"
    }
    ,

    #BASQUE

    # {
    #     "lang":"eu",
    #     "name":"ahotts-eu-female",
    #     "engine":"ahotts",
    #     "adapter":"adapters.ahotts_adapter"
    # }
    # ,



    # ARABIC

    # HL commented out Arabic 2017-09-11
    # HB put it back 2017-09-14
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

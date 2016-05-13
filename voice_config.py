

textprocessor_configs = [
    {"name":"wikitextproc_sv", "lang":"sv", "components":[("tokeniser","tokenise"), ("adapters.marytts_adapter","marytts_preproc_tokenised"), ("wikilex","lexLookup"), ("adapters.marytts_adapter","marytts_postproc")]}
    ,
    {"name":"wikitextproc_en", "lang":"en", "components":[("adapters.marytts_adapter", "marytts_preproc"), ("adapters.marytts_adapter", "marytts_postproc")]}
    ,
    {"name":"wikitextproc_ar", "lang":"ar", "components":[("adapters.marytts_adapter", "marytts_preproc"), ("adapters.marytts_adapter", "marytts_postproc")]}

]


voices = [
    {"lang":"sv", "name":"stts_sv_nst-hsmm", "engine":"marytts", "adapter":"adapters.marytts_adapter", "server":{"url":'https://demo.morf.se/marytts'}}
    ,
    {"lang":"sv", "name":"espeak_mbrola_sv1", "engine":"espeak", "adapter":"espeak_adapter", "espeak_mbrola_voice":"mb-sw1", "espeak_voice":"sv", "program":{"command":'espeak -v mb-sw1'}}
    ,

    {"lang":"en", "name":"dfki-spike-hsmm", "engine":"marytts", "adapter":"adapters.marytts_adapter", "server":{"url":'https://demo.morf.se/marytts'}, "marytts_locale":"en_US"}
    ,
    {"lang":"en", "name":"cmu-slt-hsmm", "engine":"marytts", "adapter":"adapters.marytts_adapter", "server":{"url":'https://demo.morf.se/marytts'}, "marytts_locale":"en_US"}
    ,

    #{"lang":"en", "name":"cmu_slt_hts", "engine":"hts_engine", "adapter":"hts_engine_adapter", "voice_file":"voices/hts_engine/cmu_us_arctic_slt_demo.htsvoice"}
    #,

    {"lang":"en", "name":"cmu-slt-flite", "engine":"flite", "adapter":"flite_adapter", "flite_voice":"slt"}
    ,

    {"lang":"ar", "name":"ar_nah-hsmm", "engine":"marytts", "adapter":"adapters.marytts_adapter", "server":{"url":'https://demo.morf.se/marytts'}}    
]

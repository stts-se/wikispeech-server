Adapters

Enable the wikispeech server to use third-party text processing and synthesis.

Defined in configuration files.

A textprocessing adapter needs to have a function named by the "call" parameter in the config file.

A synthesis adapter needs to have a function "synthesise".

Anything else is optional and depends on the third-party software used.

Textprocessing example:

A marytts adapter is defined in voice_config_marytts.json:

```
   "module":"adapters.marytts_adapter",
   "call":"marytts_preproc"
```

The "module" defines the adapter code, in this case it is found in adapters/marytts_adapter.py

When the wikispeech server runs the textprocessing step, the module is loaded and the text input is sent through the defined call, "marytts_preproc". Arguments to the function are: Text, language, textprocessing configuration options, and input type. A dict is returned containing the processed text.

Synthesis example:

A marytts adapter is defined in voice_config_marytts.json:

```
   "lang":"en",
   "name":"dfki-spike-hsmm",
   "adapter":"adapters.marytts_adapter",
```

When the server runs the synthesis step, the dict containing the processed text is sent through the "synthesis" function. Required arguments are: Language, voice, and input dict. Return values are a pointer to the generated audio and a list of the tokens, with timing if available.



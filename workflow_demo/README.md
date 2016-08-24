workflow_demo

The idea is to have a demo of typical workflow using wikispeech.

1) open html file/url
2) edit html
3) save

4) synthesise text, listen
5) check lexicon for existing words

6) edit existing words in lexicon
7) add words to lexicon
8) listen to transcriptions

Three tabs:
Input, Synthesis, Lexicon

Input is basically a html editor.
A synthesise command sends all? text to wikispeech/synthesis, and then shifts to the synthesis tab, where each paragraph/sentence? is displayed.
A lex_lookup command sends all? text to wikispeech/textprocessing for tokenisation, and then to lexserver for lookup. In the lexicon tab, lists of known and unknown words are displayed. Clicking on a word opens a new tab with a word editor.
Validation of input.

Synthesis displays each paragraph/sentence? from the text, with play controls and connection text/audio. Editing a text here should also be reflected in the input tab (?) - so it's a set of editable html chunks. After edit a text can be resynthesised.
Validation of input.

Lexicon displays two lists of words, known and unknown. Each should have a play button for easy proof-listening. Also show (selected) transcription. IPA? Other information needed here, before edit? And edit button, or click word to edit.

The lexicon entry editor displays editable and uneditable information for the lexicon entry. Uses json schema. Validation of fields. 

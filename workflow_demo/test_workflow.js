

/* Lexicon table TODO not on click of header*/
function setupLexiconTable() {
    $("#words_table tbody tr").click(function(){
	$(this).addClass('selected').siblings().removeClass('selected');    
	var orth=$(this).find('td:eq(0)').html();
	//alert(orth);
	//$("#selected_word").html(orth);
	//var trans=$(this).find('td:eq(1)').html();
	//alert(value);
	//$("#selected_trans").html(trans);

	displaySelected(orth);
    });
}

//make sure that the lexicon table is setup after loading words
$( document ).ajaxComplete(function( event, xhr, settings ) {
    setupLexiconTable();
});


function displaySelected(orth) {
    console.log("Displaying selected: "+orth);
    $("#selected_word").html(orth);

    var selected_table = document.getElementById("selected_table")
    selected_table.innerHTML = "";

    word = entries[orth];
    console.log(word);

    if ( word != null ) {

	for (i=0; i<word.length; i++) {
	    var entry = word[i];
	    console.log(entry);
	    
	    var row = document.createElement("tr");
	    
	    var nr = document.createElement("td");
	    nr.innerHTML = i;
	    row.appendChild(nr)
	    
	    var trans = document.createElement("td");
	    trans.appendChild(makeSSMLTranscription(entry["transcriptions"][0]["strn"]));
	    row.appendChild(trans)
	    
	    var listen = document.createElement("td");
	    listen.innerHTML = '<input type="button" value="Listen">';
	    row.appendChild(listen)

	    var lang = document.createElement("td");
	    lang.innerHTML = entry["language"];
	    row.appendChild(lang)
	    
	    var pos = document.createElement("td");
	    pos.innerHTML = entry["partOfSpeech"];
	    row.appendChild(pos)
	    
	    var pref = document.createElement("td");
	    pref.innerHTML = '<input type="checkbox" value="preferred" >';
	    row.appendChild(pref)
	    
	    selected_table.appendChild(row);
	}

    }

}

function makeSSMLTranscription(transcription) {
    var speak = document.createElement("speak");
    
    //NOTE hardcoded language
    speak.setAttribute("xml:lang", "sv");
	
    speak.setAttribute("version","1.0");
    speak.setAttribute("xmlns", "http://www.w3.org/2001/10/synthesis");
    speak.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance");
    speak.setAttribute("xsi:schemalocation", "http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd");
    

    transcription = transcription.replace(/"/g, "&quot;");
    var ssml = "<p><phoneme alphabet=\"x-sampa\" ph=\""+transcription+"\">"+transcription+"</phoneme></p>";
    speak.innerHTML = ssml;

    return speak;
}

/* Step 1 - send html/text/ssml to wikispeech for textprocessing */
/* Called from Imput tab "tokenise" button */
/* TODO remove hardcoded language */
function tokeniseHtmlText() {
    var html_editor = document.getElementById('html_editor');
    //console.log(html_editor);
    var html = html_editor.innerHTML;

    var ssml_header = '<?xml version="1.0" encoding="UTF-8" ?>\n<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"\n  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n  xsi:schemaLocation="http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd"\nxml:lang="sv">\n';
    var ssml_footer = "</speak>";

    var ssml_content = filterToSSML(html);
    
    var ssml = ssml_header+ssml_content+ssml_footer;
    
    //console.log("Tokenising:\n"+ssml);

    var params = {
	"lang": "sv",
	"input_type": "ssml",
	"input": ssml
    }
    
    $.get(
        'http://localhost/wikispeech/textprocessing',
        params,
        function(response) {
	    console.log(response);

	    if (response.hasOwnProperty("paragraphs")) {
		//console.log("Found utt");
		////addSentencesToSynthesisTab(data.sentences);
		addHtmlSentencesToSynthesisTab();
		
		var data = getSentenceAndTokens(response);
		addWordsToLexiconTab(data.words);

	    } else {
		console.log("ERROR: response is not an utt");
	    }
        }
    );
}

function filterToSSML(html) {
    //Because s and sub have html meanings, they are prefixed with "ssml:"
    var ssml_content = html.replace(/ssml:/g, "")

    //&nbsp; breaks marytts ssml parser.
    //Declare the entity?
    ssml_content = ssml_content.replace(/&nbsp;/g, " ")

    //remove unclosed br tags (even closed come out wrong)
    //ssml_content = ssml_content.replace(/<br>/g, "<br/>")
    ssml_content = ssml_content.replace(/<br>/g, " ")

    return ssml_content;
    
}



function getSentenceAndTokens(utt) {

    var sentencelist = [];
    var words = {};
    
    var paragraphs = utt.paragraphs;
    for ( i=0; i<paragraphs.length; i++ ) {
	var p = paragraphs[i];
	var sentences = p.sentences;
	for ( j=0; j<sentences.length; j++ ) {
	    var s = sentences[j];
	    var phrases = s.phrases;
	    var tokenlist = [];
	    for ( l=0; l<phrases.length; l++ ) {
		var ph = phrases[l];
		var tokens = ph.tokens;
		for ( m=0; m<tokens.length; m++ ) {
		    var token = tokens[m];
		    //console.log(token);
		    var orth = token.token_orth;
		    orth = orth.toLowerCase();
		    tokenlist.push(orth);
		    if (orth in words) {
			words[orth]["freq"] += 1;
		    } else {
			words[orth] = {};
			words[orth]["freq"] = 1;
			var trans = getTranscription(token);
			//transcriptions[orth] = trans;
			words[orth]["transcription"] = trans;
			console.log(token);
			if ( !token.words[0].hasOwnProperty("g2p_method") ) {
			    words[orth]["in_ssml"] = true;
			}
			console.log(orth + " : ")
			console.log(words[orth]);
		    }
		}
	    }
	    sentencelist.push({tokens:tokenlist});
	}
    }
    return {sentences:sentencelist, words: words};
}


function getTranscription(token) {
    var trans = "";
    var words = token.words;
    for ( i=0; i<words.length; i++ ) {
	var w = words[i];
	trans = trans+w.trans;
    }
    return trans;
}

/* Step 2, add sentences in synthesis tab */
/* TODO Is this responsive enough? */
function addHtmlSentencesToSynthesisTab() {
    var html_editor = document.getElementById('html_editor');
    //console.log(html_editor);

    var synthesis_container = document.getElementById("synthesis_container");
    //console.log(synthesis_container);
    synthesis_container.innerHTML = "";

    var text_chunks;

    //Use ssml:s tags if they exist
    text_chunks = html_editor.getElementsByTagName("ssml:s");
    //If there are no sentences, use p tags instead
    if ( text_chunks.length == 0 ) {
	text_chunks = html_editor.getElementsByTagName("p");
	//If there are no p tags, use entire text (?)
	if ( text_chunks.length == 0 ) {
	    text_chunks = [html_editor.innerHTML];
	}
    }


    //console.log("TEXT CHUNKS: ");
    //console.log(text_chunks);


    for ( i=0; i<text_chunks.length; i++ ) {
	var t = text_chunks[i];
	var clone = t.cloneNode(true);
	//console.log("TEXT CHUNK: ");
	//console.log(clone);
	
	var p = document.createElement("p");
	var speak = document.createElement("speak");

	//NOTE hardcoded language
	speak.setAttribute("xml:lang", "sv");
	
	speak.setAttribute("version","1.0");
	speak.setAttribute("xmlns", "http://www.w3.org/2001/10/synthesis");
	speak.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance");
	speak.setAttribute("xsi:schemalocation", "http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd");

	p.appendChild(speak);

	var html = clone.innerHTML;
	//console.log("HTML: "+html);
	var filtered = filterToSSML(html);
	//console.log("Filtered: "+filtered);
	speak.innerHTML = filtered;
	
	synthesis_container.appendChild(p);

	p.setAttribute("class", "ssml");
	
	var id = "sentence_nr_"+i;
	p.setAttribute("id",id);

	var lang = "sv";
	p.setAttribute("lang", lang);
   
	var playButton = document.createElement("input");
	playButton.setAttribute("type", "button");
	playButton.setAttribute("value", "Speak");
	playButton.setAttribute("onclick", "play("+id+");");

	p.appendChild(playButton);

    }	    


}

/*not used any more */
function addSentencesToSynthesisTab(sentences) {
    var synthesis_container = document.getElementById("synthesis_container");
    console.log(synthesis_container);
    synthesis_container.innerHTML = "";

    for ( i=0; i<sentences.length; i++ ) {
	var s = sentences[i].tokens;
	var sentence_text = s.join(" ");

	var p = document.createElement("p");
	var t = document.createTextNode(sentence_text);
	p.appendChild(t);           
	synthesis_container.appendChild(p);
	
	var id = "sentence_nr_"+i;
	p.setAttribute("id",id);

	var lang = "sv";
	p.setAttribute("lang", lang);
   
	var playButton = document.createElement("input");
	playButton.setAttribute("type", "button");
	playButton.setAttribute("value", "Speak");
	playButton.setAttribute("onclick", "play("+id+");");

	p.appendChild(playButton);

    }	    
}


/* Step 3, list words in lexicon tab */

function addWordsToLexiconTab(words) {
    var words_table = document.getElementById("words_table");
    var words_table_tbody = words_table.getElementsByTagName("tbody")[0];
    words_table_tbody.innerHTML = "";

    var sorted_wordlist = Object.keys(words).sort();
    console.log(sorted_wordlist);

    for ( i=0; i<sorted_wordlist.length; i++ ) {
	var orth = sorted_wordlist[i];
	var word = words[orth];
	console.log(orth);
	if ( !orth.match(/^[.,?!]+$/) ) {
	    //console.log("Adding word: "+word);

	    var word_id = "word_"+i;

	    //<div data-role="main" class="ui-content">
	    //<div class="ui-grid-a">
	    //<div class="ui-block-a">
					 
	    var tr = document.createElement("tr");
	    tr.setAttribute("id","entry_"+i);

	    //1
	    var td = document.createElement("td");
	    //td.setAttribute("id",word_id);
	    //td.setAttribute("style", "display: inline-block; width: 10em;");
	    var w = document.createTextNode(orth);
	    td.appendChild(w);
            tr.appendChild(td);

	    //2 frequency
	    var td = document.createElement("td");
	    td.innerHTML = word.freq;
            tr.appendChild(td);

	    //3
	    //Add transcription predicted by synthesiser 
	    var trans = document.createElement("td");
	    trans.setAttribute("id","trans_"+i);
	    //trans.setAttribute("style", "display: inline-block; width: 30em;");
	    trans.setAttribute("class", "ssml");
	    //TODO remove hardcoded language
	    trans.setAttribute("lang", "sv");

	    var speak = document.createElement("speak");

	    //NOTE hardcoded language
	    speak.setAttribute("xml:lang", "sv");
	
	    speak.setAttribute("version","1.0");
	    speak.setAttribute("xmlns", "http://www.w3.org/2001/10/synthesis");
	    speak.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance");
	    speak.setAttribute("xsi:schemalocation", "http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd");

	    var transcription = word.transcription;
	    transcription = transcription.replace(/"/g, "&quot;");
	    var ssml = "<p><phoneme alphabet=\"x-sampa\" ph=\""+transcription+"\">"+transcription+"</phoneme></p>";
	    //var ssml = "<p><phoneme alphabet=\"x-sampa\" ph=\""+transcription+"\">BABIAN</phoneme></p>";
	    //var t = document.createTextNode(ssml);
	    //speak.appendChild(t);
	    speak.innerHTML = ssml;
	    trans.appendChild(speak);
	    tr.appendChild(trans);
	    
	    //4
	    var td = document.createElement("td");
	    var in_lex = document.createElement("input");
	    in_lex.setAttribute("type","checkbox");
	    in_lex.setAttribute("value","in_lex");
	    td.appendChild(in_lex);
	    tr.appendChild(td);
	    
	    //5
	    var td = document.createElement("td");
	    var in_ssml = document.createElement("input");
	    in_ssml.setAttribute("type","checkbox");
	    in_ssml.setAttribute("value","in_ssml");

	    if ( word.hasOwnProperty("in_ssml") && word.in_ssml == true) {
		in_ssml.setAttribute("checked","true");
	    }
	    td.appendChild(in_ssml);
	    tr.appendChild(td);

	    //6
	    var td = document.createElement("td");
	    var multiple = document.createElement("input");
	    multiple.setAttribute("type","checkbox");
	    multiple.setAttribute("value","multiple");
	    td.appendChild(multiple);
	    tr.appendChild(td);

	    //7
	    var td = document.createElement("td");
	    var listen_button = document.createElement("input");
	    listen_button.setAttribute("type","button");
	    listen_button.setAttribute("value","listen");
	    listen_button.setAttribute("onclick", "play($('#trans_"+i+"')[0]);");
	    //listen_button.setAttribute("onclick", "playTranscription($('#trans_"+i+"'));");
	    td.appendChild(listen_button);
	    tr.appendChild(td);
	    



	    

	    words_table_tbody.appendChild(tr);


	} else {
	    console.log("Ignoring: "+word);
	}
    }
    //See if the words are found in lexicon, update table accordingly
    //Better to look up all words first..
    wordsInLex(words);
}



/* Not used - is there any point in no using simple_player.play? */
function playTranscription(t) {
    console.log(t);
    var trans = t[0].innerHTML;
    console.log(trans);
    alert("playTranscription "+trans+" not yet implemented");
}



  
/* Searches for one word/re, used in lexicon editor */
/* TODO Remove hardcoded lexicon name */
function searchLexicon(search_term) {
    console.log("Searching lexicon for: " + search_term);

    var params = {
	"lexicons": "sv-se.nst",
	"words": search_term
    }
    
    $.get(
        'http://localhost/lexicon/lookup',
        params,
        function(response) {
	    console.log(response);
	    entry_editor.setValue(response);
        }
    );

}

/* Not used any more */
function wordInLex(word, div, trans) {
    console.log("Searching lexicon for: " + word);

    var known_words_container = document.getElementById("known_words_container");
    var unknown_words_container = document.getElementById("unknown_words_container");

    var params = {
	"lexicons": "sv-se.nst",
	"words": word
    }
    
    $.get(
        'http://localhost/lexicon/lookup',
        params,
        function(response) {
	    console.log(response);
	    if ( response == null ) {
		console.log("Adding to unknown_words: "+word);
		var transcription = "NONE";
		trans.innerHTML = transcription;
		unknown_words_container.appendChild(div)
	    } else {
		console.log("Adding to known_words: "+word);

		var transcription = response[0].transcriptions[0].strn;
		//var transcription = "' A . p a";
		trans.innerHTML = transcription;

		known_words_container.appendChild(div)
	    }
        }
    );

}



function wordsInLex(words) {
    var wordlist = Object.keys(words).sort();
    var words_to_lookup = wordlist.join();
    
    //console.log("Searching lexicon for: " + words);

    //TODO hardcoded lexicon
    var params = {
	"lexicons": "sv-se.nst",
	"pagelength": 2*wordlist.length,
	"words": words_to_lookup
    }
    
    $.get(
        'http://localhost/lexicon/lookup',
        params,
        function(response) {

	    //response is a list of entries, first convert it to hash with orth as key
	    //GLOBAL for later use
	    entries = {};
	    for (i=1; i<response.length; i += 1) {
		var entry = response[i];
		if ( entry.strn in entries ) {
		    entries[entry.strn].push(entry);
		} else {
		    entries[entry.strn] = [entry];
		}
	    }
	    

	    
	    //console.log(response);
	    for (i=1; i<wordlist.length; i += 1) {
		var word = wordlist[i];
		if ( word.match(/^[.,?!]+$/) ) {
		    console.log("ignoring: "+word);
		    continue;
		}

		var tr = document.getElementById("entry_"+i);

		var in_lex = tr.getElementsByTagName("td")[3].getElementsByTagName("input")[0];
		//console.log(in_lex);

		var multiple = tr.getElementsByTagName("td")[5].getElementsByTagName("input")[0];
		

		var found = false;
		var word = wordlist[i];
		
		if ( word in entries ) {
		    console.log("Adding to known_words: "+word);
		    console.log(entries[word]);
		    
		    
		    in_lex.setAttribute("checked", true);
		    if ( entries[word].length > 1 ) {
			multiple.setAttribute("checked", true);
		    }
		    
		    found = true;
		}
		if ( found == false ) {
		    console.log(word+" not found in lex");
		}
	    }
        }
    );

}

function addPlayButtonToP() {

    var paragraphs = document.getElementsByTagName("p");
    for(i=0; i<paragraphs.length; i++) {
	p = paragraphs[i];

	var id = "paragraph_nr_"+i;
	p.setAttribute("id",id);
   
	var playButton = document.createElement("input");
	playButton.setAttribute("type", "button");
	playButton.setAttribute("value", "Speak");
	playButton.setAttribute("onclick", "play("+id+");");

	p.appendChild(playButton);
    }
	


}


function play(id) {

    console.log("play("+id+")");
    console.log(id);

    //if id is object HTMLParagraphElement ..
    var container = id;

    //else
    //var container = document.getElementById(id);

    var locale;
    var voice;

    var lang;
    if ( container.hasAttribute("lang") ) {
	lang = container.getAttribute("lang");
    } else {
	lang = document.documentElement.lang;
    }
    console.log("LANG: "+lang);


    if (lang === "en") {
	//locale = "en_US";
	locale = "en";
	//marytts voice
	voice = "cmu-slt-hsmm";
	//flite voice
	//voice = "cmu-slt-flite";
	//synth = "marytts";
	synth = "wikispeech";
    } else if (lang === "ar") {
	locale = "ar";
	voice = "ar_nah-hsmm";
	//synth = "marytts";
	synth = "wikispeech";
    } else if (lang == "sv") {
	locale = "sv";
	voice = "stts_sv_nst-hsmm";
	//synth = "marytts";
	synth = "wikispeech";
    } else if (lang == "hi") {
	locale = "hi";
        voice = "./cmu_indic_axb.flitevox"
	//voice = "cmu_indic_sb_hin.flitevox";
	synth = "flite";
    } else if (lang == "mr") {
	locale = "mr";
	voice = "cmu_indic_aup_mr.flitevox";
	synth = "flite";
    } else if (lang == "ta") {
	locale = "ta";
	voice = "cmu_indic_sks_tamil.flitevox";
	synth = "flite";
    } else if (lang == "te") {
	locale = "te";
	voice = "cmu_indic_knr_tel.flitevox";
	synth = "flite";
    } else {
	alert("ERROR: synthesis not supported for document language "+lang);
	return;
    }

    console.log("Locale: "+locale);
    console.log("Voice: "+voice);
    console.log("Synth: "+synth);

    var text = container.textContent.trim();
    console.log(text);


    if ( synth == "marytts" ) {

	//var url = "https://morf.se/marytts/process?INPUT_TYPE=TEXT&OUTPUT_TYPE=REALISED_ACOUSTPARAMS&LOCALE="+locale+"&VOICE="+voice+"&INPUT_TEXT="+encodeURIComponent(text);
	var url = "https://demo.morf.se/marytts/process?INPUT_TYPE=TEXT&OUTPUT_TYPE=REALISED_ACOUSTPARAMS&LOCALE="+locale+"&INPUT_TEXT="+encodeURIComponent(text);
	console.log(url);

	var xhr = new XMLHttpRequest();
	xhr.overrideMimeType('text/xml');
	xhr.open("GET", url, true);
	xhr.send();

	xhr.onload = function() {
	    var responseXML = xhr.responseXML;
	    console.log(responseXML);

	    addTimingInfo(container, responseXML);


	    var audio = document.createElement("audio");
	    container.appendChild(audio);

	    audio.setAttribute("controls", "true");
	    //audio.setAttribute("src", "https://morf.se/marytts/process?INPUT_TYPE=TEXT&OUTPUT_TYPE=AUDIO&AUDIO=WAVE_FILE&LOCALE=sv&VOICE=stts_sv_nst-hsmm&INPUT_TEXT="+encodeURIComponent(text));
            audio.setAttribute("src", "https://demo.morf.se/marytts/process?INPUT_TYPE=TEXT&OUTPUT_TYPE=AUDIO&AUDIO=WAVE_FILE&LOCALE="+locale+"&VOICE="+voice+"&INPUT_TEXT="+encodeURIComponent(text));

	    connectTimingAndAudio(container,audio);

	    audio.play();


	};

	xhr.onerror = function() {
	    console.log('There was an error!');
	};

    } else if ( synth == "flite" ) {

	//var url = "http://localhost/flite/"+locale+"?input="+encodeURIComponent(text);
	var url = "https://morf.se/flite/"+locale+"?input="+encodeURIComponent(text);
	console.log(url);

	var xhr = new XMLHttpRequest();
	xhr.overrideMimeType('text/json');
	xhr.open("GET", url, true);
	xhr.send();

	xhr.onload = function() {
	    var response = JSON.parse(xhr.responseText);
	    //var response = xhr.responseJSON;
	    console.log(response);

	    addTimingInfoFromJson(container, response);


	    var audio = document.createElement("audio");
	    container.appendChild(audio);

	    audio.setAttribute("controls", "true");

	    audio.setAttribute("src", response.audio);


	    connectTimingAndAudio(container,audio);

	    audio.play();


	};

	xhr.onerror = function() {
	    console.log('There was an error!');
	};

    } else if ( synth == "wikispeech" ) {

	//var url = "http://localhost/flite/"+locale+"?input="+encodeURIComponent(text);
	//var url = "https://morf.se/flite/"+locale+"?input="+encodeURIComponent(text);

	//'localhost:10000/wikispeech/?lang=sv&input=hej+hej+din+gamla+babian.'
	var url = "http://localhost/wikispeech/?lang="+locale+"&voice="+voice+"&input="+encodeURIComponent(text);

	console.log("URL: "+url);

	var xhr = new XMLHttpRequest();
	xhr.overrideMimeType('text/json');
	xhr.open("GET", url, true);
	xhr.send();

	xhr.onload = function() {
	    var response = JSON.parse(xhr.responseText);
	    //var response = xhr.responseJSON;
	    console.log(response);

	    addTimingInfoFromJson(container, response);


	    var audio = document.createElement("audio");
	    container.appendChild(audio);

	    audio.setAttribute("controls", "true");

	    audio.setAttribute("src", response.audio);


	    connectTimingAndAudio(container,audio);

	    audio.play();


	};

	xhr.onerror = function() {
	    console.log('There was an error!');
	};


    } else {
	alert("Synthesis mode "+synth+" not defined");
	return;
    }

}

function addTimingInfoFromJson(container, info) {

    var useOriginalText = true;
    if (useOriginalText) {
	var words = container.textContent.split(" ");
	container.innerHTML = "";
    }

    starttime = 0.0;


    tokens = info.tokens;

    console.log("tokens");
    console.log(tokens);

    txt = tokens[1][0].trim();
    //console.log(txt);

    var starttime = 0;
    var endtime;
    var token_duration;

    for(i=0; i<tokens.length; i++) {
	token = tokens[i];
	console.log(token);

	txt = token[0].trim();
	endtime = token[1];
	token_duration = endtime-starttime;
	
	console.log("TOKEN: " + txt);
	console.log("token_duration");
	console.log(token_duration);
		
	if (txt !== null) {
	    word_span = document.createElement("span");
		
	    word_span.setAttribute("class","token");	    
	    word_span.setAttribute("data-dur",token_duration);	    
	    word_span.setAttribute("data-begin",starttime);	    
	    word_span.setAttribute("data-timeindex",i);	    
		
	    word_span.appendChild(document.createTextNode(txt+" "));
	    	
	    console.log('Container: ' + container);
	    container.appendChild(word_span);
	}
	starttime = endtime;
    }
}


function addTimingInfo(container, xmlDoc) {

    var useOriginalText = true;
    if (useOriginalText) {
	var words = container.textContent.split(" ");
	container.innerHTML = "";
    }

    starttime = 0.0;

    phrases = xmlDoc.getElementsByTagName("phrase");

    for(k=0; k<phrases.length; k++) {
    
	var phrase = phrases[k];
	console.log("phrase");
	console.log(phrase);


	tokens = phrase.getElementsByTagName("t");

	console.log("tokens");
	console.log(tokens);

	txt = tokens[1].textContent.trim();
	//console.log(txt);


	for(i=0; i<tokens.length; i++) {
	    token = tokens[i];
	    //console.log(token);


	    phonemes = token.getElementsByTagName("ph");
	    //console.log(phonemes);
	    var token_duration = 0.0;

	    for(j=0; j<phonemes.length; j++) {
		phoneme = phonemes[j];
		token_duration += parseInt(phoneme.getAttribute("d"))*0.001;
	    }
	    endtime = starttime+token_duration;

		
	    txt = token.textContent.trim();
		
	    console.log("WORD: " + txt);
	    console.log("token_duration");
	    console.log(token_duration);
		
	    if (txt !== null) {
		word_span = document.createElement("span");
		
		word_span.setAttribute("class","token");	    
		word_span.setAttribute("data-dur",token_duration);	    
		word_span.setAttribute("data-begin",starttime);	    
		word_span.setAttribute("data-timeindex",i);	    
		
		word_span.appendChild(document.createTextNode(txt+" "));
	    	
		console.log('Container: ' + container);
		container.appendChild(word_span);
	    }
	    starttime = endtime;
	}
	//}
	//every phrase should have on boundary at the end
	var boundary = phrase.getElementsByTagName("boundary")[0];
	var pause_dur = parseInt(boundary.getAttribute("duration"))*0.001;

	console.log("boundary");
	console.log(boundary);
	console.log("pause_dur");
	console.log(pause_dur);

	starttime = starttime+pause_dur;
    }
}


function connectTimingAndAudio(root,audio){
    /**
     * HB gammalt som jag hittade någonstans..
     *
     */


    /**
     * Select next word (at audio.currentTime) when playing starts
     */
    audio.addEventListener('play', function(e){
	selectNextWord();
    }, false);


    /**
     * Abandon seeking the next word because we're paused
     */
    audio.addEventListener('pause', function(e){
	clearTimeout(timeoutSelectNext);
    }, false);


    /**
     * Seek by clicking (event delegation)
     */
    root.addEventListener('click', function(e){
	if(e.target.hasAttribute('data-begin')){
	    var i = e.target.getAttribute('data-timeindex');
	    //audio.currentTime = wordTimes[i].begin + wordTimes[i].dur/2; //@TODO
	    audio.currentTime = wordTimes[i].begin + 0.001; //Note: times apparently cannot be exactly set and sometimes select too early
	    selectNextWord();
	}
    }, false);


    /**
     * Play a word when double-clicking (event delegation)
     * Only plays the single word.
     */
    root.addEventListener('dblclick', function(e){
	audio.play();
    }, false);


    /**
     * Select a word when seeking
     */
    audio.addEventListener('seeked', function(e){
	selectNextWord(e.target.paused /* for hold, probably always true */);
    }, false);

    


    
    /**
     * Build an index of all of the words that can be read along with their begin,
     * and end times, and the DOM element representing the word.
     */
    var wordTimes = [];
    Array.prototype.forEach.call(root.querySelectorAll("[data-begin]"), function(word){
	var wordTime = {
	    begin : parseFloat(word.getAttribute("data-begin")),
	    dur   : parseFloat(word.getAttribute("data-dur")),
	    word  : word
	};
	wordTime.index = wordTimes.length;
	wordTime.end = wordTime.begin + wordTime.dur;
	word.setAttribute('data-timeindex', wordTime.index);
	wordTimes.push(wordTime);
    }
				)


    
    /**
     * Find the next word that should be played (or that is currently being played)
     * @todo Note: this would better be implemented as a binary search
     */ 
    function getNextWordTime(){
	var wordTime = null,
	currentTime = audio.currentTime;
	for(var i = 0, len = wordTimes.length; i < len; i++){
	    var thisWordTime = wordTimes[i];
	    if((currentTime >= thisWordTime.begin && currentTime < thisWordTime.end) || currentTime < wordTimes[i].begin)
	    {
		return thisWordTime;
	    }
	}
	return null;
    }


    var selection = window.getSelection();
    var timeoutSelectNext;

    /**
     * Select the next word that is going to be read or the word that is being
     * read right now
     * @param Boolean hold  Whether or not the subsequent word should automatically be selected
     */
    function selectNextWord(hold){
	clearTimeout(timeoutSelectNext);
	var next = getNextWordTime();	
	if(next){
	    function select(hold){
		selection.removeAllRanges();
		var range = document.createRange();
		range.selectNode(next.word);
		selection.addRange(range);
		if(!hold){
		    timeoutSelectNext = setTimeout(function(){
			selection.removeAllRanges();
			if(!audio.paused)
			    selectNextWord();
		    }, Math.round((next.end - audio.currentTime)*1000));
		}
	    }
	    
	    //Select now
	    if(hold || audio.currentTime >= next.begin){
		select(hold);
	    }
	    //Select later
	    else {
		timeoutSelectNext = setTimeout(function(){
		    select();
		}, Math.round((next.begin - audio.currentTime)*1000));
	    }
	}
    }
}

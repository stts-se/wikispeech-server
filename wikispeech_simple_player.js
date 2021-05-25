


//Default, if the html does not set ws_host 
//HB ws_host = "http://localhost:10000";

//Default, if getSupportedLanguages fails
supported_languages = ["en"];
//getSupportedLanguages();


//can be set to false from js if no controls or 'play-along' is wanted
var useOriginalText = true;
var showControls = true;

function toggleAudioControls() {
    if ( document.getElementById("show_controls_checkbox") != null ) {
	if ( document.getElementById("show_controls_checkbox").checked == false) {
	    console.log("hiding audio controls");
	    $('#synthesis_container audio').attr("style", "display: none");
	} else {
	    console.log("showing audio controls");
	    $('#synthesis_container audio').attr("style", "display: block");
	}
    } else {
	return;
    }
}

    
function addPlayButtonToP() {

    getSupportedLanguages();


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

function getSupportedLanguages() {

    //HB 171117 var url = ws_host+"/languages";
    var url = ws_host+"languages";
    console.log("Getting supported_languages from "+url);

    var xhr = new XMLHttpRequest();
    xhr.overrideMimeType('text/json');
    xhr.open("GET", url, true);
    xhr.send();
    
    xhr.onload = function() {
	var response = JSON.parse(xhr.responseText);
	console.log("supported_languages: "+response)
	supported_languages = response
    }

    xhr.onerror = function() {
	    console.log('ERROR: Unable to get supported languages from '+url);
    };
}

//maybe not needed at all..
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

function play(id) {

    console.log("play("+id+")");
    console.log(id);

    //if id is object HTMLParagraphElement ..
    var container = id;

    //else
    //var container = document.getElementById(id);


    var lang;
    if ( container.hasAttribute("lang") ) {
	lang = container.getAttribute("lang");
    } else {
	lang = document.documentElement.lang;
    }

    var input_type;
    if ( container.hasAttribute("class") ) {
	input_type = container.getAttribute("class");
    } else {
	input_type = "text";
    }

    console.log("LANG: "+lang);
    console.log("INPUT_TYPE: "+input_type);
    console.log("SUPPORTED_LANGUAGES: "+supported_languages);

    if ( supported_languages.indexOf(lang) < 0 ) {
	alert("ERROR: synthesis not supported for language "+lang);
	return;
    }

    console.log("Lang: "+lang);

    if ( input_type == "ssml" ) {
	text = container.getElementsByTagName("speak")[0].outerHTML;
	//Because s and sub have meanings in html, they need to be prefixed with "ssml:"
	text = text.replace(/ssml:/g, "");
    } else {
	var text = container.textContent.trim();
    }
    console.log(text);


    //HB 171117 var url = ws_host+"/";
    var url = ws_host;
    var params = "lang="+lang+"&input_type="+input_type+"&input="+encodeURIComponent(text);

    //HB 9/3 testing to switch English voice
    //if ( lang == "en") {
	//params = params+"&voice=cmu-slt-flite";
    //}
    
    console.log("URL: "+url);
    //console.log("params: "+"lang="+lang+"&input_type="+input_type+"&input="+text);
    console.log("params: "+params);

    var xhr = new XMLHttpRequest();
    xhr.overrideMimeType('text/json');
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.send(params);
    
    xhr.onload = function() {
	var response = JSON.parse(xhr.responseText);
	//var response = xhr.responseJSON;
	console.log(response);
	
	
	//using regular html5 audio
	var audio = document.createElement("audio");

	//using video.js or one html5 audio element
	//var audio = document.getElementById("audio_player");
	//using regular html5 audio

	if (showControls) { // will not work properly with showControls set to true
	    addTimingInfoFromJson(container, response);
	    connectTimingAndAudio(container,audio);
	    audio.setAttribute("controls", "true");
	    container.appendChild(audio);	
	    toggleAudioControls();
	}

	if (response.audio_data) {
	    audio.setAttribute("src", "data:audio/ogg;base64,"+response.audio_data);	    
	} else {
	    audio.setAttribute("src", response.audio);	    
	}
	audio.play();
	    
    };

    xhr.onerror = function() {
	    console.log('There was an error!');
    };



}



function addTimingInfoFromJson(container, info) {

    //Something like this is needed if using one player
    //var speakButton = container.lastChild;
    //console.log("speakButton: "+speakButton);
    //clearOldTimingInfo();

    //when true: doesn't actually use the original text, but replaces it with the tokens from the wikispeech server
    //when false: appends the new tokens after the original text. Doesn't highlight correctly!
    //var useOriginalText = true;

    //var words = container.textContent.trim().split(" ");
    var tmp = container.innerText.trim().split(/\s+/);
    var words = [];
    for(var i=0; i<tmp.length; i++) {    
	var tmp_word = tmp[i];
	var regexp = /^(.+)(,)$/;
	if ( regexp.test(tmp_word) ) {
	    var match = regexp.exec(tmp_word);	    
	    console.log("word "+match[1]+" is followed by "+match[2]);
	    words.push(match[1]);
	    words.push(match[2]);
	} else {
	    words.push(tmp_word);
	}
    }
	
    if (useOriginalText) {
	container.innerHTML = "";
    }

    starttime = 0.0;


    tokens = info.tokens;

    //console.log("tokens");
    //console.log(tokens);

    //skip empty tokens, they just mark silence
    var tmp_tokens = [];
    for(var i=0; i<tokens.length; i++) {
	token = tokens[i];
	txt = token.orth.trim();	
	if ( txt != "" ) {
	    tmp_tokens.push(token);
	}
    }
    tokens = tmp_tokens;



    
    //txt = tokens[1][0].trim();
    //console.log(txt);

    var starttime = 0;
    var endtime;
    var token_duration;

    for(var i=0; i<tokens.length; i++) {
	token = tokens[i];
	console.log(token);

	//words are the old textContents, split on space..
	word = words[i];
	//console.log(word);

	txt = token.orth.trim();	

	if ( token.hasOwnProperty("expanded") ) {
	    txt = txt + " ("+token.expanded+")";
	}

	
	endtime = token.endtime;
	token_duration = endtime-starttime;
	
	//console.log("TOKEN: " + txt);
	console.log("WORD : " + word);
	//console.log("token_duration");
	//console.log(token_duration);
		
	if (txt !== null) {
	    word_span = document.createElement("span");
		
	    word_span.setAttribute("class","token");	    
	    word_span.setAttribute("data-dur",token_duration);	    
	    word_span.setAttribute("data-begin",starttime);	    
	    word_span.setAttribute("data-timeindex",i);	    

	    //Testing ...
	    //word_span.appendChild(document.createTextNode(txt+" "));
	    if (word !== undefined) {
		word_span.appendChild(document.createTextNode(word+" "));
	    }
	    //console.log('Container: ' + container);
	    container.appendChild(word_span);
	}
	starttime = endtime;
    }

    //Something like this is needed if using one player
    //container.appendChild(speakButton);

}

//This is not enough to stop highlighting taking place in many places, if one player is used and one text is synthesised after another. Also remove class=token?
function clearOldTimingInfo() {
    var tokens = document.getElementsByClassName("token");
    var i;
    for (i = 0; i < tokens.length; i++) {
	tokens[i].removeAttribute("data-dur");
	tokens[i].removeAttribute("data-begin");
	tokens[i].removeAttribute("data-timeindex");
    }

}


//Not used any more
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


/**
 * HB comes from https://github.com/westonruter/html5-audio-read-along
 *
 */



function connectTimingAndAudio(root,audio){
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



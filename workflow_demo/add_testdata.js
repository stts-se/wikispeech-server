//1) lägg in ssml i synthesis-tab


var ssml1 = `
    <p><br>
    <ssml:s>
    Fartyget byggdes
    <ssml:sub alias='nittonhundra-femtionio'>1959</ssml:sub> 
    i 
    <phoneme alphabet='x-sampa' ph='&quot; p O . rt u0 . g a l'>Portugal</phoneme> 
    på 
    <phoneme alphabet='x-sampa' ph='E s . t a . &quot; l E j . r O s'>Estaleiros</phoneme> 
    <phoneme alphabet='x-sampa' ph='n a . &quot; v a j s'>Navais</phoneme> 
    <phoneme alphabet='x-sampa' ph='&quot; d E'>de</phoneme> 
    <phoneme alphabet='x-sampa' ph='v I . &quot; a . n a'>Viana</phoneme> 
    <phoneme alphabet='x-sampa' ph='&quot; d O'>do</phoneme> 
    <phoneme alphabet='x-sampa' ph='k a s . &quot; t E . l O'>Castelo</phoneme>
    , och levererades till Färöarna under namnet 
    <phoneme alphabet='x-sampa' ph='&quot; v A: k . b I N . k u0 r'>Vágbingur</phoneme>
    .
    </ssml:s>
    <ssml:s>
    Under 20 års tid tjänstgjorde det som fiskefartyg på 
    <ssml:sub alias='nord-atlanten'>nordatlanten</ssml:sub> 
    innan fartyget 
    <ssml:sub alias='nittonhundra-åttioett'>1981</ssml:sub> 
    såldes till Göteborg, då i namnet 
    <phoneme alphabet='x-sampa' ph='&quot;&quot; b j A: rn . % 9 j'>Bjarnoy</phoneme> 
    <ssml:sub alias='två'>II</ssml:sub>
    .
    </ssml:s>
    <br>
    <ssml:s>
    Dom gav en
    <phoneme alphabet="x-sampa" ph="&quot; d U m">dom</phoneme>
    om en
    <phoneme alphabet="x-sampa" ph="&quot; d o: m">dom</phoneme>
    .
    </ssml:s>
    <br>
    <ssml:s>
    Dom gav en dom om en dom.
    </ssml:s>
    </p>
`;



var ssml2 = "<p><br><ssml:s>Fartyget byggdes i <phoneme alphabet='x-sampa' ph='&quot; p O . rt u0 . g a l'>Portugal</phoneme></ssml:s></p>";



var en_ssml1 = `<p lang="en" class="ssml">
    <br>
    <ssml:s>
    The title of the movie is: 
    <phoneme alphabet="x-sampa" ph="' l A . ' v i . t @ . ' E . ' b E . l A"> La vita è bella</phoneme>,
(Life is beautiful), 
which is directed by 
    <phoneme alphabet="x-sampa" ph="r O . ' b r= . t O . b E . ' n I n . j i">Roberto Benigni</phoneme>.
    </ssml:s>
    </p>
    `;



var ar_text = "<p>الموسوعة الحرة التي يستطيع الجميع تحريرها. توجد الآن 520,523 مقالة بالعربية.</p>"


var no_text = "<p>Søderbergelektroden regnes som en banebrytende oppfinnelse med stor betydning for effektiv produksjon i metallurgisk industri. Spesielt etter andre verdenskrig ble Søderbergelektroden en viktig komponent i kraftkrevende industri i Norge. Lenge etter at Søderbergelektroden ble oppfunnet ble den nominert til Norges største ingeniørbragd.</p>"



function addTestdata(lang) {
    console.log("addTestdata("+lang+")");

    var html_editor = document.getElementById("html_editor");
    html_editor.innerHTML = "";
    
    if (lang === "sv") {
	html_editor.innerHTML = ssml1;
    }
    if (lang === "en") {
	html_editor.innerHTML = en_ssml1;
    }
    if (lang === "ar") {
	html_editor.innerHTML = ar_text;
    }
    if (lang === "nb") {
	html_editor.innerHTML = no_text;
    }
}

var lang = "en";
document.getElementById("language_selector").value = lang;
addTestdata(lang);
//myTabs.goToTab(2);


//Shouldn't have to set ws_hostname here ??
// REMOVED 3/10
//ws_hostname = "http://localhost:10000";
//ws_hostname = "http://localhost";
//ws_hostname = "https://morf.se";
//ws_host = ws_hostname+"/wikispeech";

tokeniseHtmlText(lang);


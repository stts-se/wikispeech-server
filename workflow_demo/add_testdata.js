//1) lägg in ssml i synthesis-tab


var ssml1 = `<p><br>
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
</p>`;



var ssml2 = "<p><br><ssml:s>Fartyget byggdes i <phoneme alphabet='x-sampa' ph='&quot; p O . rt u0 . g a l'>Portugal</phoneme></ssml:s></p>";


var html_editor = document.getElementById("html_editor");
html_editor.innerHTML = ssml1;
    
myTabs.goToTab(2);
tokeniseHtmlText();


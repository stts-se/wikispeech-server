# -*- coding: utf-8 -*-
import xmltodict
import untangle

ssml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                   http://www.w3.org/TR/speech-synthesis/synthesis.xsd"
         xml:lang="en-US">
  
  The title of the movie is: 
  <phoneme alphabet="ipa"
    ph="&#x2C8;l&#x251; &#x2C8;vi&#x2D0;&#x27E;&#x259; &#x2C8;&#x294;e&#x26A; &#x2C8;b&#x25B;l&#x259;"> 
  La vita è bella </phoneme>
  <!-- The IPA pronunciation is ˈlɑ ˈviːɾə ˈʔeɪ ˈbɛlə -->
  (Life is beautiful), 
  which is directed by 
  <phoneme alphabet="ipa"
    ph="&#x279;&#x259;&#x2C8;b&#x25B;&#x2D0;&#x279;&#x27E;o&#x28A; b&#x25B;&#x2C8;ni&#x2D0;nji"> 
  Roberto Benigni </phoneme>
  <!-- The IPA pronunciation is ɹəˈbɛːɹɾoʊ bɛˈniːnji -->

  <!-- Note that in actual practice an author might change the
     encoding to UTF-8 and directly use the Unicode characters in
     the document rather than using the escapes as shown.
     The escaped values are shown for ease of copying. -->
</speak>
"""


doc = xmltodict.parse(ssml)

print(doc["speak"])
print(doc["speak"]["#text"])
print(doc["speak"]["phoneme"])

unp = xmltodict.unparse(doc)
print(unp)

print("-----------------------")

doc = untangle.parse(ssml)
print(doc.speak)
print("-------")
print(doc.speak.children)
print("-------")
print(doc.speak.cdata)
print("-------")
print("#%s#" % doc.speak.cdata[10])

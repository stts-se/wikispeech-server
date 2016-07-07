import lxml.etree as ET

xml_filename = "test/ssml_example1.xml"
xsl_filename = "test/ssml-to-mary.xsl"


dom = ET.parse(xml_filename)
xslt = ET.parse(xsl_filename)
transform = ET.XSLT(xslt)
newdom = transform(dom)
print(ET.tostring(newdom, pretty_print=True))

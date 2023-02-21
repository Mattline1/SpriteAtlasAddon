import xml.etree.ElementTree as xml

# https://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
def XMLIndent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            XMLIndent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def GetMonoXMLHeader(_type):
    root = xml.Element('XnaContent')
    root.attrib['xmlns:ns' ] = 'Microsoft.Xna.Framework'
    asset = xml.SubElement(root, 'Asset')
    asset.attrib['Type'] = _type
    return root, asset

def GetXMLHeader():
    root = xml.Element('Sprites')
    root.attrib['xmlns:ns'] = 'MK.SpriteTools.Addon'
    return root, root

def ExportXml(path, root):
    XMLIndent(root)
    f = open(path, 'wb')
    tree = xml.ElementTree(root)
    tree.write(f, 'UTF-8', xml_declaration=True, short_empty_elements=False )
    f.close()

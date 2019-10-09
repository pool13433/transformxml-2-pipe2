from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring, XML

import xml.etree.ElementTree as ET
import re
import json


class ParserLogic:

    def __init__(self, xmlSourceFileName, xmlTargetFileName):
        self.xmlSourceFileName = xmlSourceFileName
        self.xmlTargetFileName = xmlTargetFileName
        self.arcDict = {'waitingLine' : {},'departure' : 'P?'}

    def read_rawxml(self):
        tree = ET.parse(self.xmlSourceFileName)
        result = {'connection': [], 'waitingLine': [], 'departure': []}
        root = tree.getroot()
        childrens = root.getchildren()
        root.getiterator()
        for child in childrens:
            child_name = child.tag
            for _key in result:
                if child_name == _key:
                    result[_key].append(child.attrib)
        return result

    def draw_place(self, net, place_dict):
        _id = place_dict['id']
        _loc = place_dict['location']
        _group = place_dict['group']

        place = SubElement(net, 'place', {'id': _id})
        graphics = SubElement(place, 'graphics')
        position = SubElement(graphics, 'position', _loc['position'])
        name = SubElement(place, 'name')
        value = SubElement(name, 'value')
        value.text = _id
        graphics = SubElement(name, 'graphics')
        offset = SubElement(graphics, 'offset', _loc['offset0'])
        initialMarking = SubElement(place, 'initialMarking')
        value = SubElement(initialMarking, 'value')
        value.text = 'Default,0'
        graphics = SubElement(initialMarking, 'graphics')
        offset = SubElement(graphics, 'offset', _loc['offset1'])
        capacity = SubElement(place, 'capacity')
        value = SubElement(capacity, 'value')
        value.text = '0'
        self.append_arc(_group,None,{
            'id' : _id
        })

    def draw_transition(self, net, tran_dict):
        _id = tran_dict['id']
        _loc = tran_dict['location']
        _group = tran_dict['group']
        _name = tran_dict['name']
        transition = SubElement(net, 'transition', {'id': _id})
        graphics = SubElement(transition, 'graphics')
        position = SubElement(graphics, 'position', _loc['position'])
        name = SubElement(transition, 'name')
        value = SubElement(name, 'value')
        value.text = _id
        graphics = SubElement(name, 'graphics')
        offset = SubElement(graphics, 'offset', _loc['offset'])

        values = {
            'orientation': '0', 'rate': '0',
            'timed': '0', 'infiniteServer': 'false',
            'priority': '1'
        }
        for _v in values:
            #print('_v::=='+str(_v))
            #print('values[_v]::=='+str(values[_v]))
            orientation = SubElement(transition, _v)
            value = SubElement(orientation, 'value')
            value.text = values[_v]        
        self.append_arc(_group,_name,{'id' : _id})

    def draw_arc(self,net,arc_dict):
        #_id = arc_dict['id']
        _source = arc_dict['source']
        _target = arc_dict['target']

        arc = SubElement(net,'arc',{
                'id':_source+" to "+_target,'source':_source,'target':_target
            })
        graphics = SubElement(arc,'graphics')
        inscription = SubElement(arc,'inscription')
        value = SubElement(inscription,'value')
        value.text = 'Default,1'
        graphics = SubElement(inscription,'graphics')

        tagged = SubElement(arc,'tagged')
        value = SubElement(tagged,'value')
        value.text = 'false'

        SubElement(arc,'arcpath',{'id':"000", 'x':"137", 'y':"184", 'curvePoint':"false"})
        SubElement(arc,'arcpath',{'id':"001", 'x':"181",'y':"157", 'curvePoint':"false"})
        SubElement(arc,'type',{'value':"normal"})

    def write_xml(self):
        raw = self.read_rawxml()
        pnml = Element('pnml')
        net = self.draw_top(pnml)
        loc = {
            'place': {
                'position': {'x': "0.0", 'y': "280.0",'x_gap' : '200','y_gap' : '1'},
                'offset0': {'x': "18.0", 'y': "-8.0"},
                'offset1': {'x': "0.0", 'y': "0.0"}
            },
            'transition': {
                'position': {
                            'x': "100.0", 'y': "250.0",
                            'x_gap' : "200",'y_gap' : "75",
                            'x_init' : '100' , 'y_init' : '250'
                        },
                'offset': {'x': "0.0", 'y': "0.0",}
            }
        }
        server_no = 1 
        line_no =1        
        place_x_gap = loc['place']['position']['x_gap']
        place_y_gap = loc['place']['position']['y_gap']
        tran_x_gap = loc['transition']['position']['x_gap']
        for _key in raw:
            #print('_key::=='+json.dumps(_key))
            place_dict = raw[_key]               
            if 'waitingLine' == _key:
                for _line in place_dict:
                    _len = int(_line['server'])
                    _name = 'P'+str(line_no) #_line['name']
                    print('_len::=='+json.dumps(_len))

                    self.draw_place(net, {
                            'id': 'P'+str(line_no), 'location': loc['place'],
                            'group' : _key
                        })                       
                    self.update_loc(loc,'place',{'name' : 'position','x' : place_x_gap , 'y' : 1})
                    self.update_loc(loc,'place',{'name' : 'offset0','x' : 10 , 'y' : 2})

                    for _seq in range(_len):
                        self.draw_transition(net, {
                            'id': 'T'+str(server_no), 'location': loc['transition'],
                            'group' : _key , 'name' : _name}) 
                        self.update_loc(loc,'transition',{'name' : 'position','x' : 0 , 'y' : 75})
                        #self.update_loc(loc,'transition',{'name' : 'offset','x' : 0 , 'y' : 0})
                        server_no += 1  
                    self.reset_loc(loc,'transition','position')                    
                    line_no += 1  
        if 'departure' in raw:
            self.draw_place(net, {
                'id': 'P'+str(line_no), 'location': loc['place'],
                'group' : _key
            })                       
            self.update_loc(loc,'place',{'name' : 'position','x' : place_x_gap , 'y' : 1})
            self.update_loc(loc,'place',{'name' : 'offset0','x' : 10 , 'y' : 1})                               
        
        for arc_key in self.arcDict:
            #print('arc_key::=='+json.dumps(arc_key))
            _data = self.arcDict[arc_key]
            print('arc_dict::=='+json.dumps(_data))
            if type(_data) is dict:
                print('is dict')
                for p_key in sorted(_data):
                    print('p_key::=='+str(p_key))
                    p_key_next = self.getPidNamNextValue(p_key)
                    print('p_key_next::=='+str(p_key_next))
                    for t_key in _data[p_key]:
                        print('t_key::=='+str(t_key))
                        # draw
                        self.draw_arc(net,{'source' : p_key,'target' : t_key})
                        self.draw_arc(net,{'source' : t_key,'target' : p_key_next})
            elif type(_data) is str:
                print('is str')
                print('_key::=='+str(_data))
                
        self.export_xml(pnml)

    def getPidNamNextValue(self,p_key):
        _int = 1
        ints = re.findall(r'[\d]', p_key)
        strs = re.findall(r'[a-z,A-Z]', p_key)
        print('ints::=='+json.dumps(ints))
        print('strs::=='+json.dumps(strs))
        if len(ints) > 0:
            _int = int(ints[0])+1

        if len(strs) == 1:
            return strs[0]+str(_int)
        else:
            return '-'

    def update_loc(self,loc_origin,loc_group,loc_dict):
        _name = loc_dict['name']
        _x = loc_dict['x']
        _y = loc_dict['y']
        _loc = loc_origin[loc_group][_name]
        _loc['x'] = str(float(_loc['x']) + float(_x))
        _loc['y'] = str(float(_loc['y']) + float(_y))
        return _loc['x'],_loc['y']
    
    def reset_loc(self,loc_origin,loc_group,loc_name):
        _name = loc_name
        _target = loc_origin[loc_group][_name]
        #print('_target::=='+json.dumps(_target))
        _x_gap = _target['x_gap']
        _y_gap = _target['y_gap']
        x_new = str(int(_target['x_init']) + int(_x_gap))
        y_new = str(_target['y_init'])
        _target['x'] = x_new
        _target['y'] = y_new
        _target['x_init'] = x_new
        _target['y_init'] = y_new

    def append_arc(self,arc_tag,arc_name,arc_dict):
        print('arc_tag::=='+str(arc_tag))
        _id = arc_dict['id']
        if 'waitingLine' == arc_tag:            
            if arc_name is not None:
                if arc_name in self.arcDict[arc_tag]:
                    self.arcDict[arc_tag][arc_name].append(_id)
                else:
                    self.arcDict[arc_tag] = {
                        arc_name :  [_id]
                    }
            else:
                old_dict = self.arcDict[arc_tag]
                old_dict[_id] = []
                self.arcDict[arc_tag] = old_dict

        elif 'departure' == arc_tag:
            self.arcDict[arc_tag] = _id         

    def export_xml(self, pnml):
        xmlstr = minidom.parseString(tostring(pnml)).toprettyxml(
            encoding="ISO-8859-1", indent="     ")
        with open(self.xmlTargetFileName, "w") as f:
            f.write(xmlstr)

    def draw_top(self, pnml):
        net = SubElement(pnml, 'net', {
            'id': 'Net-One',
            'type': 'P/T net'
        })
        token = SubElement(net, 'token', {
            'id': "Default",
            'enabled': "true",
            'red': "0",
            'green': "0",
            'blue': "0"
        })
        return net


def main():
    parser = ParserLogic('./Input_queue.xml', './Output_SPN001.xml')
    '''result = parser.read_rawxml()
    print('result::=='+json.dumps(result,indent=1))'''
    result = parser.write_xml()
    print('result::=='+json.dumps(result, indent=1))


if __name__ == "__main__":
    main()

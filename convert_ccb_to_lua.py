
import os
import sys
import xml.etree.ElementTree as ET

def get_real_pos(valName, x, y, ref, tx, ty):
    pos = {}
    if ref == 0 or ref == 1:
        if tx == 0:
            pos['x'] = str(x) 
        elif tx == 1:
            pos['x'] = str(x) + ' * CCB_UI_SCALE'
        else:
            pos['x'] = str(x) + ' * ' + valName + '_ref_size.width'
    else:
        if tx == 0:
            pos['x'] = valName + '_ref_size.width - ' + str(x)
        elif tx == 1:
            pos['x'] = valName + '_ref_size.width - ' + str(x) + ' * CCB_UI_SCALE'
        else:
            pos['x'] = valName + '_ref_size.width - ' + str(x) + ' * ' + valName + '_ref_size.width'

    if ref == 0 or ref == 3:
        if ty == 0:
            pos['y'] = str(y)
        elif ty == 1:
            pos['y'] = str(y) + ' * CCB_UI_SCALE'
        else:
            pos['y'] = str(y) + ' * ' + valName + '_ref_size.height'
    else:
        if ty == 0:
            pos['y'] = valName + '_ref_size.height - ' + str(y) 
        elif ty == 1:
            pos['y'] = valName + '_ref_size.height - ' + str(y) + ' * CCB_UI_SCALE'
        else:
            pos['y'] = valName + '_ref_size.height - ' + str(y) + ' * ' + valName + '_ref_size.height'

    return {'x':pos['x'], 'y':pos['y']}

def get_real_scale(sx, sy, st):
    if st == 0:
        return {'x':str(sx),  'y':str(sy)}
    else:
        return {'x':str(sx) + ' * CCB_UI_SCALE' , 'y':str(sy) + ' * CCB_UI_SCALE'}

def get_properties(properties, valName):
    ret = {}
    records = {}
    for prop in properties:
        i = 0
        name = ''
        type = ''
        value = ''
        while i < len(prop):
            if prop[i].text == 'name':
                name = prop[i + 1].text
            elif prop[i].text == 'type':
                type = prop[i + 1].text
            elif prop[i].text == 'value':
                value = prop[i + 1]
            i += 2 

        if type == 'Position':
            x = float(value[0].text)
            y = float(value[1].text)
            ref = int(value[2].text)
            tx = int(value[3].text)
            ty = int(value[4].text)
            records[name] = {'ref':ref, 'tx':tx, 'ty':ty}
            ret[name] = get_real_pos(valName, x, y, ref, tx, ty)
        elif type == 'Point':
            x = float(value[0].text)
            y = float(value[1].text)
            ret[name] = {'x' : str(x), 'y' : str(y)}
        elif type == 'Size':
            w = float(value[0].text)
            h = float(value[1].text)
            tw = int(value[2].text)
            th = int(value[3].text)
            size = {}
            if tw == 0:
                size['w'] = str(w) 
            elif tw == 1:
                size['w'] = str(w) + ' * CCB_UI_SCALE'
            elif tw == 2:
                size['w'] = str(w) + ' * ' + valName + '_ref_size.width'

            if th == 0:
                size['h'] = str(h) 
            elif th == 1:
                size['h'] = str(h) + ' * CCB_UI_SCALE'
            elif th == 2:
                size['h'] = str(h) + ' * ' + valName + '_ref_size.height' 
            ret[name] = 'cc.size(' + size['w'] + ', ' + size['h'] + ')'
        elif type == 'ScaleLock':
            sx = float(value[0].text)
            sy = float(value[1].text)
            st = int(value[3].text)
            records[name] = st
            ret[name] = get_real_scale(sx, sy, st)

        elif type == 'SpriteFrame':
            tex = value[1].text
            ret[name] = tex
        elif type == 'Color3':
            r = int(float(value[0].text) * 255)
            g = int(float(value[1].text) * 255)
            b = int(float(value[2].text) * 255)
            a = int(float(value[3].text) * 255)
            ret[name] = {'r':r, 'g':g, 'b':b, 'a':a}
        elif type == 'Color4':
            t = 1 if float(value[3].text) > 1 else 255 
            r = int(float(value[0].text) * t)
            g = int(float(value[1].text) * t)
            b = int(float(value[2].text) * t)
            a = int(float(value[3].text) * t)
            ret[name] = {'r':r, 'g':g, 'b':b, 'a':a}
        elif type == 'Degrees':
            r = float(value.text)
            ret[name] = r
        elif type == 'Text':
            ret[name] = value[0].text
        elif type == 'FontTTF':
            ret[name] = value.text
        elif type == 'FloatScale':
            if int(value[1].text) == 0:
                ret[name] = value[0].text
            else:
                ret[name] = value[0].text + ' * CCB_UI_SCALE'
        elif type == 'IntegerLabeled':
            ret[name] = int(value.text)
        elif type == 'Float':
            ret[name] = float(value.text)
        elif type == 'StringSimple':
            ret[name] = value.text
        elif type == 'String':
            ret[name] = value[0].text
        elif type == 'Block':
            ret[name] = {'name':value[0].text, 'type':value[1].text}
        elif type == 'Check':
            ret[name] = value.tag
        elif type == 'FntFile':
            fnt = value.text.split('.')[0]
            ret[name] = 'fonts/' + fnt + '.fnt'
        elif type == 'FloatXY':
            sx = float(value[0].text)
            sy = float(value[1].text)
            ret[name] = {'x':sx, 'y':sy}
        elif type == 'Flip':
            ret[name] = {'x':value[0].tag, 'y':value[1].tag}
        elif type == 'CCBFile':
            ret[name] = value.text
        #else:
            #print 'unhandled type ', type

    return ret, records

def parse_node(dict, name, sequences_size):
    properties = {}
    animatedProperties = {}
    children = {}
    baseClass = ''
    memberVarAssignmentName = ''
    memberVarAssignmentType = 0

    index = 0
    while index < len(dict):
        key = dict[index]
        value = dict[index + 1]
        
        if key.text == 'children':
            children = value
        elif key.text == 'properties':
            properties = value
        elif key.text == 'animatedProperties':
            animatedProperties = value
        elif key.text == 'baseClass':
            baseClass = value.text
        elif key.text == 'memberVarAssignmentName':
            memberVarAssignmentName = value.text
        elif key.text == 'memberVarAssignmentType':
            memberVarAssignmentType = value.text


        index = index + 2

    properties, records = get_properties(properties, name)
    
    # create node
    output = ''
    if baseClass == 'CCNode':
        output += '\tlocal ' + name + ' = cc.Node:create()\n'
    elif baseClass == 'CCNodeColor':
        color = properties['color']
        size = properties['contentSize']
        output += '\tlocal ' + name + " = cc.LayerColor:create(" + 'cc.c4b('+ str(color['r']) + ', ' + str(color['g']) + ', ' + str(color['b']) + ', ' + str(color['a']) + '))\n' 
        output += '\t' + name + ':ignoreAnchorPointForPosition(false)\n'
    elif baseClass == 'CCNodeGradient':
        sc = properties['startColor']
        ec = properties['endColor']
        v = properties['vector']
        vx = -float(v['x'])
        vy = -float(v['y'])
        output += '\tlocal ' + name + ' = cc.LayerGradient:create('
        output += 'cc.c4b('+ str(sc['r']) + ', ' + str(sc['g']) + ', ' + str(sc['b']) + ', ' + str(sc['a']) + '), ' 
        output += 'cc.c4b('+ str(ec['r']) + ', ' + str(ec['g']) + ', ' + str(ec['b']) + ', ' + str(ec['a']) + '), ' 
        output += 'cc.vertex2F(' + str(vx) + ', ' + str(vy) + '))\n'
        output += '\t' + name + ':ignoreAnchorPointForPosition(false)\n'
    elif baseClass == 'CCSprite':
        output += '\tlocal ' + name + " = cc.Sprite:create('" + properties['spriteFrame'] + "')\n"
    elif baseClass == 'CCSprite9Slice':
        output += '\tlocal ' + name + " = cc.Scale9Sprite:create('" + properties['spriteFrame'] + "')\n"
    elif baseClass == 'CCLabelTTF':
        text = properties['string'] if properties['string'] != None else ''
        output += '\tlocal ' + name + " = cc.LabelTTF:create([[" + text + "]], '" + properties['fontName'] + "', " + properties['fontSize'] + ", " + properties['dimensions'] + ", "+ str(properties['horizontalAlignment']) + ", "+ str(properties['verticalAlignment']) + ")\n"
    elif baseClass == 'CCLabelBMFont':
        output += '\tlocal ' + name + " = cc.LabelBMFont:create('" + properties['string'] + "', '" + properties['fntFile'] + "')\n" 
    elif baseClass == 'CCTextField':
        if properties['backgroundSpriteFrame'] != None:
            output += '\tlocal ' + name + ' = cc.EditBox:create(' + properties['preferredSize'] + ", cc.Scale9Sprite:create('" + properties['backgroundSpriteFrame'] + "'))\n"
        else:
            output += '\tlocal ' + name + ' = cc.EditBox:create(' + properties['preferredSize'] + ", cc.Scale9Sprite:create())\n"
        if properties['block']['name'] != None:
            block = properties['block']
            if block['type'] == '2' :
                output += "\t" + name + ":registerScriptEditBoxHandler(function(event, sender) if node." + block['name'] + " then owner." + block['name'] + "(event, sender) end)\n"
            else:
                output += "\t" + name + ":registerScriptEditBoxHandler(function(event, sender) if node." + block['name'] + " then node." + block['name'] + "(event, sender) end)\n"

    elif baseClass == 'CCButton':

        if properties['title'] != None:
            text = properties['title']
            output += "\tlocal label = cc.LabelTTF:create('" + text + "', '" + properties['fontName'] + "', " + properties['fontSize'] + ")\n"
            color = properties['fontColor']
            output += '\tlabel' + ':setColor(' + 'cc.c3b('+ str(color['r']) + ', ' + str(color['g']) + ', ' + str(color['b']) + '))\n' 
            output += '\tlabel:setOpacity(' + str(color['a']) + ')\n'
            temp = properties['outlineColor']
            outlineColor = 'cc.c3b('+ str(temp['r']) + ', ' + str(temp['g']) + ', ' + str(temp['b']) + ')' 
            outlineWidth = properties['outlineWidth']
            output += '\tlabel:enableStroke(' + outlineColor + ', ' + outlineWidth + ')\n'
            output += '\tlabel:enableShadow(cc.p(' + properties['shadowOffset']['x'] + ', ' + properties['shadowOffset']['y']+ "), " + str(properties['shadowColor']['a'] / 255.0) + ", " +  properties['shadowBlurRadius'] + ")\n"
            #output += '\t' + name + ":setTitleLabel(label)\n"

            output += '\tlocal ' + name + ' = cc.ControlButton:create(label, cc.Scale9Sprite:create())\n'
        else:
            output += '\tlocal ' + name + ' = cc.ControlButton:create()\n'

        if properties['backgroundSpriteFrame|Normal'] != None:
            output += '\t' + name + ":setBackgroundSpriteForState(cc.Scale9Sprite:create('" + properties['backgroundSpriteFrame|Normal'] + "'), cc.CONTROL_STATE_NORMAL)\n"
        if properties['backgroundSpriteFrame|Highlighted'] != None:
            output += '\t' + name + ":setBackgroundSpriteForState(cc.Scale9Sprite:create('" + properties['backgroundSpriteFrame|Highlighted'] + "'), cc.CONTROL_STATE_HIGH_LIGHTED)\n"
        if properties['backgroundSpriteFrame|Disabled'] != None:
            output += '\t' + name + ":setBackgroundSpriteForState(cc.Scale9Sprite:create('" + properties['backgroundSpriteFrame|Disabled'] + "'), cc.CONTROL_STATE_DISABLED)\n"
        if properties['backgroundSpriteFrame|Selected'] != None:
            output += '\t' + name + ":setBackgroundSpriteForState(cc.Scale9Sprite:create('" + properties['backgroundSpriteFrame|Selected'] + "'), cc.CONTROL_STATE_SELECTED)\n"
        if properties['block']['name'] != None:
            block = properties['block']
            if block['type'] == '2':
                output += "\t" + name + ":registerControlEventHandler(function() \n\t\tif owner." 
                output += block['name'] + " then \n\t\t\towner." + block['name'] + "(" + name + ") \n\t\tend\n\tend, cc.CONTROL_EVENTTYPE_TOUCH_UP_INSIDE)\n"
            else:
                output += "\t" + name + ":registerControlEventHandler(function() \n\t\tif node." 
                output += block['name'] + " then \n\t\t\tnode." + block['name'] + "(" + name + ") \n\t\tend\n\tend, cc.CONTROL_EVENTTYPE_TOUCH_UP_INSIDE)\n"
        try:
            output += '\t' + name + ':setZoomOnTouchDown(' + properties['zoomWhenHighlighted'] + ')\n'
        except:
            output += '\t' + name + ':setZoomOnTouchDown(false)\n'

        output += "\t" + name + ":setPreferredSize(" + properties['preferredSize'] + ")\n"
    elif baseClass == 'CCScrollView':
        if properties['pagingEnabled'] == 'false':
            output += '\tlocal ' + name + ' = cc.ScrollView:create(' + properties['contentSize'] + ')\n'
        else:
            output += '\tlocal ' + name + ' = cc.TableView:create(' + properties['contentSize'] + ')\n'

        output += '\t' + name + ':ignoreAnchorPointForPosition(false)\n'
        if properties['horizontalScrollEnabled'] == 'true' and properties['verticalScrollEnabled'] == 'true':
            output += '\t' + name + ':setDirection(cc.SCROLLVIEW_DIRECTION_BOTH)\n'
        elif properties['horizontalScrollEnabled'] == 'true':
            output += '\t' + name + ':setDirection(cc.SCROLLVIEW_DIRECTION_HORIZONTAL)\n'
        else:
            output += '\t' + name + ':setDirection(cc.SCROLLVIEW_DIRECTION_VERTICAL)\n'

        output += '\t' + name + ':setBounceable(' + properties['bounces'] + ')\n'
    elif baseClass == 'CCBFile':
        ccbfile = properties['ccbFile']

        output += '\tlocal ' + name + " = require('" + ccbfile.split('.')[0] + "').create(owner or node)\n"
    else:
        print 'unhandled class ', baseClass
        return ''

    # set property
    contentSize = None
    outlineWidth = None
    outlineColor = None
    for prop in properties:
        value = properties[prop]
        if prop == 'position':
            output += '\t' + name + ':setPosition(cc.p(' + value['x'] + ', ' + value['y'] + '))\n'
        elif prop == 'scale':
            output += '\t' + name + ':setScale(' + value['x'] + ', ' + value['y'] + ')\n'
        elif prop == 'anchorPoint':
            output += '\t' + name + ':setAnchorPoint(' + value['x'] + ', ' + value['y'] + ')\n'
        elif prop == 'color':
            output += '\t' + name + ':setColor(' + 'cc.c3b('+ str(value['r']) + ', ' + str(value['g']) + ', ' + str(value['b']) + '))\n' 
        elif prop == 'opacity':
            output += '\t' + name + ':setOpacity(' + str(value * 255) + ')\n'
        elif prop == 'contentSize':
            output += '\t' + name + ':setContentSize(' + value + ')\n'
            contentSize = value
        elif prop == 'rotation':
            output += '\t' + name + ":setRotation(" + str(value) + ')\n'
        elif prop == 'skew':
            output += '\t' + name + ":setSkewX(" + str(value['x']) + ")\n"
            output += '\t' + name + ":setSkewY(" + str(value['y']) + ")\n"
        elif prop == 'outlineColor':
            outlineColor = 'cc.c3b('+ str(value['r']) + ', ' + str(value['g']) + ', ' + str(value['b']) + ')' 
        elif prop == 'outlineWidth':
            outlineWidth = value
        elif prop == 'fontColor':
            if baseClass == 'CCLabelTTF' :
                output += '\t' + name + ':setFontFillColor(' + 'cc.c3b('+ str(value['r']) + ', ' + str(value['g']) + ', ' + str(value['b']) + '))\n' 
        elif prop == 'visible':
            output += '\t' + name + ':setVisible(' + value + ')\n'


        #else:
            #print 'unhandled property ', prop

    if outlineWidth != None and outlineColor != None and baseClass == 'CCLabelTTF':
        output += '\t' + name + ':enableStroke(' + outlineColor + ', ' + outlineWidth + ')\n'

    if memberVarAssignmentName != None:
        if memberVarAssignmentType == '2':
            output += '\towner.' + memberVarAssignmentName + ' = ' + name + '\n'
        else:
            output += '\tnode.' + memberVarAssignmentName + ' = ' + name + '\n'
    elif properties['name'] != None:
        output += '\tnode.' + properties['name'] + ' = ' + name + '\n'

    # parse animatedProperties
    index = 0 
    while index < len(animatedProperties):
        key = animatedProperties[index]
        value = animatedProperties[index + 1]

        if len(value) > 0 and int(key.text) < sequences_size:
            output += "\tsequences[" + key.text + "].nodes[" + name + "] = {"
            i = 0
            while i < len(value):
                action = value[i]
                detail = value[i + 1]

                output += action.text + " = {"

                # record current info.
                output += "{ time = -1, value = "
                if action.text == 'visible' :
                    output += 'false'
                elif action.text == 'rotation':
                    try:
                        output += str(properties['rotation']) + ""
                    except:
                        output += "0"
                elif action.text == 'opacity':
                    try:
                        output += str(properties['opacity'] ) 
                    except:
                        output += "1"
                elif action.text == 'scale':
                    try:
                        output += "{x=" + properties['scale']['x'] + ", y=" + properties['scale']['y'] + "}"
                    except:
                        output += "{x=1,y=1}"
                elif action.text == 'skew':
                    try:
                        output += "{x=" + properties['skew']['x'] + ", y=" + properties['skew']['y'] + "}"
                    except:
                        output += "{x=0,y=0}"
                elif action.text == 'position':
                    try:
                        output += "{x=" + properties['position']['x'] + ", y=" + properties['position']['y'] + "}"
                    except:
                        output += "{x=0,y=0}"
                elif action.text == 'color':
                    try:
                        c = properties['color']
                        output += "{r=" + c['r'] + ', g=' + c['g'] + ', b=' + c['b'] + ', a=' + c['a'] + "}"
                    except:
                        output += "{r=255, g=255, b=255, a=255}"
                elif action.text == 'spriteFrame':
                    output += "'" + properties['spriteFrame'] + "'"

                output += "},"

                keyframes = None
                j = 0
                while j < len(detail):
                    if detail[j].text == 'keyframes':
                        keyframes = detail[j + 1]
                        break
                    j += 2

                k = 0
                while k < len(keyframes):
                    keyframe = keyframes[k]
                    t = 0
                    keyDetail = {} # time and value
                    while t < len(keyframe):
                        v1 = keyframe[t]
                        v2 = keyframe[t + 1]
                        if v1.text == 'value':
                            if action.text == 'rotation' or action.text == 'opacity':
                                keyDetail[v1.text] = v2.text
                            elif action.text == 'scale':
                                temp = get_real_scale(v2[0].text, v2[1].text, records['scale'])
                                keyDetail[v1.text] = "{x=" + temp['x'] + ", y=" + temp['y'] + "}"
                            elif action.text == 'position':
                                record = records['position']
                                temp = get_real_pos(name, v2[0].text, v2[1].text, record['ref'], record['tx'], record['ty'])
                                keyDetail[v1.text] = "{x=" + temp['x'] + ", y=" + temp['y'] + "}"
                            elif action.text == 'scale' or action.text == 'skew' or action.text == 'position':
                                keyDetail[v1.text] = "{x=" + v2[0].text + ", y=" + v2[1].text + "}"
                            elif action.text == 'visible':
                                keyDetail[v1.text] = v2.tag
                            elif action.text == 'color':
                                keyDetail[v1.text] = "{r=" + v2[0].text + ", g=" + v2[1].text + ", b=" + v2[2].text + ", a=" + v2[3].text + "}"
                            elif action.text == 'spriteFrame':
                                keyDetail[v1.text] = v2[0].text
                        elif v1.text == 'time':
                            keyDetail[v1.text] = v2.text

                        t += 2

                    output += "{ time = " + keyDetail['time'] + ", value = " + keyDetail['value'] + "},"
                    
                    k += 1

                output += "},"

                i += 2
            output += "}\n"

        index += 2

    output += '\n'
    if len(children) > 0:
        if contentSize != None:
            output += '\tlocal ' + name + '_self_size = ' + contentSize + '\n'
        else:
            output += '\tlocal ' + name + '_self_size = ' + name + ':getContentSize() \n'

    # add children
    for i in range(len(children)):
        childName = name + '_' + str(i)
        output += '\tlocal ' + childName + '_ref_size = ' + name + '_self_size\n'
        result = parse_node(children[i], childName, sequences_size)
        if len(result) > 0:
            output += result
            output += '\t' + name + ':addChild(' + childName + ')\n\n'
    
    return output 

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: convert_ccb_to_lua xxx.ccb'
        exit(0)

    input = sys.argv[1]
    ccbfile = os.path.basename(input).split('.')[0]
    output  = os.path.dirname(input) + '/' + ccbfile + '.lua'

    print 'converting ', input, output

    tree = ET.parse(input)

    root = tree.getroot()

    dict = root[0]

    index = 0

    sequences = None
    nodeGraph = None
    currentSequenceId = None

    while index < len(dict):
        key = dict[index]
        value = dict[index + 1]

        if key.text == 'nodeGraph':
            nodeGraph = value
        elif key.text == 'sequences':
            sequences = value
        elif key.text == 'currentSequenceId':
            currentSequenceId = value.text

        index += 2

    result = "-- auto created from " + ccbfile + ".ccb\n\n"
    result += "\nlocal sp = require('sp')\n"
    result += "\nlocal " + ccbfile + " = {}\n\n"
    result += "function " + ccbfile + ".create(owner)\n"

    # parse sequences
    if sequences != None:
        result += "\tlocal sequences = {\n"
        for child in sequences:
            i = 0
            info = {}
            while i < len(child):
                key = child[i]
                value = child[i + 1]
                info[key.text] = value

                i += 2

            result += "\t\t[" + info['sequenceId'].text + "] = {\n\t"
            result += "\t\tname = '" + info['name'].text + "',\n\t"
            result += "\t\tlength = " + info['length'].text + ",\n\t"
            result += "\t\tchainedSequenceId = " + info['chainedSequenceId'].text + ",\n\t"
            result += "\t\tautoPlay = " + info['autoPlay'].tag + ",\n\t"
            # try:
            callbackChannel = info['callbackChannel']
            result += "\t\tcallbackChannel = {"
            keyframes = {}
            i = 0
            while i < len(callbackChannel):
                key = callbackChannel[i]
                value = callbackChannel[i + 1]
                if key.text == 'keyframes':
                    keyframes = value
                    break
                i += 2
            for keyframe in keyframes:
                temp = {}
                i = 0
                while i < len(keyframe):
                    key = keyframe[i]
                    value = keyframe[i + 1]
                    temp[key.text] = value
                    i += 2
                if temp['value'][0].text != None:
                    result += "{time = " + temp['time'].text + ", func='" + temp['value'][0].text + "'},"

            result += "},\n"

            result += "\t\t\tnodes = {},\n"
            result += "\t\t},\n"
        result += "\t}\n\n"

    # parse graph
    result += "\tlocal node_ref_size = cc.Director:getInstance():getWinSize()\n"
    result += parse_node(nodeGraph, 'node', 0 if sequences == None else len(sequences))

    if sequences != None:
        result += "\tnode.sequences = sequences\n"
        result += "\tnode.sequence = sequences[" + currentSequenceId + "]\n"
        result += "\tnode.timer = 0\n"
        result += "\tsp.addAnimFuncs(node)\n"

    result += "\tsp.addBasicFuncs(node)\n"
    result += "\n\treturn node\nend\n\nreturn " + ccbfile + "\n"

    f = open(output, 'wt')
    f.write(result.encode('utf-8'))
    f.close()

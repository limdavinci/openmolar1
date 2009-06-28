# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division
import sys
from openmolar.settings import localsettings,fee_keys
from openmolar.ptModules import plan

import struct

class est():
    '''
    this class has attributes suitable for storing in the estimates table
    '''
    def __init__(self):
        self.ix=None
        self.serialno=None
        self.courseno=None
        self.type=""
        self.number=None
        self.itemcode="4001"
        self.description=None
        self.fee=None
        self.ptfee=None
        self.feescale=None
        self.csetype=None
        self.dent=None
        self.completed=None
        self.carriedover=None

    def __repr__(self):
        retarg="("
        for att in self.__dict__:
            retarg+="%s ,"%self.__dict__[att]
        return retarg+")"


    def __str__(self):
        retarg="("
        for att in ("ix","serialno","courseno","number","fee","ptfee","dent"):
            retarg+='%s ,'%self.__dict__[att]
        for att in ("type","itemcode","description","csetype","feescale"):
            retarg+='"%s" ,'%self.__dict__[att]
        for att in ("completed","carriedover"):
            retarg+="%s ,"%self.__dict__[att]
        return "%s)"%retarg.strip(",")

    def toHtmlRow(self):
        return '''<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
        <td>%s</td><td>&pound;%.02f</td><td>&pound;%.02f</td>
        <td>%s</td><td>%s</td><td>%s</td></tr>'''%(
        localsettings.ops.get(self.dent),self.number,self.itemcode,self.type,
        self.description,self.fee/100,self.ptfee/100,self.feescale,
        self.csetype,self.completed)
    def htmlHeader(self):
        return '''<tr><th>Dentist</th><th>number</th><th>code</th>
        <th>input</th><th>Description</th><th>fee</th><th>pt fee</th>
        <th>feescale</th><th>cset</th><th>completed</th></tr>'''
    
def toothTreatDict(pt):
    '''
    cycles through the patient attriubutes,
    and brings up planned / completed treatment on teeth only
    '''
    treats={"pl":[], "cmp":[]}
    for quadrant in ("ur","ul", "ll", "lr"):
        if "r" in quadrant:
            order=(8, 7, 6, 5, 4, 3, 2, 1)
        else:
            order=(1, 2, 3, 4, 5, 6, 7, 8)
        for tooth in order:
            for type in ("pl", "cmp"):
                att="%s%s%s"%(quadrant, tooth,type)
                if pt.__dict__[att] != "":
                    items=pt.__dict__[att].strip(" ").split(" ")
                    for item in items:
                        treats[type].append(("%s%s"%(quadrant, tooth), item), )
    #print "toothTreatDict"
    #print "returning ",treats
    return treats

def abandon_estimate(pt):
    pt.ests=()

def recalculate_estimate(pt):
    planned=plan.plannedDict(pt)
    completed=plan.completedDict(pt)
    if pt.dnt2!=0:
        dent=pt.dnt2
    else:
        dent=pt.dnt1
    for key in planned.keys():
        print key,planned[key]
    for key in completed.keys():
        print key,completed[key]
        
    return
    for treat in chosen:
        #-- treat[0]= the tooth name
        #-- treat[1] = item code
        #-- treat[2]= description
        #-- treat[3]= adjusted fee
        #-- treat[4]=adjusted ptfee
        
        pt.addToEstimate(1, treat[1], treat[2], treat[3], treat[4],
                               dent, self.pt.cset, treat[0])


def toBriefHtml(currEst):
    '''
    returns an HTML table showing the estimate in a receptionist friendly format
    '''
    if currEst==[]:
        retarg='<html><body>No current estimate</body></html>'
        return retarg
    '''just the final row - ie... current estimate'''
    retarg='<html><body><table width ="100%" border="1">'
    retarg+='<tr><td colspan="7"><h3>ESTIMATE</h3></td></tr>'
    retarg+='''<tr><th>No.</th><th>Description</th><th>Type</th><th>Course</th>
    <th>Fee</th><th>Pt Fee</th><th>Completed</th></tr>'''
    total=0
    pt_total=0
    for est in currEst:
        total+=est.fee
        pt_total+=est.ptfee
        retarg+='<tr><td>%s</td><td>%s</td>'%(est.number,est.description)
        retarg+='<td align="center">%s</td>'%est.type
        if est.csetype==None:
            retarg+='<td align="center">?</td>'
        else:
            retarg+='<td align="center">%s</td>'%est.csetype
        retarg+='<td align="right">&pound;%.02f</td>'%(est.fee/100)
        retarg+='<td align="right"><b>&pound;%.02f</b></td>'%(est.ptfee/100)
        retarg+='<td align="center">'
        if est.completed:
            retarg+='YES'
        else:
            retarg+='NO'
        retarg+="</td></tr>"

    retarg+='<tr><td colspan="4"></td>'
    retarg+='<td align="right">&pound;%.02f</td>'%(total/100)
    retarg+='<td align="right"><b>&pound;%.02f</b></td>'%(pt_total/100)
    retarg+='<td></td></tr>'

    retarg+='</table></body></htsml>'

    return retarg

def getCurrentEstimate(rows,tsrows):
    ##OLD CODE.
    dec=()
    if rows!=():
        dec=decode(rows[0][7])
    total=0
    retarg=[]
    for d in dec:
        number_of_items=d[0]
        mult=""
        if int(number_of_items)>1:
            mult="s"
        item=d[1].replace("*",mult)
        if "^" in item:
            item=item.replace("^","")
            number_of_items=""

        retarg.append((number_of_items,item,d[2]))  #(d[0],d[1],d[2]))
        total+=d[2]
    dec=()
    if tsrows!=():
        dec=decodeTS(tsrows[0][4])
    for d in dec:
        number_of_items=d[0]
        mult=""
        if int(number_of_items)>1:
            mult="s"
        item=d[1].replace("*",mult)
        if "^" in item:
            item=item.replace("^","")
            number_of_items=""
        retarg.append((number_of_items,item,d[2]))  #(d[0],d[1],d[2]))
        total+=d[2]

    return (retarg,total)

def decode(blob):
    '''
    old estimates were blocks of 8 bytes - format
    ('N','/x00','ITEM','ITEM','COST','COST','COST','/x00')
    '''
    retlist=[]
    for i in range(0,len(blob),8):
        number=struct.unpack_from('b',blob,i)[0]
        ## this could be a lot tidier.... struct.unpack(bHi,blob)
        ## returns a tuple (number,item,cost)
        item=struct.unpack_from('H',blob,i+2)[0]
        try:
            item_text=localsettings.descriptions['%04d'%item]
        except:
            item_text="unknown item! - '%s'"%item
        cost=struct.unpack_from('i',blob,i+4)[0]
        retlist.append((number,item_text,cost))
    return retlist

def encode(number,item,fee):
    return struct.pack("bHi",number,item,fee)


def decodeTS(blob):
    '''
    old estimates were blocks of 8 bytes - format
    ('N','/x00','ITEM','ITEM','COST','COST','COST','/x00')
    '''
    retlist=[]
    for i in range(0,len(blob),8):
        #print struct.unpack("Hbi",blob[i:i+8])
        item=struct.unpack_from('H',blob,i)[0]
        #--this could be a lot tidier.... struct.unpack(bHi,blob)
        #--returns a tuple (number,item,cost)
        tooth=struct.unpack_from('B',blob,i+2)[0]
        try:
            item_text=localsettings.descriptions['%04d'%item]
        except:
            item_text="unknown item! - '%s'"%item
        cost=struct.unpack_from('i',blob,i+4)[0]
        print "unknown tooth code",tooth
        retlist.append((1,item_text,cost))
    return retlist

if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    localsettings.initiate(False)
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=29833

    pt=patient_class.patient(serialno)
    #print pt.estimates
    #print toHtml(pt.estimates,pt.tsfees)

    #print toBriefHtml(pt.currEstimate)
    #print
    #est=((1,101,1950),(2,1739,5600),(1,6521,0))
    #blob=encode(est)
    #print decode(blob)
    
    recalculate_estimate(pt)
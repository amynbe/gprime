#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""Generic Filtering Routines"""

__author__ = "Don Allingham"

#-------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser,handler,SAXParseException
except:
    from _xmlplus.sax import make_parser,handler,SAXParseException

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
from string import find,join

import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import RelLib
import Date
import Calendar
import Errors
from intl import gettext as _
from Utils import for_each_ancestor

#-------------------------------------------------------------------------
#
# date_cmp
#
#-------------------------------------------------------------------------
def date_cmp(rule,value):
    sd = rule.get_start_date()
    s = sd.mode
    if s == Calendar.BEFORE:
        return Date.compare_dates(rule,value) == 1
    elif s == Calendar.AFTER:
        return Date.compare_dates(rule,value) == -1
    elif sd.month == Date.UNDEF and sd.year != Date.UNDEF:
        return sd.year == value.get_start_date().year
    else:
        return Date.compare_dates(rule,value) == 0

#-------------------------------------------------------------------------
#
# Rule
#
#-------------------------------------------------------------------------
class Rule:
    """Base rule class"""

    labels = []
    
    def __init__(self,list):
        assert(type(list) == type([]),"Argument is not a list")
        self.list = list

    def values(self):
        return self.list

    def trans_name(self):
        return _(self.name())
    
    def name(self): 
        return 'None'
    
    def check(self):
        return len(self.list) == len(self.labels)

    def apply(self,db,p):
        return 1

    def display_values(self):
        v = []
        for i in range(0,len(self.list)):
            if self.list[i]:
                v.append('%s="%s"' % (_(self.labels[i]),self.list[i]))
        return join(v,'; ')

#-------------------------------------------------------------------------
#
# Everyone
#
#-------------------------------------------------------------------------
class Everyone(Rule):
    """Matches Everyone"""

    labels = []
    
    def name(self):
        return 'Everyone'

    def apply(self,db,p):
        return 1

#-------------------------------------------------------------------------
#
# HasIdOf
#
#-------------------------------------------------------------------------
class HasIdOf(Rule):
    """Rule that checks for a person with a specific GID"""

    labels = [ _('ID:') ]
    
    def name(self):
        return 'Has the Id'

    def apply(self,db,p):
        return p.getId() == self.list[0]

#-------------------------------------------------------------------------
#
# IsFemale
#
#-------------------------------------------------------------------------
class IsFemale(Rule):
    """Rule that checks for a person that is a female"""

    labels = []
    
    def name(self):
        return 'Is a female'

    def apply(self,db,p):
        return p.getGender() == RelLib.Person.female

#-------------------------------------------------------------------------
#
# IsDescendantOf
#
#-------------------------------------------------------------------------
class IsDescendantOf(Rule):
    """Rule that checks for a person that is a descendant
    of a specified person"""

    labels = [ _('ID:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}

    def name(self):
        return 'Is a descendant of'

    def apply(self,db,p):
        self.orig = p

        if not self.init:
            self.init = 1
            root = db.getPerson(self.list[0])
            self.init_list(root)
        return self.map.has_key(p.getId())

    def init_list(self,p):
        if self.map.has_key(p.getId()) == 1:
            loop_error(self.orig,p)
        self.map[p.getId()] = 1
        
        for fam in p.getFamilyList():
            for child in fam.getChildList():
                self.init_list(child)

#-------------------------------------------------------------------------
#
# IsDescendantFamilyOf
#
#-------------------------------------------------------------------------
class IsDescendantFamilyOf(Rule):
    """Rule that checks for a person that is a descendant or the spouse
    of a descendant of a specified person"""

    labels = [ _('ID:') ]
    
    def name(self):
        return "Is a descendant family member of"

    def apply(self,db,p):
        self.map = {}
        self.orig = p
        return self.search(p,1)

    def search(self,p,val):
        if self.map.has_key(p.getId()):
            loop_error(self.orig,p)
        if p.getId() == self.list[0]:
            self.map[p.getId()] = 1
            return 1
        for (f,r1,r2) in p.getParentList():
            for p1 in [f.getMother(),f.getFather()]:
                if p1:
                    if self.search(p1,0):
                        return 1
        if val:
            for fm in p.getFamilyList():
                if p == fm.getFather():
                    s = fm.getMother()
                else:
                    s = fm.getFather()
                if s:
                    if self.search(s,0):
                        return 1
            
        return 0

#-------------------------------------------------------------------------
#
# IsAncestorOf
#
#-------------------------------------------------------------------------
class IsAncestorOf(Rule):
    """Rule that checks for a person that is an ancestor of a specified person"""

    labels = [ _('ID:') ]

    def __init__(self,list):
        Rule.__init__(self,list)
        self.init = 0
        self.map = {}
    
    def name(self):
        return 'Is an ancestor of'

    def apply(self,db,p):
        self.orig = p
        if not self.init:
            self.init = 1
            root = db.getPerson(self.list[0])
            self.init_ancestor_list(root)
        return self.map.has_key(p.getId())

    def init_ancestor_list(self,p):
        if self.map.has_key(p.getId()) == 1:
            loop_error(self.orig,p)
        self.map[p.getId()] = 1
        
        fam = p.getMainParents()
        if fam:
            f = fam.getFather()
            m = fam.getMother()
        
            if f:
                self.init_ancestor_list(f)
            if m:
                self.init_ancestor_list(m)

#-------------------------------------------------------------------------
#
# HasCommonAncestorWith
#
#-------------------------------------------------------------------------
class HasCommonAncestorWith(Rule):
    """Rule that checks for a person that has a common ancestor with a specified person"""

    labels = [ _('ID:') ]

    def name(self):
        return 'Has a common ancestor with'

    def __init__(self,list):
        Rule.__init__(self,list)
        # Keys in `ancestor_cache' are ancestors of list[0].
        # We delay the computation of ancestor_cache until the
        # first use, because it's not uncommon to instantiate
        # this class and not use it.
        self.ancestor_cache = {}

    def init_ancestor_cache(self,db):
        # list[0] is an Id, but we need to pass a Person to for_each_ancestor.
        p = db.getPerson(self.list[0])
        if p:
            def init(self,pid): self.ancestor_cache[pid] = 1
            for_each_ancestor([p],init,self)

    def apply(self,db,p):
        # On the first call, we build the ancestor cache for the
        # reference person.   Then, for each person to test,
        # we browse his ancestors until we found one in the cache.
        if len(self.ancestor_cache) == 0:
            self.init_ancestor_cache(db)
        return for_each_ancestor([p],
                                 lambda self,p: self.ancestor_cache.has_key(p),
                                 self);

#-------------------------------------------------------------------------
#
# IsMale
#
#-------------------------------------------------------------------------
class IsMale(Rule):
    """Rule that checks for a person that is a male"""

    labels = []
    
    def name(self):
        return 'Is a male'

    def apply(self,db,p):
        return p.getGender() == RelLib.Person.male

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasEvent(Rule):
    """Rule that checks for a person with a particular value"""

    labels = [ _('Personal event:'), _('Date:'), _('Place:'), _('Description:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list[0]:
            self.date = Date.Date()
            self.date.set(self.list[0])
        else:
            self.date = None

    def name(self):
        return 'Has the personal event'

    def apply(self,db,p):
        for event in p.getEventList():
            val = 1
            if self.list[0] and event.getName() != self.list[0]:
                val = 0
            if self.list[3] and find(event.getDescription().upper(),
                                     self.list[3].upper())==-1:
                val = 0
            if self.date:
                if date_cmp(self.date,event.getDateObj()):
                    val = 0
            if self.list[2]:
                pn = event.getPlaceName()
                if find(pn.upper(),self.list[2].upper()) == -1:
                    val = 0
            if val == 1:
                return 1
        return 0

#-------------------------------------------------------------------------
#
# HasFamilyEvent
#
#-------------------------------------------------------------------------
class HasFamilyEvent(Rule):
    """Rule that checks for a person who has a relationship event
    with a particular value"""

    labels = [ _('Family event:'), _('Date:'), _('Place:'), _('Description:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list[0]:
            self.date = Date.Date()
            self.date.set(self.list[0])
        else:
            self.date = None

    def name(self):
        return 'Has the family event'

    def apply(self,db,p):
        for f in p.getFamilyList():
            for event in f.getEventList():
                val = 1
                if self.list[0] and event.getName() != self.list[0]:
                    val = 0
                v = self.list[3]
                if v and find(event.getDescription().upper(),v.upper())==-1:
                    val = 0
                if self.date:
                    if date_cmp(self.date,event.getDateObj()):
                        val = 0
                pn = event.getPlaceName().upper()
                if self.list[2] and find(pn,self.list[2].upper()) == -1:
                    val = 0
                if val == 1:
                    return 1
        return 0

#-------------------------------------------------------------------------
#
# HasRelationship
#
#-------------------------------------------------------------------------
class HasRelationship(Rule):
    """Rule that checks for a person who has a particular relationship"""

    labels = [ _('Number of relationships:'),
               _('Relationship type:'),
               _('Number of children:') ]

    def name(self):
        return 'Has the relationships'

    def apply(self,db,p):
        rel_type = 0
        cnt = 0
        num_rel = len(p.getFamilyList())

        # count children and look for a relationship type match
        for f in p.getFamilyList():
            cnt = cnt + len(f.getChildList())
            if self.list[1] and f.getRelationship() == self.list[1]:
                rel_type = 1

        # if number of relations specified
        if self.list[0]:
            try:
                v = int(self.list[0])
            except:
                return 0
            if v != num_rel:
                return 0

        # number of childred
        if self.list[2]:
            try:
                v = int(self.list[2])
            except:
                return 0
            if v != cnt:
                return 0

        # relation
        if self.list[1]:
            return rel_type == 1
        else:
            return 1

#-------------------------------------------------------------------------
#
# HasBirth
#
#-------------------------------------------------------------------------
class HasBirth(Rule):
    """Rule that checks for a person with a birth of a particular value"""

    labels = [ _('Date:'), _('Place:'), _('Description:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list[0]:
            self.date = Date.Date()
            self.date.set(self.list[0])
        else:
            self.date = None
        
    def name(self):
        return 'Has the birth'

    def apply(self,db,p):
        event = p.getBirth()
        ed = event.getDescription().upper()
        if len(self.list) > 2 and find(ed,self.list[2].upper())==-1:
            return 0
        if self.date:
            if date_cmp(self.date,event.getDateObj()) == 0:
                return 0
        pn = event.getPlaceName().upper()
        if len(self.list) > 1 and find(pn,self.list[1].upper()) == -1:
            return 0
        return 1

#-------------------------------------------------------------------------
#
# HasDeath
#
#-------------------------------------------------------------------------
class HasDeath(Rule):
    """Rule that checks for a person with a death of a particular value"""

    labels = [ _('Date:'), _('Place:'), _('Description:') ]
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list[0]:
            self.date = Date.Date()
            self.date.set(self.list[0])
        else:
            self.date = None

    def name(self):
        return 'Has the death'

    def apply(self,db,p):
        event = p.getDeath()
        ed = event.getDescription().upper()
        if self.list[2] and find(ed,self.list[2].upper())==-1:
            return 0
        if self.date:
            if date_cmp(self.date,event.getDateObj()) == 0:
                return 0
        pn = p.getPlaceName().upper()
        if self.list[1] and find(pn,self.list[1].upper()) == -1:
            return 0
        return 1

#-------------------------------------------------------------------------
#
# HasAttribute
#
#-------------------------------------------------------------------------
class HasAttribute(Rule):
    """Rule that checks for a person with a particular personal attribute"""

    labels = [ _('Personal attribute:'), _('Value:') ]
    
    def name(self):
        return 'Has the personal attribute'

    def apply(self,db,p):
        for event in p.getAttributes():
            if self.list[0] and event.getType() != self.list[0]:
                return 0
            ev = event.getValue().upper()
            if self.list[1] and find(ev,self.list[1].upper())==-1:
                return 0
        return 1

#-------------------------------------------------------------------------
#
# HasFamilyAttribute
#
#-------------------------------------------------------------------------
class HasFamilyAttribute(Rule):
    """Rule that checks for a person with a particular family attribute"""

    labels = [ _('Family attribute:'), _('Value:') ]
    
    def name(self):
        return 'Has the family attribute'

    def apply(self,db,p):
        for f in p.getFamilyList():
            for event in f.getAttributes():
                val = 1
                if self.list[0] and event.getType() != self.list[0]:
                    val = 0
                ev = event.getValue().upper()
                if self.list[1] and find(ev,self.list[1].upper())==-1:
                    val = 0
                if val == 1:
                    return 1
        return 0

#-------------------------------------------------------------------------
#
# HasNameOf
#
#-------------------------------------------------------------------------
class HasNameOf(Rule):
    """Rule that checks for full or partial name matches"""

    labels = [_('Given name:'),_('Family name:'),_('Suffix:'),_('Title:')]
    
    def name(self):
        return 'Has a name'
    
    def apply(self,db,p):
        self.f = self.list[0]
        self.l = self.list[1]
        self.s = self.list[2]
        self.t = self.list[3]
        for name in [p.getPrimaryName()] + p.getAlternateNames():
            val = 1
            if self.f and find(name.getFirstName().upper(),self.f.upper()) == -1:
                val = 0
            if self.l and find(name.getSurname().upper(),self.l.upper()) == -1:
                val = 0
            if self.s and find(name.getSuffix().upper(),self.s.upper()) == -1:
                val = 0
            if self.t and find(name.getTitle().upper(),self.t.upper()) == -1:
                val = 0
            if val == 1:
                return 1
        return 0

    
#-------------------------------------------------------------------------
#
# MatchesFilter
#
#-------------------------------------------------------------------------
class MatchesFilter(Rule):
    """Rule that checks against another filter"""

    labels = [_('Filter name:')]

    def name(self):
        return 'Matches the filter named'

    def apply(self,db,p):
        for filter in SystemFilters.get_filters():
            if filter.get_name() == self.list[0]:
                return filter.check(p)
        for filter in CustomFilters.get_filters():
            if filter.get_name() == self.list[0]:
                return filter.check(db,p)
        return 0

#-------------------------------------------------------------------------
#
# loop_error
#
#-------------------------------------------------------------------------
def loop_error(p1,p2):
    p1name = p1.getPrimaryName().getName()
    p2name = p2.getPrimaryName().getName()
    p1id = p1.getId()
    p2id = p2.getId()
    raise Errors.FilterError(_("Loop detected while applying filter"),
                             _("A relationship loop was detected between %s [%s] "
                               "and %s [%s]. This is probably due to an error in the "
                               "database.") % (p1name,p1id,p2name,p2id))
    
#-------------------------------------------------------------------------
#
# GenericFilter
#
#-------------------------------------------------------------------------
class GenericFilter:
    """Filter class that consists of several rules"""
    
    def __init__(self,source=None):
        if source:
            self.flist = source.flist[:]
            self.name = source.name
            self.comment = source.comment
            self.logical_op = source.logical_op
            self.invert = source.invert
        else:
            self.flist = []
            self.name = ''
            self.comment = ''
            self.logical_op = 'and'
            self.invert = 0

    def set_logical_op(self,val):
        if val in const.logical_functions:
            self.logical_op = val
        else:
            self.logical_op = 'and'

    def get_logical_op(self):
        return self.logical_op

    def set_invert(self, val):
        self.invert = not not val

    def get_invert(self):
        return self.invert
    
    def get_name(self):
        return self.name
    
    def set_name(self,name):
        self.name = name

    def set_comment(self,comment):
        self.comment = comment

    def get_comment(self):
        return self.comment
    
    def add_rule(self,rule):
        self.flist.append(rule)

    def delete_rule(self,rule):
        self.flist.remove(rule)

    def set_rules(self,rules):
        self.flist = rules

    def get_rules(self):
        return self.flist

    def check_or(self,db,p):
        test = 0
        for rule in self.flist:
            test = test or rule.apply(db,p)
            if test:
                break
        if self.invert:
            return not test
        else:
            return test

    def check_xor(self,db,p):
        test = 0
        for rule in self.flist:
            temp = rule.apply(db,p)
            test = ((not test) and temp) or (test and (not temp))
        if self.invert:
            return not test
        else:
            return test

    def check_one(self,db,p):
        count = 0
        for rule in self.flist:
            if rule.apply(db,p):
                count = count + 1
                if count > 1:
                    break
        if self.invert:
            return count != 1
        else:
            return count == 1

    def check_and(self,db,p):
        test = 1
        for rule in self.flist:
            test = test and rule.apply(db,p)
            if not test:
                break
        if self.invert:
            return not test
        else:
            return test
    
    def get_check_func(self):
        try:
            m = getattr(self, 'check_' + self.logical_op)
        except AttributeError:
            m = self.check_and
        return m

    def check(self,db,p):
        return self.get_check_func()(db,p)

    def apply(self,db,list):
        m = self.get_check_func()
        res = []
        for p in list:
            if m(db,p):
                res.append(p)
        return res


#-------------------------------------------------------------------------
#
# Name to class mappings
#
#-------------------------------------------------------------------------
tasks = {
    _("Everyone")                        : Everyone,
    _("Has the Id")                      : HasIdOf,
    _("Has a name")                      : HasNameOf,
    _("Has the relationships")           : HasRelationship,
    _("Has the death")                   : HasDeath,
    _("Has the birth")                   : HasBirth,
    _("Is a descendant of")              : IsDescendantOf,
    _("Is a descendant family member of"): IsDescendantFamilyOf,
    _("Is an ancestor of")               : IsAncestorOf,
    _("Has a common ancestor with")      : HasCommonAncestorWith,
    _("Is a female")                     : IsFemale,
    _("Is a male")                       : IsMale,
    _("Has the personal event")          : HasEvent,
    _("Has the family event")            : HasFamilyEvent,
    _("Has the personal attribute")      : HasAttribute,
    _("Has the family attribute")        : HasFamilyAttribute,
    _("Matches the filter named")        : MatchesFilter,
    }

#-------------------------------------------------------------------------
#
# GenericFilterList
#
#-------------------------------------------------------------------------
class GenericFilterList:
    """Container class for the generic filters. Stores, saves, and
    loads the filters."""
    
    def __init__(self,file):
        self.filter_list = []
        self.file = os.path.expanduser(file)

    def get_filters(self):
        return self.filter_list
    
    def add(self,filter):
        self.filter_list.append(filter)
        
    def load(self):
        try:
            parser = make_parser()
            parser.setContentHandler(FilterParser(self))
            if self.file[0:7] != "file://":
                parser.parse("file://" + self.file)
            else:
                parser.parse(self.file)
        except (IOError,OSError,SAXParseException):
            pass

    def fix(self,line):
        l = line.strip()
        l = l.replace('&','&amp;')
        l = l.replace('>','&gt;')
        l = l.replace('<','&lt;')
        return l.replace('"','&quot;')

    def save(self):
#        try:
#            f = open(self.file,'w')
#        except:
#            return

        f = open(self.file.encode('iso8859-1'),'w')
        
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        f.write('<filters>\n')
        for i in self.filter_list:
            f.write('  <filter name="%s"' % self.fix(i.get_name()))
            if i.get_invert():
                f.write(' invert="1"')
            f.write(' function="%s"' % i.get_logical_op())
            comment = i.get_comment()
            if comment:
                f.write(' comment="%s"' % self.fix(comment))
            f.write('>\n')
            for rule in i.get_rules():
                f.write('    <rule class="%s">\n' % self.fix(rule.name()))
                for v in rule.values():
                    f.write('      <arg value="%s"/>\n' % self.fix(v))
                f.write('    </rule>\n')
            f.write('  </filter>\n')
        f.write('</filters>\n')
        f.close()

#-------------------------------------------------------------------------
#
# FilterParser
#
#-------------------------------------------------------------------------
class FilterParser(handler.ContentHandler):
    """Parses the XML file and builds the list of filters"""
    
    def __init__(self,gfilter_list):
        handler.ContentHandler.__init__(self)
        self.gfilter_list = gfilter_list
        self.f = None
        self.r = None
        self.a = []
        self.cname = None
        
    def setDocumentLocator(self,locator):
        self.locator = locator

    def startElement(self,tag,attrs):
        if tag == "filter":
            self.f = GenericFilter()
            self.f.set_name(attrs['name'])
            if attrs.has_key('function'):
                try:
                    if int(attrs['function']):
                        op = 'or'
                    else:
                        op = 'and'
                except ValueError:
                    op = attrs['function']
                self.f.set_logical_op(op)
            if attrs.has_key('comment'):
                self.f.set_comment(attrs['comment'])
            if attrs.has_key('invert'):
                try:
                    self.f.set_invert(int(attrs['invert']))
                except ValueError:
                    pass
            self.gfilter_list.add(self.f)
        elif tag == "rule":
            cname = attrs['class']
            name = _(cname)
            self.a = []
            self.cname = tasks[name]
        elif tag == "arg":
            self.a.append(attrs['value'])

    def endElement(self,tag):
        if tag == "rule":
            rule = self.cname(self.a)
            self.f.add_rule(rule)
            
    def characters(self, data):
        pass


#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------
SystemFilters = None
CustomFilters = None

def reload_system_filters():
    global SystemFilters
    SystemFilters = GenericFilterList(const.system_filters)
    SystemFilters.load()
    
def reload_custom_filters():
    global CustomFilters
    CustomFilters = GenericFilterList(const.custom_filters)
    CustomFilters.load()
    
if not SystemFilters:
    reload_system_filters()

if not CustomFilters:
    reload_custom_filters()

def build_filter_menu(local_filters = []):
    menu = gtk.Menu()

    for filter in local_filters:
        menuitem = gtk.MenuItem(filter.get_name())
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filter)

    for filter in SystemFilters.get_filters():
        menuitem = gtk.MenuItem(_(filter.get_name()))
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filter)

    for filter in CustomFilters.get_filters():
        menuitem = gtk.MenuItem(_(filter.get_name()))
        menuitem.show()
        menu.append(menuitem)
        menuitem.set_data("filter", filter)

    if len(local_filters):
        menu.set_active(2)
    elif len(SystemFilters.get_filters()):
        menu.set_active(4 + len(local_filters))
    elif len(CustomFilters.get_filters()):
        menu.set_active(6 + len(local_filters) + len(SystemFilters.get_filters()))
    else:
        menu.set_active(0)
        
    return menu

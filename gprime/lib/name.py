#
# gPrime - A web-based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Doug Blank <doug.blank@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Name class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gprime modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .privacybase import PrivacyBase
from .citationbase import CitationBase
from .notebase import NoteBase
from .datebase import DateBase
from .surnamebase import SurnameBase
from .nametype import NameType
from .handle import Handle
from .const import IDENTICAL, EQUAL, DIFFERENT
from .date import Date
from gprime.const import LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Personal Name
#
#-------------------------------------------------------------------------
class Name(SecondaryObject, PrivacyBase, SurnameBase, CitationBase, NoteBase,
           DateBase):
    """
    Provide name information about a person.

    A person may have more that one name throughout his or her life. The Name
    object stores one of them
    """

    DEF = 0    # Default format (determined by gramps-wide prefs)
    LNFN = 1   # last name first name
    FNLN = 2   # first name last name
    FN = 4     # first name
    LNFNP = 5  # primary name primconnector rest, given pa/ma suffix, primprefix

    NAMEFORMATS = (DEF, LNFN, FNLN, FN, LNFNP)
    #deprecated :
    PTFN = 3  # patronymic first name

    def __init__(self, source=None):
        """Create a new Name instance, copying from the source if provided.
        We should connect here to 'person-groupname-rebuild' and do something
        correct when first parameter is the name, and second parameter is
        different from the group here. However, that would be complicated and
        no real errors that cannot be ammended can be done if group is
        saved differently.
        """
        PrivacyBase.__init__(self, source)
        SurnameBase.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        DateBase.__init__(self, source)
        if source:
            self.copy_from(source)
        else:
            self.first_name = ""
            self.suffix = ""
            self.title = ""
            self.type = NameType()
            self.group_as = ""
            self.sort_as = self.DEF
            self.display_as = self.DEF
            self.call = ""
            self.nick = ""
            self.famnick = ""

    def copy_from(self, source):
        self.first_name = source.first_name
        self.suffix = source.suffix
        self.title = source.title
        self.type = NameType(source.type)
        self.group_as = source.group_as
        self.sort_as = source.sort_as
        self.display_as = source.display_as
        self.call = source.call
        self.nick = source.nick
        self.famnick = source.famnick

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.

        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"_class": "Name",
                "private": PrivacyBase.to_struct(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "date": DateBase.to_struct(self),
                "first_name": self.first_name,
                "surname_list": SurnameBase.to_struct(self),
                "suffix": self.suffix,
                "title": self.title,
                "type": self.type.to_struct(),
                "group_as": self.group_as,
                "sort_as": self.sort_as,
                "display_as": self.display_as,
                "call": self.call,
                "nick": self.nick,
                "famnick": self.famnick}

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        self = default = Name()
        data = (Date.from_struct(struct.get("date", {})),
                struct.get("first_name", default.first_name),
                struct.get("suffix", default.suffix),
                struct.get("title", default.title),
                NameType.from_struct(struct.get("type", {})),
                struct.get("group_as", default.group_as),
                struct.get("sort_as", default.sort_as),
                struct.get("display_as", default.display_as),
                struct.get("call", default.call),
                struct.get("nick", default.nick),
                struct.get("famnick", default.famnick))
        (self.date,
         self.first_name, self.suffix, self.title, self.type,
         self.group_as, self.sort_as, self.display_as, self.call,
         self.nick, self.famnick) = data
        PrivacyBase.set_from_struct(self, struct)
        SurnameBase.set_from_struct(self, struct)
        CitationBase.set_from_struct(self, struct)
        NoteBase.set_from_struct(self, struct)
        DateBase.set_from_struct(self, struct)
        return self

    @classmethod
    def get_labels(cls, _):
        return {
            "_class": _("Name"),
            "private": _("Private"),
            "citation_list": _("Citations"),
            "note_list": _("Notes"),
            "date": _("Date"),
            "first_name": _("Given name"),
            "surname_list": _("Surnames"),
            "suffix": _("Suffix"),
            "title": _("Title"),
            "type": _("Type"),
            "group_as": _("Group as"),
            "sort_as": _("Sort as"),
            "display_as": _("Display as"),
            "call": _("Call name"),
            "nick": _("Nick name"),
            "famnick": _("Family nick name"),
        }

    @classmethod
    def get_schema(cls):
        from .surname import Surname
        return {
            "private": bool,
            "citation_list": [Handle("Citation", "CITATION-HANDLE")],
            "note_list": [Handle("Note", "NOTE-HANDLE")],
            "date": Date,
            "first_name": str,
            "surname_list": [Surname],
            "suffix": str,
            "title": str,
            "type": NameType,
            "group_as": str,
            "sort_as": int,
            "display_as": int,
            "call": str,
            "nick": str,
            "famnick": str,
        }

    def is_empty(self):
        """
        Indicate if the name is empty.
        """
        namefieldsempty = (self.first_name == "" and
                           self.suffix == "" and
                           self.title == "" and
                           self.nick == "" and
                           self.famnick == "")
        surnamefieldsempty = False not in [surn.is_empty()
                                           for surn in self.surname_list]
        return namefieldsempty and surnamefieldsempty

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.first_name, self.suffix, self.title,
                str(self.type), self.call, self.nick, self.famnick]

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.surname_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may
                  refer notes.
        :rtype: list
        """
        return []

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return []

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return self.get_referenced_note_handles() + \
               self.get_referenced_citation_handles()

    def is_equivalent(self, other):
        """
        Return if this name is equivalent, that is agrees in type, first,
        call, surname_list, suffix, title and date, to other.

        :param other: The name to compare this name to.
        :type other: Name
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        # TODO what to do with sort and display?
        if self.get_text_data_list() != other.get_text_data_list() or \
            self.get_date_object() != other.get_date_object() or \
            SurnameBase.to_struct(self) != SurnameBase.to_struct(other):
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this name.
        Normally the person merge code should opt for adding an alternate
        name if names are actually different (like not equal surname list)

        Lost: type, first, call, suffix, title, nick, famnick and date of
        acquisition.

        :param acquisition: The name to merge with the present name.
        :type acquisition: Name
        """
        # TODO what to do with sort and display?
        self._merge_privacy(acquisition)
        self._merge_surname_list(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)

    def set_group_as(self, name):
        """
        Set the grouping name for a person.

        Normally, this is the person's surname. However, some locales group
        equivalent names (e.g. Ivanova and Ivanov in Russian are usually
        considered equivalent.

        .. note:: There is also a database wide grouping set_name_group_mapping
          So one might map a name Smith to SmithNew, and have one person still
          grouped with name Smith. Hence, group_as can be equal to surname!
        """
        self.group_as = name

    def get_group_as(self):
        """
        Return the grouping name, which is used to group equivalent surnames.
        """
        return self.group_as

    def get_group_name(self):
        """
        Return the grouping name, which is used to group equivalent surnames.
        """
        if self.group_as:
            return self.group_as
        else:
            return self.get_primary_surname().get_surname()

    def set_sort_as(self, value):
        """
        Specifies the sorting method for the specified name.

        Typically the locale's default should be used. However, there may be
        names where a specific sorting structure is desired for a name.
        """
        self.sort_as = value

    def get_sort_as(self):
        """
        Return the selected sorting method for the name.

        The options are LNFN (last name, first name), FNLN (first name, last
        name), etc.
        """
        return self.sort_as

    def set_display_as(self, value):
        """
        Specifies the display format for the specified name.

        Typically the locale's default should be used. However, there may be
        names where a specific display format is desired for a name.
        """
        self.display_as = value

    def get_display_as(self):
        """
        Return the selected display format for the name.

        The options are LNFN (last name, first name), FNLN (first name, last
        name), etc.
        """
        return self.display_as

    def get_call_name(self):
        """
        Return the call name.

        The call name's exact definition is not predetermined, and may be
        locale specific.
        """
        return self.call

    def set_call_name(self, val):
        """
        Set the call name.

        The call name's exact definition is not predetermined, and may be
        locale specific.
        """
        self.call = val

    def get_nick_name(self):
        """
        Return the nick name.

        The nick name of the person, a not official name the person is known
        with.
        """
        return self.nick

    def set_nick_name(self, val):
        """
        Set the nick name.

        The nick name of the person, a not official name the person is known
        with.
        """
        self.nick = val

    def get_family_nick_name(self):
        """
        Return the family nick name.

        The family nick name of the family of the person, a not official name
        use to denote the entire family.
        """
        return self.famnick

    def set_family_nick_name(self, val):
        """
        Set the family nick name.

        The family nick name of the family of the person, a not official name
        use to denote the entire family.
        """
        self.famnick = val

    def set_type(self, the_type):
        """Set the type of the Name instance."""
        self.type.set(the_type)

    def get_type(self):
        """Return the type of the Name instance."""
        return self.type

    def set_first_name(self, name):
        """Set the given name for the Name instance."""
        self.first_name = name

    def get_first_name(self):
        """Return the given name for the Name instance."""
        return self.first_name

    def set_suffix(self, name):
        """Set the suffix (such as Jr., III, etc.) for the Name instance."""
        self.suffix = name

    def get_suffix(self):
        """Return the suffix for the Name instance."""
        return self.suffix

    def set_title(self, title):
        """Set the title (Dr., Reverand, Captain) for the Name instance."""
        self.title = title

    def get_title(self):
        """Return the title for the Name instance."""
        return self.title

    def get_name(self):
        """
        Return a name string built from the components of the Name instance,
        in the form of: surname, Firstname.
        """
        first = self.first_name
        surname = self.get_surname()
        if self.suffix:
            # translators: needed for Arabic, ignore otherwise
            return _("%(surname)s, %(first)s %(suffix)s"
                    ) % {'surname':surname, 'first':first, 'suffix':self.suffix}
        else:
            # translators: needed for Arabic, ignore otherwise
            return _("%(str1)s, %(str2)s") % {'str1':surname, 'str2':first}

    def get_upper_name(self):
        """
        Return a name string built from the components of the Name instance,
        in the form of SURNAME, Firstname.
        """
        first = self.first_name
        surname = self.get_surname().upper()
        if self.suffix:
            # translators: needed for Arabic, ignore otherwise
            return _("%(surname)s, %(first)s %(suffix)s"
                    ) % {'surname':surname, 'first':first, 'suffix':self.suffix}
        else:
            # translators: needed for Arabic, ignore otherwise
            return _("%(str1)s, %(str2)s") % {'str1':surname, 'str2':first}

    def get_regular_name(self):
        """
        Return a name string built from the components of the Name instance,
        in the form of Firstname surname.
        """
        first = self.first_name
        surname = self.get_surname()
        if self.suffix == "":
            return "%s %s" % (first, surname)
        else:
            # translators: needed for Arabic, ignore otherwise
            return _("%(first)s %(surname)s, %(suffix)s"
                    ) % {'surname':surname, 'first':first, 'suffix':self.suffix}

    def get_gedcom_parts(self):
        """
        Returns a GEDCOM-formatted name dictionary.

        .. note:: Fields patronymic and prefix are deprecated, prefix_list and
                  surname list, added.
        """
        retval = {}
        retval['given'] = self.first_name.strip()
        retval['surname'] = self.get_surname().replace('/', '?')
        retval['suffix'] = self.suffix
        retval['title'] = self.title
        retval['surnamelist'] = self.get_surnames()
        retval['prefixes'] = self.get_prefixes()
        retval['connectors'] = self.get_connectors()
        retval['nick'] = self.nick
        retval['famnick'] = self.famnick
        return retval

    def get_gedcom_name(self):
        """
        Returns a GEDCOM-formatted name.
        """
        firstname = self.first_name.strip()
        surname = self.get_surname().replace('/', '?')
        suffix = self.suffix
        if suffix == "":
            return '%s /%s/' % (firstname, surname)
        else:
            return '%s /%s/ %s' % (firstname, surname, suffix)

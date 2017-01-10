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
Address class for Gramps.
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
from .locationbase import LocationBase
from .const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Address for Person/Repository
#
#-------------------------------------------------------------------------
class Address(SecondaryObject, PrivacyBase, CitationBase, NoteBase, DateBase,
              LocationBase):
    """Provide address information."""

    def __init__(self, source=None):
        """
        Create a new Address instance, copying from the source if provided.
        """
        PrivacyBase.__init__(self, source)
        CitationBase.__init__(self, source)
        NoteBase.__init__(self, source)
        DateBase.__init__(self, source)
        LocationBase.__init__(self, source)

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
        return {"_class": "Address",
                "private": PrivacyBase.to_struct(self),
                "citation_list": CitationBase.to_struct(self),
                "note_list": NoteBase.to_struct(self),
                "date": DateBase.to_struct(self),
                "street": self.street,
                "locality": self.locality,
                "city": self.city,
                "county": self.county,
                "state": self.state,
                "country": self.country,
                "postal": self.postal,
                "phone": self.phone,
               }

    @classmethod
    def get_schema(cls):
        from .date import Date
        from .handle import Handle
        from .location import Location
        return {
            "_class": "Address",
            "private": bool,
            "citation_list": [Handle("Citation", "CITATION-HANDLE")],
            "note_list": [Handle("Note", "CITATION-HANDLE")],
            "date": Date,
            "street": str,
            "locality": str,
            "city": str,
            "county": str,
            "state": str,
            "country": str,
            "postal": str,
            "phone": str,
        }

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        self = Address()
        PrivacyBase.set_from_struct(self, struct)
        CitationBase.set_from_struct(self, struct)
        NoteBase.set_from_struct(self, struct)
        DateBase.set_from_struct(self, struct)
        LocationBase.set_from_struct(self, struct)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return LocationBase.get_text_data_list(self)

    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return []

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
        Return if this address is equivalent, that is agrees in location and
        date, to other.

        :param other: The address to compare this one to.
        :type other: Address
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if self.get_text_data_list() != other.get_text_data_list() or \
            self.get_date_object() != other.get_date_object():
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this address.

        Lost: date, street, city, county, state, country, postal and phone of
        acquisition.

        :param acquisition: The address to merge with the present address.
        :type acquisition: Address
        """
        self._merge_privacy(acquisition)
        self._merge_note_list(acquisition)
        self._merge_citation_list(acquisition)

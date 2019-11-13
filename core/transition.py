#!/usr/bin/python
"""
Transition class
"""

import json

class Transition:
    """
    Class Transition
    """

    def __init__(self, one_state_from="", one_token="", one_state_to=""):
        """ Constructor """

        self.__state_from = one_state_from
        self.__token = one_token
        self.__state_to = one_state_to

    def get_state_from(self):
        """ Getter """
        return self.__state_from

    def set_state_from(self, one_string):
        """ Setter """
        self.__state_from = one_string

    def get_token(self):
        """ Getter """
        return self.__token

    def set_token(self, one_string):
        """ Setter """
        self.__token = one_string

    def get_state_to(self):
        """ Getter """
        return self.__state_to

    def set_state_to(self, one_string):
        """ Setter """
        self.__state_to = one_string

    def to_json(self):
        """ To JSON """
        _dict = {}
        _dict['state_from'] = self.__state_from
        _dict['token'] = self.__token
        _dict['state_to'] = self.__state_to
        return _dict

    def from_json(self, one_jsonx):
        """ From JSON """
        one_json = one_jsonx
        if isinstance(one_jsonx, str):
            one_json = json.loads(one_jsonx)

        if 'state_from' in one_json.keys():
            self.__state_from = one_json['state_from']

        if 'token' in one_json.keys():
            self.__token = one_json['token']

        if 'state_to' in one_json.keys():
            self.__state_to = one_json['state_to']

    def replace_name(self, callback):
        """
        Replace names on the states by one given callback
        the callback receive one state name and return the new name
        """
        new_trans = Transition()
        new_trans.set_state_to(callback(self.get_state_to()))
        new_trans.set_state_from(callback(self.get_state_from()))
        new_trans.set_token(self.get_token())
        return new_trans

    def sort_str(self):
        """ Sort Key """
        return "{0}{1}{2}".format(self.get_state_from(), \
                                  self.get_state_to(), \
                                  self.get_token())


    def copy(self):
        """ Copy object """
        def same_callback(str_value):
            return str_value
        return self.replace_name(same_callback)

    def equal_obj(self, other):
        """ Equal object """
        if self.get_state_from() == other.get_state_from() and \
           self.get_state_to() == other.get_state_to() and \
           self.get_token() == other.get_token():
            return True
        return False

    def equal(self, value1, value2, value3):
        """ Equal with value """
        new_trans = Transition(value1, value2, value3)
        return self.equal_obj(new_trans)

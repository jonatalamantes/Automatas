#!/usr/bin/python
# pylint: disable=W0640
""" File for Automata Class """

import json
from core.transition import Transition

class Automata:
    """ Class Automata """

    def __init__(self):
        """ Constructor """
        self.__alphabet = []
        self.__states = []
        self.__transitions = []
        self.__initial = ""
        self.__aceptation = []

    def init(self):
        """ Clean all the object """
        self.__alphabet = []
        self.__states = []
        self.__transitions = []
        self.__initial = ""
        self.__aceptation = []

    def get_alphabet(self):
        """ Getter """
        return self.__alphabet

    def set_alphabet(self, one_list):
        """ Setter """
        self.__alphabet = one_list

    def get_states(self):
        """ Getter """
        return self.__states

    def set_states(self, one_list):
        """ Setter """
        self.__states = one_list

    def get_transitions(self):
        """ Getter """
        return self.__transitions

    def set_transitions(self, one_list):
        """ Setter """
        self.__transitions = one_list

    def get_initial(self):
        """ Getter """
        return self.__initial

    def set_initial(self, one_string):
        """ Setter """
        self.__initial = one_string

    def get_aceptation(self):
        """ Getter """
        return self.__aceptation

    def set_aceptation(self, one_list):
        """ Setter """
        self.__aceptation = one_list

    def to_json(self):
        """ To JSON """
        _dict = {}
        _dict['alphabet'] = self.__alphabet
        _dict['states'] = self.__states
        _dict['transitions'] = list(map(lambda x: x.to_json(), self.__transitions))
        _dict['initial'] = self.__initial
        _dict['aceptation'] = self.__aceptation
        return _dict

    def to_file(self, filename):
        """ Create a File with the automata """
        with open(filename, "w") as filex:
            _json = self.to_json()
            json.dump(_json, filex, indent=4, sort_keys=True)

    def from_json(self, one_jsonx):
        """ From JSON """

        self.init()
        one_json = one_jsonx
        if isinstance(one_jsonx, str):
            one_json = json.loads(one_jsonx)

        if 'alphabet' in one_json.keys():
            self.__alphabet = one_json['alphabet']

        if 'states' in one_json.keys():
            self.__states = one_json['states']

        if 'transitions' in one_json.keys():
            transitions = one_json['transitions']
            for trans in transitions:
                new_trans = Transition()
                new_trans.from_json(trans)
                self.__transitions.append(new_trans)

        if 'initial' in one_json.keys():
            self.__initial = one_json['initial']

        if 'aceptation' in one_json.keys():
            self.__aceptation = one_json['aceptation']

    def from_filename(self, filename):
        """ Load one automata from file """
        with open(filename) as filex:
            _json = json.loads(filex.read())
            self.from_json(_json)

    def console_print(self):
        """ Print in console """
        print(json.dumps(self.to_json(), indent=4, sort_keys=True))

    def copy(self):
        """ Create one new automata from the original """
        auto = Automata()
        j = self.to_json()
        auto.from_json(j)
        return auto

    def build_alphabet(self):
        """ Build the alphabet of the automata reading the transitions """
        self.__alphabet = sorted(list(set(map(lambda x: x.get_token(), self.__transitions))))

    def build_states(self):
        """ Build the states of the automata reading the transitions """
        self.__states = []
        for trans in self.__transitions:
            self.__states.append(trans.get_state_from())
            self.__states.append(trans.get_state_to())
        self.__states = sorted(list(set(self.__states)))

    def uniform_names(self):
        """ Change the name of the nodes by standard names like q0, q1 """

        new_names = {}

        _counter = 0
        for state in self.__states:
            new_names[state] = "q{0}".format(_counter)
            _counter += 1

        def str_replace(one_str):
            return new_names[one_str]

        self.do_name_mapping(str_replace)

    def clean(self):
        """ Remove commas, dots and empty names in the states """

        def str_replace(one_str):
            new_str = one_str
            if new_str == "":
                new_str = "empty"
            else:
                new_str = new_str.replace(",", "_")
                new_str = new_str.replace(".", "_")
            return new_str

        self.do_name_mapping(str_replace)

    def fetch_transition(self, state_from=None, token=None, state_to=None):
        """ Fetch a list of transitions passing the state_from, token or state_to """

        transitions = []
        for transition in self.__transitions:

            found = 0
            if state_from is None or transition.get_state_from() == state_from:
                found += 1

            if token is None or transition.get_token() == token:
                found += 1

            if state_to is None or transition.get_state_to() == state_to:
                found += 1

            if found == 3:
                transitions.append(transition)

        return transitions

    def do_name_mapping(self, callback):
        """
        Change the name of the states by one given callback
        The callback receive the old name of the state and return the new name
        """

        self.__states = list(map(callback, self.__states))
        self.__initial = callback(self.__initial)
        self.__aceptation = list(map(callback, self.__aceptation))
        self.__transitions = list(map(lambda x: x.replace_name(callback), self.__transitions))

    def is_deterministic(self):
        """ Return if the automata is deterministic """
        return self.get_next_incomplete() is None

    def get_next_incomplete(self):
        """ Get the first state that invalidate the deterministic property """

        # iterate over all the states to find the token of every state
        for state in self.__states:
            tokens = []

            for trans in self.fetch_transition(state_from=state):

                # if there is one more state with the same begin and token is NFA
                if trans.get_token() in tokens:
                    return state

                tokens.append(trans.get_token())

            # in case one missing token of the alphabet is NFA
            if set(tokens) != set(filter(lambda x: x != "", self.__alphabet)):
                return state

        return None

    def epsilon_cerradure(self, one_state, cerradure=None):
        """ Calculate the cerradure epsilon from one state """

        new_cerradure = []

        # calculate cerradure epsilon first time
        if cerradure is None or one_state not in cerradure:

            # base case: ce(x) += [x]
            new_cerradure.append(one_state)

            # recursive case: ce(x) += ce(eval(x, ""))
            for trans in self.fetch_transition(one_state, ""):
                if trans.get_state_to() not in new_cerradure:
                    new_cerradure += self.epsilon_cerradure(trans.get_state_to(), new_cerradure)

        #return final  cerradure
        return new_cerradure

    def extend_states(self):
        """ Remove the epsilon transitions and create new transitions """

        def mini_add(new_transitions, state, token, ext):
            nt1 = Transition(state, token, ext)

            add = True
            for nt2 in new_transitions:
                if nt1.equal_obj(nt2):
                    add = False
                    break

            if add:
                new_transitions.append(nt1)

        new_transitions = []

        # calculate all epsilon cerradure
        epsilon = {}
        for state in self.__states:
            epsilon[state] = self.epsilon_cerradure(state)

        # ce(state) -> eval(ce, token) -> new(from, token, ce(to))
        for state, cerradure in epsilon.items():

            for token in self.__alphabet:

                # skip epsilon transitions
                if token == "":
                    continue

                posible_add = []

                # eval(ce, token)
                for ce_state in cerradure:
                    for trans in self.fetch_transition(ce_state, token):
                        posible_add.append(trans.get_state_to())

                # new(from, token, ce(to))
                for posible_state in posible_add:

                    future = epsilon[posible_state]

                    for ext in future:
                        mini_add(new_transitions, state, token, ext)

        # Remove empty string from alphabeth
        if "" in self.__alphabet:
            self.__alphabet.remove("")

        # update of transitions
        self.__transitions = new_transitions
        self.clean()


    def to_deterministic(self):
        """ Return the deterministic automata without change the actual one """

        def calculate_goes(copy_self, current_state):
            goes_to = {}
            for goes in current_state.split(","):
                for token in copy_self.get_alphabet():

                    if token not in goes_to:
                        goes_to[token] = []

                    for trans in copy_self.fetch_transition(goes, token):
                        goes_to[token].append(trans.get_state_to())

                    if goes_to[token] == []:
                        goes_to[token].append("empty")
            return goes_to

        if self.is_deterministic():
            return self.copy()

        copy_self = self.copy()
        copy_self.extend_states()

        new_automata = Automata()
        new_automata.set_alphabet(list(self.__alphabet))
        new_automata.set_initial(self.__initial)
        new_automata.set_states([self.__initial])
        new_automata.set_transitions([])

        start = True
        while not new_automata.is_deterministic() or start:

            current_state = new_automata.get_next_incomplete()
            start = False

            # Get the states tha goes from the actual node
            goes_to = calculate_goes(copy_self, current_state)

            # Create the transitions
            for token, goesx in goes_to.items():

                goes = set(goesx)
                goes = list(goes)
                goes.sort()

                if goes != ["empty"]:
                    goes = list(filter(lambda x: x != "empty", goes))

                uid = ",".join(goes)
                if uid not in new_automata.get_states():
                    new_automata.get_states().append(uid)

                if not new_automata.fetch_transition(current_state, token, uid):
                    new_t = Transition(current_state, token, uid)
                    new_automata.get_transitions().append(new_t)

        # Mark aceptations states
        for state in new_automata.get_states():
            for aceptation in copy_self.get_aceptation():
                if aceptation in state.split(",") and \
                   aceptation not in new_automata.get_aceptation():
                    new_automata.get_aceptation().append(state)

        # Return the clean automata
        new_automata.clean()
        return new_automata

    def minimizete(self):
        """
        Minimizate the automata without change the original
        The minimization is done by creating pairs of states and calculate its compatibility
        """

        if not self.is_deterministic():
            raise ValueError("Automata must to be deterministic")

        def build_pairs():

            pairs = {}
            for left in self.get_states():
                for right in self.get_states():
                    pair = [left, right]
                    key = ",".join(pair)
                    compatible = list(map(lambda x: str(x in self.get_aceptation()), pair))
                    pairs[key] = compatible.count("True") != 1

            return pairs

        def iterate_incompatibles(original_pairs):

            # Iterate until get only find all the incompatibles
            no_compatibles = 1
            pairs = dict(original_pairs)
            while no_compatibles != 0:
                no_compatibles = 0
                for pair, compatible in dict(pairs).items():

                    # Find only still comparibles pairs
                    if compatible:
                        for token in self.__alphabet:

                            eval_left = self.fetch_transition(pair.split(",")[0], token)
                            eval_left = eval_left[0].get_state_to()
                            eval_right = self.fetch_transition(pair.split(",")[1], token)
                            eval_right = eval_right[0].get_state_to()

                            eval_key = ",".join([eval_left, eval_right])

                            # Transition no compartible
                            if not original_pairs[eval_key]:
                                pairs[pair] = False
                                no_compatibles += 1

            # Dilter only valid pairs
            pairs = sorted(list(filter(lambda x: pairs[x], pairs.keys())))
            pairs = sorted(list(set(map(lambda x: ",".join(sorted(x.split(","))), pairs))))

            return pairs

        def create_new_state_pairs(pairs):

            # Join into one only state the same pairs
            new_states = []
            for pair_str in pairs:
                pair = pair_str.split(",")
                add = False
                for state in new_states:
                    if pair[0] in state or pair[1] in state:
                        state.append(pair[0])
                        state.append(pair[1])
                        add = True
                if not add:
                    new_states.append(pair)

            new_states = sorted(list(map(lambda x: ",".join(list(set(x))), new_states)))

            return new_states

        def create_automata(new_states):

            # Build new automata
            initial = list(filter(lambda x: self.get_initial() in x.split(","), new_states))[0]

            new_automata = Automata()
            new_automata.set_initial(initial)

            # Mark acepation states
            for aceptation in self.get_aceptation():
                acept = list(filter(lambda x: aceptation in x.split(","), new_states))[0]
                if acept not in new_automata.get_aceptation():
                    new_automata.get_aceptation().append(acept)

            # Create the transitions
            for new_state in new_states:
                for token in self.get_alphabet():
                    zero_state = new_state.split(",")[0]
                    zero_to = self.fetch_transition(zero_state, token)[0].get_state_to()
                    zero_to = list(filter(lambda x: zero_to in x.split(","), new_states))[0]

                    # add new transition
                    if not new_automata.fetch_transition(new_state, token, zero_to):
                        new_trans = Transition(new_state, token, zero_to)
                        new_automata.get_transitions().append(new_trans)

            # Build missing elements
            new_automata.build_alphabet()
            new_automata.build_states()
            new_automata.clean()
            return new_automata

        pairs = build_pairs()
        pairs = iterate_incompatibles(pairs)
        new_states = create_new_state_pairs(pairs)
        return create_automata(new_states)

    def evaluate(self, one_string, one_callback=None):
        """
        Test the automata with one_string, return if the one_string is valid
        Receive one callback to visualizate the evaluation
        The callback receive (old_state, token, new_states)
        """

        # create one initial state with the begin of the automata
        actual = [self.__initial]

        # read the string
        for token in one_string:

            # create follow iteration actual nodes by the evaluation
            new_actual = []

            # Add the epsilon transitions as well
            for statex in actual:
                fetch = self.fetch_transition(statex, "")
                for fec in fetch:
                    if fec.get_state_to() not in actual:
                        actual.append(fec.get_state_to())
            actual = sorted(list(set(actual)))

            # get the transitions of the current nodes and match with the actual token
            for current_state in actual:
                for trans in self.fetch_transition(current_state, token):
                    new_actual.append(trans.get_state_to())
            new_actual = sorted(list(set(new_actual)))

            # callback to debug evaluation
            if one_callback is not None:
                one_callback(actual, token, new_actual)

            # update of new step
            actual = new_actual

        # check if the latest step correspond to one aceptation state
        for current_state in actual:
            if current_state in self.__aceptation:
                return True

        return False

    def kleen_star(self):
        """ Return one autoamta with the Kleen star of original """

        self_copy = self.copy()
        old_initial = self_copy.get_initial()

        #Add transation from aceptation to initial
        for aceptation in self.__aceptation:
            self_copy.get_transitions().append(Transition(aceptation, "", "i"))

        #Add new initial state
        self_copy.set_initial("i")
        self_copy.get_transitions().append(Transition("i", "", old_initial))
        self_copy.get_aceptation().append("i")

        self_copy.clean()
        return self_copy

    @staticmethod
    def concatenation(automata1, automata2):
        """ Return one automata that is the concatenation of two automatas """

        def remap1(one_state_name):
            return "{0}_1".format(one_state_name)

        def remap2(one_state_name):
            return "{0}_2".format(one_state_name)

        copy1 = automata1.copy()
        copy2 = automata2.copy()

        copy1.do_name_mapping(remap1)
        copy2.do_name_mapping(remap2)

        #Create new automata
        new_automata = Automata()
        new_automata.set_initial(copy1.get_initial())
        new_automata.set_aceptation(copy2.get_aceptation())
        new_automata.set_transitions(copy1.get_transitions() + copy2.get_transitions())

        for old_aceptation in copy1.get_aceptation():
            link = Transition(old_aceptation, "", copy2.get_initial())
            new_automata.get_transitions().append(link)

        new_automata.build_alphabet()
        new_automata.build_states()

        new_automata.clean()
        return new_automata

    @staticmethod
    def merge_automata(automata1, automata2, merge_type):
        """
        Return one automata that is the merge of two automatas
        The merge type must to be union or intersection
        """

        if merge_type not in ["union", "intersection"]:
            raise ValueError("merge_type parameter must to be [union, intersection]")

        deter1 = automata1.to_deterministic()
        deter2 = automata2.to_deterministic()

        new_automata = Automata()
        new_automata.set_alphabet(list(set(automata1.get_alphabet()+automata2.get_alphabet())))
        new_automata.set_initial(",".join([automata1.get_initial(), automata2.get_initial()]))
        new_automata.set_states([new_automata.get_initial()])
        new_automata.set_transitions([])

        # Evaluate every path of the automata
        while not new_automata.is_deterministic():

            incomplete = new_automata.get_next_incomplete()
            incomplete_split = incomplete.split(",")

            for token in new_automata.get_alphabet():

                goes_one = deter1.fetch_transition(incomplete_split[0], token)
                goes_two = deter2.fetch_transition(incomplete_split[1], token)

                goes_one = list(map(lambda x: x.get_state_to(), goes_one))
                goes_two = list(map(lambda x: x.get_state_to(), goes_two))

                goes = ",".join(goes_one + goes_two)

                if goes not in new_automata.get_states():
                    new_automata.get_states().append(goes)

                if not new_automata.fetch_transition(incomplete, token, goes):
                    trans = Transition(incomplete, token, goes)
                    new_automata.get_transitions().append(trans)

        # Calculate aceptation states
        for state in new_automata.get_states():

            if merge_type == "union":
                if state.split(",")[0] in deter1.get_aceptation() or \
                   state.split(",")[1] in deter2.get_aceptation():
                    new_automata.get_aceptation().append(state)

            elif merge_type == "intersection":
                if state.split(",")[0] in deter1.get_aceptation() and \
                   state.split(",")[1] in deter2.get_aceptation():
                    new_automata.get_aceptation().append(state)

        new_automata.build_alphabet()
        new_automata.build_states()

        new_automata.clean()
        return new_automata

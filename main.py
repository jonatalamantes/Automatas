#!/usr/bin/python
"""
Main script
"""

import os

from core.automata import Automata
from core.automata import Transition

def xinput(string):
    """
    Python 2/3 input compatibility
    """
    try:
        return raw_input(string)
    except NameError:
        return input(string)

class App:
    """
    App Class
    """

    def __init__(self):
        self.__auto = Automata()
        self.__loaded = False

    @staticmethod
    def print_actual(old, token, new):
        """
        Internal callback to print the evaluation
        """
        print("eval('{0}','{1}') = {2}".format(old, token, new))

    @staticmethod
    def load_automata():
        """
        Load from filename the automata
        """
        ready = sorted(os.listdir("data"))
        ready = list(map(lambda x: x.replace(".json", ""), ready))

        _file = xinput("Select one file {0}: ".format(ready))

        if _file not in ready:
            print("'{0}' is a invalid automata".format(_file))
            return None

        _file = "data/{0}.json".format(_file)
        auto = Automata()
        auto.from_filename(os.path.abspath(_file))
        return auto

    @staticmethod
    def create_automata():
        """
        Create new automata with user input
        """

        opt = None
        new_automata = Automata()

        while opt != "":
            msg = "Insert transition 'state_from,token,state_to' or Enter to continue: "
            opt = xinput(msg).replace(" ", "")
            trans = opt.split(",")

            if opt != "":
                try:
                    new_trans = Transition(trans[0], trans[1], trans[2])
                    new_automata.get_transitions().append(new_trans)
                except IndexError:
                    print("Invalid format on transition")

        initial = xinput("Insert the initial state: ")
        new_automata.set_initial(initial)

        aceptation = xinput("Insert aceptation state dived by comas 's0,s1,s3': ")
        new_automata.set_aceptation(aceptation.split(","))

        new_automata.build_alphabet()
        new_automata.build_states()

        return new_automata

    def menu(self):
        """
        Print the option menu and return the desire option
        """

        print("")
        print("*** Create Tasks ***")
        print("C) Create Automata")
        print("L) Load Automata")
        print("X) Load from Regular Expresion")
        if self.__loaded:
            print("S) Save Automata")
        print("")

        if self.__loaded:
            print("*** Single Automata Tasks ***")
            print("A) Evaluate String")
            print("T) Transform To Determinisitic")
            print("M) Minimizate")
            print("N) Uniform Names")
            print("R) Regular Expresion")
            print("P) Print Automata")
            print("*) Kleen Star")
            print("")

        print("*** Multi-Automata Tasks ***")
        print("U) Union Automatas")
        print("I) Intersection Automatas")
        print("Y) Concatenation Automatas")
        print("E) Two Regular Expresion Equivalence")
        print("")
        print("q) Exit")
        print("")
        return xinput("Option:  ").replace(" ", "")

    def do_fs_tasks(self, option):
        """
        Do FileSystem Tasks
        """

        if option == "L":
            print("Load")
            temp = App.load_automata()
            if temp is not None:
                self.__auto = temp
                self.__auto.console_print()
                self.__loaded = True

        if option == "S" and self.__loaded:
            print("Save")
            _file = xinput("Insert the name of the automata: ")
            _file = os.path.abspath("data/{0}.json".format(_file))
            self.__auto.to_file(_file)
            print("Saved on: {0}".format(_file))

        if option == "C":
            print("Create")
            self.__auto = App.create_automata()
            self.__auto.console_print()
            self.__loaded = True

        if option == "X":
            print("Create from Regex")
            regex = xinput("Insert the regex: ")
            self.__auto = Automata.read_expresion(regex)
            self.__auto.console_print()
            self.__loaded = True

    def multi_tasks(self, option):
        """
        Do operation that requieres two automatas
        """

        if option == "E":

            print("Equivalence")

            one = xinput("Insert the first regular expresion:  ")
            two = xinput("Insert the second regular expresion: ")

            auto1 = Automata.read_expresion(one)
            auto2 = Automata.read_expresion(two)

            try:
                auto3 = Automata.merge_automata(auto1, auto2, "equiv")
                print("\n*** Regular Expresions ARE equivalent ***\n")
            except ValueError as error:
                print("\n*** Regular Expresions are NOT equivalent ***")
                print(str(error) + '\n')

        if option in ["I", "U", "Y"]:

            print("Combinate")

            one = App.load_automata()
            two = App.load_automata()
            if one is not None and two is not None:

                if option in ["I", "U"]:

                    m_type = "intersection"
                    if option == "U":
                        m_type = "union"

                    try:
                        self.__auto = Automata.merge_automata(one, two, m_type)
                        self.__auto.console_print()
                        self.__loaded = True
                    except ValueError as error:
                        print(error)

                elif option in ["Y"]:
                    self.__auto = Automata.concatenation(one, two)
                    self.__auto.console_print()
                    self.__loaded = True


    def single_tasks(self, option):
        """
        Do operation that requires only one automata
        """

        if option == "A" and self.__loaded:
            string = xinput("String to Evaluate:  ")
            print("Evaluate '{0}'".format(string))
            print(self.__auto.evaluate(string, App.print_actual))

        if option == "T" and self.__loaded:
            print("Original automata is deterministic?")
            print(self.__auto.is_deterministic())
            print("\nGenerate Deterministic")
            self.__auto = self.__auto.to_deterministic()
            self.__auto.console_print()

        if option == "R" and self.__loaded:
            copy_self = self.__auto.copy()
            exp = copy_self.generate_expresion()
            print("\nRegular Expresion: {0}\n".format(exp))

        if option == "M" and self.__loaded:
            print("Minimizate")
            try:
                self.__auto = self.__auto.minimizete()
                self.__auto.console_print()
            except ValueError as error:
                print(error)

        if option == "N" and self.__loaded:
            print("Uniform names")
            self.__auto.uniform_names()
            self.__auto.console_print()

        if option == "P" and self.__loaded:
            print("Print")
            self.__auto.console_print()

        if option == "*" and self.__loaded:
            print("Kleen Star")
            self.__auto = self.__auto.kleen_star()
            self.__auto.console_print()

    def main_loop(self):
        """
        Main function
        """

        option = ""
        while option != "q":

            option = self.menu()

            self.single_tasks(option)
            self.multi_tasks(option)
            self.do_fs_tasks(option)

            xinput("Press Enter to Continue... ")

if __name__ == "__main__":
    try:
        print("Welcome!")
        APP = App()
        APP.main_loop()
    except KeyboardInterrupt:
        print("")
        print("Bye")

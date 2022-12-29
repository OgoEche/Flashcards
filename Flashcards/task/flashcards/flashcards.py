# Write your code here
from random import randint
import os.path
import logging
from io import StringIO
import argparse


class FlashCards:

    def __init__(self):
        self.cards = []
        self.action_function = {'add': self.add,
                                'remove': self.remove,
                                'import': self.import_cards,
                                'export': self.export_cards,
                                'ask': self.ask,
                                'exit': self.exit_process,
                                'log': self.log,
                                'hardest card': self.hardest_card,
                                'reset stats': self.reset_stats}
        self.app_log_stream = StringIO()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--import_from')
        self.parser.add_argument('--export_to')

    def print_log_app_activity(self, activity):
        print(activity)
        self.app_log_stream.write(f'{activity}\n')

    def input_log_app_activity(self, activity):
        self.app_log_stream.write(f'{activity}\n')
        response = input(activity)
        self.app_log_stream.write(f'{response}\n')
        return response

    def is_term_or_definition(self, item):
        for term_defn in self.cards:
            if item in term_defn.values():
                return True
        return False

    def add(self):
        term_value = self.input_log_app_activity(f'The card:\n')
        if self.is_term_or_definition(term_value):
            term_value = self.try_again(term_value, 'term')

        defn_value = self.input_log_app_activity(f'The definition of the card:\n')
        if self.is_term_or_definition(defn_value):
            defn_value = self.try_again(defn_value, 'definition')

        self.cards.append({'term': term_value, 'definition': defn_value, 'mistakes': 0})
        self.print_log_app_activity(f'The pair ("{term_value}":"{defn_value}") has been added.\n')

    def get_command_line_args(self, type_str):
        args = self.parser.parse_args()
        if type_str == 'import':
            return args.import_from
        if type_str == 'export':
            return args.export_to

    def remove(self):
        card = self.input_log_app_activity(f'Which card?\n')
        for kv in self.cards:
            if card == kv['term']:
                self.cards.remove(kv)
                self.print_log_app_activity(f'The {card} has been removed.')
                return
        self.print_log_app_activity(f"""Can't remove "{card}": there is no such card.""")

    def import_cards(self, cmdLine=False):
        file_name = self.get_command_line_args('import') if cmdLine else self.input_log_app_activity('File name:\n')
        if not os.path.isfile(file_name):
            self.print_log_app_activity("File not found.")
            return

        from_file = []
        with open(file_name, 'r') as file:
            for kv in file:
                from_file.append(eval(kv))

        self.print_log_app_activity(f"{len(from_file)} cards have been loaded.")
        for item in from_file:
            if value := [(i, v) for i, v in enumerate(self.cards) if item['term'] == v['term']]:
                idx, _ = value[0]
                self.cards[idx] = item
            else:
                self.cards.append(item)

    def export_cards(self, cmdLine=False):
        file_name = self.get_command_line_args('export') if cmdLine else self.input_log_app_activity('File name:\n')
        with open(file_name, 'w') as file:
            for item in self.cards:
                file.write(str(item) + '\n')
        self.print_log_app_activity(f"{len(self.cards)} cards have been saved.")

    def ask(self):
        number_of_times = int(self.input_log_app_activity("How many times to ask?\n"))

        for idx in range(number_of_times):
            random_card = self.cards[randint(0, len(self.cards) - 1)]
            defn_answer = self.input_log_app_activity(f'print the definition of {random_card["term"]}:\n')
            if defn_answer == random_card['definition']:
                self.print_log_app_activity('Correct!')
            else:
                ans = self.query(defn_answer)
                part_string = f', but your definition is correct for "{ans}".' if ans else '.'
                self.print_log_app_activity(f'Wrong. The right answer is "{random_card["definition"]}"{part_string}')
                self.update_mistakes(random_card)

    def exit_process(self):
        if self.get_command_line_args('export'):
            self.export_cards(cmdLine=True)
        self.print_log_app_activity('Bye bye!')
        self.app_log_stream.close()
        exit(0)

    def query(self, answer):
        for kv in self.cards:
            if answer == kv['definition']:
                return kv['term']

    def update_mistakes(self, card):
        if card in self.cards:
            card['mistakes'] = card.get('mistakes') + 1

    def try_again(self, value, input_type):
        while True:
            value = self.input_log_app_activity(f'The {input_type} "{value}" already exists. Try again:\n')
            if not self.is_term_or_definition(value):
                return value

    def log(self):
        log_file_name = self.input_log_app_activity('File name: ')
        with open(log_file_name, 'w') as file:
            file.write(self.app_log_stream.getvalue())
        self.print_log_app_activity('The log has been saved')

    def hardest_card(self):
        if self.cards and (max_value := max(item['mistakes'] for item in self.cards)):
            max_mistakes = [item for item in self.cards if item['mistakes'] == max_value]
            marker = '"{}", '
            size = len(max_mistakes)
            term_string = (size * marker).format(*[item['term'] for item in max_mistakes]).rstrip(', ')
            clause = ' is' if size < 2 else 's are'
            message = 'The hardest card{} {}. You have {} errors answering it'.format(clause, term_string, max_value)
            self.print_log_app_activity(message)
        else:
            self.print_log_app_activity('There are no cards with errors.')

    def reset_stats(self):
        for item in self.cards:
            item['mistakes'] = 0
        self.print_log_app_activity('Card statistics have been reset.')

    def main_processing(self):

        if self.get_command_line_args('import'):
            self.import_cards(cmdLine=True)
        if self.get_command_line_args('export'):
            self.export_cards(cmdLine=True)

        while True:
            action = self.input_log_app_activity('Input the action (add, remove, import, export, ask, exit, log,'
                                              ' hardest card, reset stats):\n')

            if action in self.action_function.keys():
                self.action_function[action]()


if __name__ == '__main__':
    FlashCards().main_processing()

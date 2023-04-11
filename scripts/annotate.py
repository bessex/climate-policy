import json
import keyboard
import os


def begin_json_dict_in_file(file_path: str) -> bool:
    if os.path.exists(file_path):
        with open(file_path, 'r+') as f:
            if (start := f.read(1)) == '{':
                print("file_path non-empty.")
            elif start:
                print("file_path non-empty, but doesn't start with '{'. Stopping.")
                return False
            else:
                print("file_path empty. Will overwrite")
                f.write('{\n')

        with open(file_path, 'rb+') as f:
            f.seek(-2, os.SEEK_END)
            final = str(f.read(1), 'utf-8')
            f.seek(-1, os.SEEK_CUR)
            if final == '}':
                print("file_path ends with '}'. Removing.")
                f.truncate()
                f.write(bytes(',\n', 'utf-8'))
            elif final == ',' or final == '{':
                print("file_path ends with " + final + ". Will append to end.")
            else:
                print("file_path doesn't end with ',' or '}'. Check that it's valid"
                      " JSON and that the file ends with newline. Stopping.")
                return False
    else:
        with open(file_path, 'w') as f:
            print("file_path doesn't exist. Will create.")
            f.write('{\n')

    return True


def end_json_dict_in_file(file_path: str):
    with open(file_path, 'rb+') as f:
        # Remove trailing comma if present
        f.seek(-2, os.SEEK_END)
        if str(f.read(1), 'utf-8') == ',':
            print("Removing trailing comma.")
            f.seek(-1, os.SEEK_CUR)
            f.truncate()
            f.write(bytes('\n}\n', 'utf-8'))


def main():
    gold_file = '../models/gold_emma.json'
    gold = {}

    # load training data
    with open('../models/training_new_emma.json', 'r') as f:
        training = json.load(f)

    for instance_id, window in training:
        # remove extra whitespace (e.g. newlines in the middle)
        print_window = ' '.join(window.split())

        # add newline every 98 chars
        for i in range(98, len(print_window), 98):
            print_window = print_window[:i] + '\n' + print_window[i:]

        # print instance and request input
        print('------------------------------------------------------------')
        print(print_window)
        print('------------------------------------------------------------')
        # print number completed/left
        print(f'{len(gold)}/{len(training)}')
        print('| -: negative | 0: neutral | +: positive | q: quit |')
        print('------------------------------------------------------------') \
            # get input
        key = input()
        # user can press a key to classify the instance
        # ('-' for negative, '+' for positive, '0' for neutral)

        instance = {
            'window': window,
            'polarity': None
        }

        key = key.lower()
        if key == '-':
            instance['polarity'] = 'negative'
        elif key == '0':
            instance['polarity'] = 'neutral'
        elif key == '+':
            instance['polarity'] = 'positive'
        elif key == 'q':
            # quit
            break
        else:
            # value error
            print('Invalid input. Try again.')
            raise ValueError

        gold[instance_id] = instance

    # each instance is saved (continuously, during classification) to a new json file
    # so that the user can quit at any time and not lose progress
    with open(gold_file, 'w') as f:
        f.write(json.dumps(gold))


if __name__ == '__main__':
    main()

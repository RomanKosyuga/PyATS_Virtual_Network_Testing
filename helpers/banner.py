"""helper functions"""
import random
from string import ascii_lowercase


def get_banner():
    """generate random banner"""
    char_list = random.sample(ascii_lowercase, 16)
    return ''.join(char_list)


if __name__ == '__main__':
    # debug
    print(get_banner())

def notify(content):
    # ANSI escape code for green bold text
    green_bold = "\033[1;32m"
    reset = "\033[0m"

    # Print green bold text
    print()
    print(f"{green_bold}-----------{content}-----------{reset}")

import random
def random_string():
    return f'jet_{random.randint(0,500)}_{random.randint(0,500)}_{random.randint(0,500)}'
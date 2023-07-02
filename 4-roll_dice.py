import re
import subprocess

class random:
    """
    Re-implementation of the random number generator using the hash as seed.
    """

    # get the current hash
    show = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)
    # convert hash to integer seed.
    # seed should be global
    base_seed = int(show.stdout.decode().strip(), 16)
    shiftseed = base_seed

    def __init__(self):
        pass

    def randint(self, die):
        """
        Parameters: die (int) maximum number of generation
        Returns:    int: number from 0 to die non-inclusive.
        Example:    randint(6) := 3
        """
        # If there are less bits left in the shiftseed than requested,
        # re-add the base_seed for more.
        if random.shiftseed < die:
            random.shiftseed += random.base_seed

        # Get bottom bits
        ret = random.shiftseed % die

        # Remove used bits.
        random.shiftseed //= die
        return ret

    def randchoice(self, li):
        """
        Parameters: li (list) a list of items to chose from.
        Returns:    a single object from li
        Example:    randchoice([1, 2, 3]) := 2
        """
        return li[self.randint(len(li))]

randint = random().randint
randchoice = random().randchoice

def replace_die(match):
    """
    Replaces a placeholder with a random percentage.
    Parameters: match (RegEx match)
    Returns:    str: ...
    Example:    replace_percent('') := '[75%]'

    Required NdN: Number and quantity of dice to roll
    rhN: Reroll highest N dice. (Ex. paralyzed)
    rlN: Reroll lowest N dice. (Ex. overcharged if cyborg/robot)
    dhN: drop highest N dice. (Ex. strong poison)
    dlN: drop lowest N dice. (Ex. weak poison)
    +N or -N: Constant offset
    """
    # Parse
    count = int(match.group(1))
    roll = int(match.group(2))

    reroll_highest = min(int(match.group(3) or "0"), count)
    reroll_lowest  = min(int(match.group(4) or "0"), count)
    drop_highest   = int(match.group(5) or "0")
    drop_lowest    = int(match.group(6) or "0")

    addsub = match.group(7)
    if addsub:
        constant = int(addsub + match.group(8))
    else:
        constant = 0

    # Top and bottom
    # Overlapping, edge-cases, and over-length numbers are safe.
    top    = count - drop_highest
    bottom = drop_lowest

    # Initial roll list
    total = 0
    rolls = [randint(roll)+1 for _ in range(count)]
    rolls.sort()

    for i in range(reroll_lowest):  rolls[i] = randint(roll)+1
    rolls.reverse()
    for i in range(reroll_highest): rolls[i] = randint(roll)+1
    rolls.sort()
    rolls = rolls[bottom:top]

    total = sum(rolls) + constant

    appstr =  f"[{count}d{roll}"
    if reroll_highest: appstr += f"rh{reroll_highest}"
    if reroll_lowest:  appstr += f"rl{reroll_lowest}"
    if drop_highest:   appstr += f"dh{drop_highest}"
    if drop_lowest:    appstr += f"dl{drop_lowest}"
    if addsub:         appstr += f"{constant:+}"
    appstr += f" = ({'+'.join(str(i) for i in rolls)}"
    if addsub:         appstr += f"{constant:+}"
    appstr += f") = {total}]"

    return appstr

def replace_percent(x):
    """
    Replaces a placeholder with a random percentage 0-100 inclusive.
    Parameters: _ (any): This parameter is ignored.
    Returns:    str: A string containing a random percentage enclosed in square brackets.
    Example:    replace_percent('percent') := '[75%]'
    """
    return f"[{randint(101)}%]"

def replace_general_body(x):
    """
    Replaces a placeholder with a random body part.
    Parameters: _ (any): This parameter is ignored.
    Returns:    str: A string containing a random body part enclosed in square brackets.
    Example:    replace_general_body('general body') := '[general_body=Torso]'
    """
    li = ["Head", "Left arm", "Right arm", "Torso", "Left leg", "Right leg"]
    return f"[general_body={randchoice(li)}]"

def replace_specific_body(x):
    """
    Replaces a placeholder with a random body part.
    Parameters: _ (any): This parameter is ignored.
    Returns:    str: A string containing a random body part enclosed in square brackets.
    Example:    replace_specific_body('specific body') := '[specific_body=Nose]'
    """
    li = [
        "Left Ear",         "Right Ear",         "Left Eye",          "Right Eye",          "Nose",             "Mouth",
        "Left Shoulder",    "Left Upper Arm",    "Left Elbow",        "Left Forearm",       "Left Wrist",       "Left Hand",
        "Right Shoulder",   "Right Upper Arm",   "Right Elbow",       "Right Forearm",      "Right Wrist",      "Right Hand",
        "Left Upper Torso", "Right Upper Torso", "Left Middle Torso", "Right Middle Torso", "Left Lower Torso", "Right Lower Torso",
        "Left Hip",         "Left Thigh",        "Left Knee",         "Left Calf",          "Left Ankle",       "Left Foot",
        "Right Hip",        "Right Thigh",       "Right Knee",        "Right Shin",         "Right Ankle",      "Right Foot"
    ]
    return f"[specific_body={randchoice(li)}]"

def replace_code_eval(py_code):
    """
    Replaces 'py_code' with it's evaulation or error.
    Parameters: py_code (str): This parameter is ignored.
    Returns:    str: The evaution of py_code, or it's error
    Example:    replace_code_eval('{py: 2*3}') := '[py: 2*3 = 6]'
    """
    try:
        return f"[py:{py_code.group(1)} = {eval(py_code.group(1))}]"
    except Exception as e:
        return f"[py:{py_code.group(1)} = {e}]"

def convert(content):
    contentv = re.sub(r'{(\d+)d(\d+)(?:rh(\d+))?(?:rl(\d+))?(?:dh(\d+))?(?:dl(\d+))?(?:\w*(\+|-)\w*(\d+))?}', replace_die, content)
    contentv = re.sub(r'{percent}', replace_percent, contentv)
    contentv = re.sub(r'{general body}', replace_general_body, contentv)
    contentv = re.sub(r'{specific body}', replace_specific_body, contentv)
    contentv = re.sub(r'{py: ?(.+?)}', replace_code_eval, contentv)
    return contentv

c="""roll: {6d6}
roll: {6d8}
roll: {6d6rh2}
roll: {6d6rl2}
roll: {6d6dh2}
roll: {6d6dl2}
roll: {6d6dh1dl1}
roll: {6d6+2}
roll: {6d6-2}
{percent}
{general body}
{specific body}
{py: 2 + 2}
"""
#print(convert(c))

if __name__ == '__main__':
    git_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True)
    if not git_status.stdout.decode().strip():
        story = open("./2-story/story.txt", "r+")
        text = story.read()
        con = convert(text)
        if con == text:
            print("No rolls found in story.")
            story.close()
        else:
            story.seek(0)     # go to start of file
            story.write(con)  # overwrite entire file
            story.truncate()  # if shorter, delete rest
            story.close()     # push cache to disk for git
            subprocess.run(["git", "add", "./2-story/story.txt"]) # tell git you changed this bit and want to save it
            subprocess.run(["git", "commit", "-m", "Rolled die for story."]) # save the story
            print("Something spicy happened.")
    else:
        print("Cannot roll die while files are in limbo!")
    print("Press the any key [enter] to continue...")
    input()

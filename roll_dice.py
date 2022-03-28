import subprocess, re

show = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True)
seed = not_random_number = int(show.stdout.decode().strip(), 16)
def randint(die):
    global seed
    if seed < die:
        seed += not_random_number
    ret = seed % die
    seed //= die
    return ret

def replace_die(x):
    count = int(x.group(1))
    roll = int(x.group(2))
    take_highest = int(x.group(3) or "0")
    take_lowest  = int(x.group(4) or "0")
    drop_highest = int(x.group(5) or "0")
    drop_lowest  = int(x.group(6) or "0")

    addsub = x.group(7)
    if addsub:
        connum = int(addsub + x.group(8))
    else:
        connum = 0

    bottom = 0
    top = count

    if take_highest: bottom = -take_highest
    if take_lowest:  top = take_lowest
    if drop_highest: top = -drop_highest
    if drop_lowest:  bottom = drop_lowest

    #return f"{count}.{roll}[{bottom}:{top}] = {list(range(1,count+1))[bottom:top]}"
    total = 0
    rolls = [randint(roll)+1 for _ in range(count)]
    rolls.sort()
    rolls = rolls[bottom:top]

    total = sum(rolls) + connum

    appstr =  f"[{count}d{roll}"
    if take_highest: appstr += f"th{take_highest}"
    if take_lowest:  appstr += f"tl{take_lowest}"
    if drop_highest: appstr += f"dh{drop_highest}"
    if drop_lowest:  appstr += f"dl{drop_lowest}"
    if addsub:       appstr += f" {connum:+}"
    appstr += f" = ({'+'.join(str(i) for i in rolls)}"
    if addsub:       appstr += f"{connum:+}"
    appstr += f") = {total}]"    

    return appstr

def replace_percent(x):
    return f"[{randint(101)}%]"

def replace_general_body(x):
    li = ["Head", "Left arm", "Right arm", "Torso", "Left leg", "Right leg"]
    return f"[general_body={li[randint(6)]}]"

def replace_specific_body(x):
    li = [
    "Left ear", "Right ear", "Left eye", "Right eye", "Nose", "Mouth",
    "Left Shoulder", "Left Upper arm", "Left Elbow", "Left Forearm", "Left Wrist", "Left Hand",
    "Right Shoulder", "Right Upper arm", "Right Elbow", "Right Forearm", "Right Wrist", "Right Hand",
    "Left upper Torso", "Right upper Torso", "Left middle Torso", "Right middle Torso", "Left lower Torso", "Right lower Torso",
    "Left Hip", "Left Thigh", "Left Knee", "Left Calf", "Left Ankle", "Left Foot",
    "Right Hip", "Right Thigh", "Right Knee", "Right Shin", "Right Ankle", "Right Foot"
    ]
    return f"[specific_body={li[randint(36)]}]"

def replace_code_eval(x):
    return f"[py:{x.group(1)} = {eval(x.group(1))}]"

def convert(content):
    content = re.sub(r'{(\d+)d(\d+)(?:th(\d+))?(?:tl(\d+))?(?:dh(\d+))?(?:dl(\d+))?(?:\w*(\+|-)\w*(\d+))?}', replace_die, content)
    content = re.sub(r'{percent}', replace_percent, content)
    content = re.sub(r'{general body}', replace_general_body, content)
    content = re.sub(r'{specific body}', replace_specific_body, content)
    content = re.sub(r'{py: ?(.+?)}', replace_code_eval, content)
    return content

c="""roll: {6d6}
roll: {6d8}
roll: {6d6th2}
roll: {6d6tl2}
roll: {6d6dh2}
roll: {6d6dl2}
roll: {6d6+2}
roll: {6d6-2}
{percent}
{general body}
{specific body}
{py: 2 + 2}
{py: randint(3)+5}
"""
#print(convert(c))

git_status = subprocess.run(["git", "status", "--porcelain"], capture_output=True)
if not git_status.stdout.decode().strip().split("\n"):
    with open("./story.txt", "rw") as story:
        story.write(convert(story.read()))


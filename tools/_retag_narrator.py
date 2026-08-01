"""
One-shot: add phrase-level performance direction to every narrator block.

Words are IDENTICAL -- only [direction] is added. The script verifies that before
writing anything, because the audit's word-for-word parity with the player depends
on the visible text never moving.

    python tools/_retag_narrator.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "script"))
import blocks as B  # noqa: E402

NEW = {
"cover_nar_01": "[warmly, slowly, drawing them in] The Hushabaloo. ... [almost a whisper, conspiratorial] Behind the third door on the left of the hall.",
"p1_nar_01": "[bright and inviting, a story beginning] In a house at the end of a hall that was long, [lilting] where the stairs had a squeak and the kettle a song, [warmly, introducing old friends] there was Etta, who planned. There was Mo, who could hear. [with a grin] There was Kip, who climbed everything, year after year.",
"p1_nar_02": "[picking up speed, delighted] And the house was so full of so much to be heard, [rattling them off joyfully] of a clank and a clink and a creak and a bird, of the hum of the fridge, of the drip of the tap, [landing it with a thump] of the whumpf of the dog as he flopped for a nap.",
"p1_nar_03": "[slowing right down, secretive] And the best of them all, and remember this trick, [quietly, leaning in] was the door down the hall. And the door went...",
"p1_nar_04": "[softly, savouring it] click.",
"p2_nar_01": "[puzzled, something is off] But on Tuesday the kettle did not sing its song. [more troubled] And the stairs did not squeak. And the tap-drip was gone.",
"p2_nar_02": "[building curiosity] Now the hall had three doors, and they knew one and two. [dropping to a hush] But the third door, the third door they'd never been through. [very quiet] And they stood there. And Mo put his ear to the wood.",
"p2_nar_03": "[dry, matter-of-fact] And there was. ... [gathering, urgent] For a sound they had heard every day of their lives, the small squeak of the stairs, came unstuck, and it dived [quickening] through the crack of that door with a...",
"p2_nar_04": "[flat, a little stunned] and was gone. [softly, sadly] And the stairs were as silent as snow, from then on.",
"p3_nar_01": "[hushed, careful] So they opened the door, and the door made no sound, and they stepped through the door, and they looked all around. [wondering] And behind the third door on the left of the hall [awed] was a room that was not in the house. Not at all.",
"p3_nar_02": "[full of awe, slow and wide] It was tall as a church and as wide as a town, [craning upward] and it went up so far that no ceiling came down. [marvelling] And on every last shelf, in a row, in a row, were the jars. And each jar had a label. [curious] And so...",
"p3_nar_03": "[quiet, uneasy, a slow reveal] Then a shelf became shoulders. [slower] A jar became eye. [barely breathing] And the thing they'd been sure was a wall said...",
"p4_nar_01": "[watchful, wary] And he reached out a hand that was mostly a sleeve, [sharper] and he took Kip's small laugh. [disapproving] And he did not ask leave.",
"p4_nar_02": "[flat, clipped] And he took Mo's low hum.",
"p4_nar_03": "[quicker, alarmed] And then, gentle and quick, he took Etta's own word, in the middle. Like this.",
"p4_nar_04": "[whispering, dreadful] And behind them, so soft that not one of them heard, he reached out once again. [slowly] And he took, from the door, [the worst of it] the small click that it made.",
"p4_nar_05": "[hollow] And the door was no more. ... [flat, three heavy beats] For a door with no click isn't really a door. It's a wall. It's a wall. It's a wall. [final] Nothing more.",
"p5_nar_01": "[warm, explaining patiently] Now Etta was five, which is old. And she knew that when somebody's taken a thing that's not theirs, [firmly] you say give it back, please. [proud of her] So she said it. She did.",
"p5_nar_02": "[dry, wincing sympathy] And the word that she needed went off in a jar. [slower] And she opened her mouth. ... [very small] And there wasn't a sound.",
"p6_nar_01": "[amused, fond] Then Kip sized the shelf up. Now, Kip is quite small. [with a knowing smile] But of all of the things about Kip, above all...",
"p6_nar_02": "[brisk, a climbing rhythm] Kip climbs. And Kip climbed. And Kip went up a shelf, and another, and up, and he leant",
"p6_nar_03": "[breathless, rising tension] and he reached for a jar, and he stretched, and he wobbled, and grabbed, and...",
"p6_nar_04": "[exhilarated, fast and joyful] And the jar came down hard, and the jar came apart, [thrilled] and out came the rain! All the rain! From the start! [racing] And it went up, and out, and it went through the wall, [triumphant] to the window it came from, right down the long hall.",
"p7_nar_01": "[deflating, sad] But the Hushabaloo sighed. And he lifted the shelf. [heavier] And he put it up high, where a person can't climb. [almost inaudible] And he said it so softly, and mostly himself...",
"p7_nar_02": "[very slow, very quiet, emptying out] And it got very dark. And it got very still. [slower] And the three of them sat. And they sat. And they sat. [hushed] And there wasn't a squeak. And there wasn't a drip. [barely a whisper] And there wasn't a sound in the world. ... [empty] Just like that.",
"p7_nar_03": "[gently, tenderly] And Etta, who's five, and who plans, and who's brave, [softly] had no plan. And she said it out loud, very small...",
"p7_nar_04": "[a spark returning] But then Mo, who hears things that the rest of us miss, [curious, quiet] put his hand on a jar. And he listened. Like this.",
"p7_nar_05": "[quickening, excited] And Etta's eyes went round and wide.",
"p8_nar_01": "[fast, breathless, everything at once] So Kip climbed. Because Kip climbs. And Mo found the jar, because Mo always finds them. That's just what Mo does. [urgent] And Etta said...",
"p8_nar_02": "[building, gleeful] and the twins, who were two, did the one thing that two-year-old people do best.",
"p8_nar_03": "[building, gathering force] And it wasn't a squeak. And it wasn't a drip. And it wasn't the rain, and it wasn't a door. [louder, delighted] It was nothing! It meant nothing! It came from a lip and it went nowhere useful, [joyously] a wonderful roar of a silly, wet, pointless, ridiculous noise [landing it] that had no jar at all.",
"p8_nar_04": "[slower, almost pitying] And he looked for a jar. And he looked. And he looked. And he looked down the hall of ten thousand jars... [quiet wonder] and there wasn't one. Not one. Not a label. Not one. Not at all. Not a jar.",
"p8_nar_05": "[quiet, certain, the hinge of it] And a thing with no jar is a thing you can't keep.",
"p8_nar_06": "[joyful, headlong, unstoppable] And the empty jar popped. And the next. And the next. [faster, exultant] And the rain and the dog and the kettle and drip and the whumpf and the hum and the squeak of the stair [soaring] went UP, and went OUT, and went HOME through the air.",
"p9_nar_01": "[coming down from the roar, hushed] And in all of that noise, in that whole rushing flood, [very quiet] there was one little sound that was smaller than most.",
"p9_nar_02": "[warm, proud] And Mo heard it. Of course. Because that's what Mo does. [gently] And he pointed. And there, in the dark, was a...",
"p9_nar_03": "[relieved, warm] click. [brightening] And a door with a click is a door once again.",
"p9_nar_04": "[slowing, tender] But they stood in the doorway. And turned. And they saw that the Hushabaloo hadn't got anything more. [sadly] He had shelves. He had jars. He had none of them full. [very softly] And he sat down. And he was extremely small.",
"p9_nar_05": "[gentle, quiet] And she walked all the way back, and stood by his knee.",
"p9_nar_06": "[warmly, with a smile in it] And she blew him a raspberry, right through the air.",
"p9_nar_07": "[tender, unhurried] And he caught it. And held it. And kept it. Right there. [softly] And he put it in nothing. No jar and no lid. [thoughtfully] Just held it, which is, I suppose, what you do with a sound that was given and not taken. ... [warmly] He did. And he smiled. If a Hushabaloo can. And he knew.",
"p9_nar_08": "[coming home, warm and slowing] So they went down the hall to the house that was theirs, where the kettle had a song, and a squeak had the stairs, [contented] where the pipes gave a knock, and the tap gave a drip, and the dog gave a whumpf...",
"p9_nar_09": "[softly, home at last] and the door gave a click.",
"final_nar_01": "[quiet, direct, sincere] For everybody small who was ever once told to be quiet, be quiet, be quiet, be still... [warm and certain] here's a story where noise is the thing that saves all.",
"final_nar_02": "[playful, inviting, with a grin] Go on. ... [conspiratorial] Make the sound. You know the one.",
}


def visible(t):
    t = re.sub(r"\[.*?\]", " ", t)
    t = re.sub(r"\.{2,}", " ", t)
    return " ".join(t.split())


def main():
    old = {b[0]: b[3] for b in B.BLOCKS}

    # Guard: direction may be added, words may not move.
    drift = [k for k, v in NEW.items() if visible(v) != visible(old.get(k, ""))]
    if drift:
        for k in drift:
            print(f"WORD DRIFT in {k}")
            print(f"  was: {visible(old.get(k, ''))[:110]}")
            print(f"  now: {visible(NEW[k])[:110]}")
        sys.exit("aborted -- narrator words must not change, only direction")

    path = ROOT / "script" / "blocks.py"
    src = path.read_text(encoding="utf-8")
    for bid, text in NEW.items():
        # Some blocks sit on one line, others wrap across several -- match both.
        pat = re.compile(
            r'(\("' + re.escape(bid) + r'", "speech", "NARRATOR",\s*)(".*?")'
            r'(,\s*(?:LINE|BEAT|SECTION|PAGE|0\.0), ")', re.S)
        m = pat.search(src)
        if not m:
            sys.exit(f"could not locate {bid} in blocks.py")
        src = src[:m.start(2)] + '     "' + text.replace('"', '\\"') + '"' + src[m.end(2):]
    path.write_text(src, encoding="utf-8")
    print(f"rewrote {len(NEW)} narrator blocks -- visible words unchanged")


if __name__ == "__main__":
    main()

import re

a="{'volume': 48}{'volume': 46}"

c=re.compile('\{\'volume\': \d+\}$')

d=c.search(a)

print(d)

import pyttsx3


engine = pyttsx3.init()
#engine.setProperty('rate', 100)
engine.setProperty('volume', 0.5)
engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()

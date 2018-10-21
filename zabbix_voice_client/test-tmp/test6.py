
locations=0
raw_nums=0
while 1:
    with open('OnWrite.txt', 'r')as f:
        print(locations,raw_nums)
        f.seek(locations, 0)
        lines = f.readlines()
        raw_nums = len(lines) + 1
        locations = f.tell()
    import time
    time.sleep(3)
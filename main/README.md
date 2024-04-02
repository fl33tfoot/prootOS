

LOG ERROR IDs
0 = no error (not shown)

11 = generic code error
12 = hardware error
13 = network error
14 = file operation error

100 = file structure not formatted correctly (update.py)
101 = update.zip file not found (update.py)
102 = unimportable config.json file. i could write a module to repair 
      this through some hacky text manipulation but tbh the only reason 
      this would happen is if youre editing the json manually. which is
      why i wont make a module for this cus you prolly just left an extra
      comma where it shouldnt be. sorry for the hostility. im sleepy.
103 = Different hashfile 

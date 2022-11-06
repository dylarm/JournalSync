# Journal Sync
A brief script to sync a journal from Monica to plain-text (i.e., Zim wiki)

## Currently functional
- Connect to Monica API 
- Download journal (at least, one page worth)
- Reformat journal JSON into usable Python
- Checking if folder structure is already present

## Next steps
- [x] Create an actual flow for syncing rather than working at it haphazardly
- [x] Create skeleton `config.yml` file (and maybe load if populated)
- [ ] Make folder structure if it doesn't exist (per entry)
- [ ] Create (touch) Zim file for entry
- [ ] Add journal entries to each text file
  - [ ] Have a way of creating entries/files in a reproducible way (to check if they need to be added to or rewritten/created)

The current dilemma is that Zim (specifically Zim) will only have one file per day, while Monica may have an unlimited number.
This presents a problem in determining if a file in Zim has all the entries for a particular day in Monica.
Ideas:
- Overwrite the Zim file with the concatenated data from Monica (simple)
- Have Monica entries in a Zim file appear after a certain "tag" (little more complicated)
  - This is likely the way it'll go

## Ideal flow
This is how the program is supposed to work, ideally:
![](./JournalSync.png)

But for right now, after getting the Monica data, it creates a Zim page and just writes to the file, regardless of existing contents.
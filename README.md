# Journal Sync
A brief script to sync a journal from Monica to plain-text (i.e., Zim wiki)

## Currently functional
- Connect to Monica API 
- Download journal (at least, one page worth)
- Reformat journal JSON into usable Python
- Checking if folder structure is already present

## Next steps
- [ ] Make folder structure if it doesn't exist (per entry)
- [ ] Create (touch) Zim file for entry
- [ ] Add journal entries to each text file
  - [ ] Have a way of creating entries/files in a reproducible way (to check if they need to be added to or rewritten/created)
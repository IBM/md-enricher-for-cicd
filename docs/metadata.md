

# Metadata replacements
These common variables can be used in the metadata of each of your markdown content files without including them in your own reuse files.



<br />

|Metadata variable|Description|
|----------|-----------|
|`[{<!--Do not transform-->CURRENT_YEAR}]`|In the copyright metadata, the current year is automatically inserted. At the start of the new year, the value will change automatically the next time you make a change to the file. You can choose whether to force a change to every file by adding something like a line break or just let them update as you make necessary content changes.|
|`[{<!--Do not transform-->LAST_UPDATED_DATE}]`|The date of the last file modification is automatically inserted at build time.|

Example metadata source for the marked-it markdown processor:
```
---

copyright:
  years: 2014, [{<!--Do not transform-->CURRENT_YEAR}]
lastupdated: "[{<!--Do not transform-->LAST_UPDATED_DATE}]"

keywords: keyword1, keyword2

subcollection: subcollection-name

---
```

Example output:
```
---

copyright:
  years: 2014, 2022
lastupdated: "2022-12-13"

keywords: keyword1, keyword2

subcollection: subcollection-name

---
```

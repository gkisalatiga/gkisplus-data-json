# gkisplus-data-json
Dedicated JSON cloud repo for the church app GKI Salatiga+ and the admin app Simon Petrus

- Status code for "not writing any change because there is no change in data" is **234**.
- Status which calls for the creation of a new commit (because there is data change/update) is **0**.

In each JSON node, the following key is used for comment: `"_comment"`. Do not parse this node!

## v2.3 Update Note

**gkisplus-main**
- `data/backend/flags/is_feature_seasonal_shown` is deprecated. Use `data/backend/is_feature_seasonal_v2_3_shown` instead to control the visibility of the entire seasonal menu.
- `data/backend/flags/is_feature_bible_shown` is deprecated. Use `data/backend/is_feature_bible_new_shown` instead to control the visibility of the Bible menu.
- Use `data/backend/flags/is_feature_inspirations_shown` ("0" or "1") to control the visibility of the "Inspirations"/spinwheel menu.

**gkisplus-modules**

- Use `modules/seasonal-v2-3` in place of `modules/seasonal` for reading seasonal data (Easter, Christmas, Family Month, etc.), because `modules/seasonal` is deprecated.
- In `modules/seasonal-v2-3`, there is `active` key (values between "0" and "1"). Use this API to show/hide a certain seasonal menu (e.g., set to "0" in "Christmas 2024" to hide "Christmas 2024" seasonal menu).
- `modules/inspirations` is introduced. This is where spinwheel data are stored. (The spinwheel can be placed in the main menu.) This node is an array-typed JSON node, each item consisting of the following JSON object keys:

```js
...
"modules": {
    ...
    "inspirations": [
        {
            // the title of the spinwheel.
            "title": "40 Hari Niat Baik (Anak)",
            // the description of the spinwheel.
            "desc": "Inspirasi niat baik bagi anak-anak untuk dilakukan selama Puasa Prapaskah 2026.",
            // for generality, perhaps needed in the future.
            "type": "spinwheel",
            // the front banner of the spinwheel menu.
            "banner": "https://raw.githubusercontent.com/gkisalatiga/gkisplus-data/refs/heads/main/images-seasonal/mrn_2025_banner.webp",
            // UUID for the current spinwheel.
            "uuid": "bccf4869-e667-4356-a4c9-9ff2915668bd",
            // tags (in array format, used for e.g. search functionality)
            "tags": ["mrp-2026"],
            // the date this spinwheel was added to the JSON.
            "date": 1769789343,
            // whether or not this particular spinwheel should be displayed in the "inspirations" menu.
            "is_shown": 1,
            // the individual spinwheel items.
            "content": [
                {
                    // ID (relative to each spinwheel).
                    "i": 0,
                    // The illustrative picture of the current item
                    // (pops up only after the spinwheel stops spinning and an item is selected).
                    "p": "https://raw.githubusercontent.com/gkisalatiga/gkisplus-data/refs/heads/main/images-seasonal/mrn_2025_buku.webp",
                    // The spinwheel string.
                    "s": "Mengucapkan niat sebelum belajar atau bermain"
                },
                {
                    "i": 1,
                    "p": "https://raw.githubusercontent.com/gkisalatiga/gkisplus-data/refs/heads/main/images-seasonal/mrn_2025_buku.webp"
                    "s": "Merapikan mainan setelah digunakan",
                }
                ...
            ]
        },
    ]
    ...
}
...
```

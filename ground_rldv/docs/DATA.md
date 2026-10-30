# Data notes

## Records

The subset contains selected velocity exports from moving-vehicle pavement tests. Condition labels and file checksums are recorded in [the manifest](../data/manifest.json).

## Format

The TXT files use `gb18030` encoding. The original tab-separated header is followed by two numeric columns:

| Column | Meaning | Unit |
| --- | --- | --- |
| 1 | Exported time | s |
| 2 | Exported velocity | mm/s |

Original numeric values and row order are preserved. Exported time values repeat; they are not a verified acquisition time base. The acquisition sampling rate is not supplied, so the preview uses sample index and preserves all rows. The velocity component is reported as exported, without assigning a vertical or line-of-sight interpretation.

## Example programs

The reader checks the supplied files against their manifest. The preview plots the recorded values without filtering, normalization, or event alignment. These programs demonstrate data access and visualization; specialized research processing is retained separately.

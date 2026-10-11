# SteadyStud — Product spec (pro-speed) v0.3

## Core product truth (avoid overclaiming)
Magnetic stud finders detect **metal fasteners** (nails/screws) in studs. Users often confirm by finding multiple fasteners and inferring stud position/spacing.

Source: https://en.wikipedia.org/wiki/Stud_finder

## Pro-speed positioning
This is a tool for people who do this repeatedly.
- Fast to locate
- Fast to mark
- Low friction on wall
- Durable; magnets do not fall out

## Dimensions (authoritative)
- Target length: **5.0 inches** (confirmed by you)
- STEP v1 extents support 5.0 in length when interpreted as inches.

Source: your confirmation + `Magnetic Stud Finer v1.step` extents.

## Design requirements
### Speed loop (the whole point)
1) Slide along wall
2) Feel the “snap” at a fastener
3) Mark immediately (built-in notch) without shifting position

### Wall-safe
- Edge radii/chamfers to avoid scratching paint
- Finish choice matters (anodize or smooth bead-blast + clear)

### Marking notch
- Must accommodate common pens/Sharpie; must guide tip consistently.
- We will dimension and tolerance it from STEP v1 (no guessing).

## Next CAD-derived outputs
- A dimension table (overall + notch + magnet pocket)
- DFM recommendation: full CNC vs hybrid vs 2D cut

# StitchToon Gui
Graphical user interface for [stitchtoon](https://github.com/BishrGhalil/stitchtoon) written in Python and Qt6.

## Features over SmartStitch
Stitchtoon is a fork of SmartStitch, However it offers much more features like:
- An option to split into a specific number of images.
- Auto conversion between `PSD` and `PSB` when maximum size exceeded.
- Batch mode is optional.
- Better code which is easier to maintain.
- Better errors handling, It won't simply fail without telling you why.
- Better logs, disabled by default.
- Better output names, It won't output as `[stitched]`.
- Better progress bar.
- Dark and light themes with multiple accents.
- Environment variables in post-process arguments.
- Export as archive.
- New mode for width enforcement.
- Post-process output will be shown.
- Tools Tips all over the interface.
- Transparency support.

### Screenshots
![stitch tab](.github/screenshots/home.png)

## Install

Build from source
```
git clone https://github.com/BishrGhalil/stitchtoon-gui
cd stitchtoon-gui
pip instal --user requirements.txt
pip install .
stitchtoon-gui
```
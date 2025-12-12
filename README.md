# Ashs Image Converter

## No subscriptions. No logins. No cloud. No account.
### Because 4GB installers for resizing a PNG are unhinged… fuck you, Adobe.

What Is This?

This is a small, fast, local desktop application for doing image chores without:

a subscription

an account

a cloud sync

a login popup

a “your trial ends in 3 days” threat

a creative director asking how the image feels

It exists because opening Photoshop to:

resize an image

convert a format

make a Windows icon

is an act of self-harm.

So I built a tool that just does the job and shuts up.

What This App Does (And Does Well)
Convert Images Like a Normal Person

Convert between:

PNG

JPG / JPEG

WEBP

BMP

TIFF

Batch convert entire folders

Choose output format from a dropdown

Choose output folder

Keep original filenames or add prefixes/suffixes

Auto-number files so nothing explodes

No “Export As…”
No “Save for Web…”
No dialogs nested inside dialogs.

Resize Images Without Summoning a Wizard

Optional resize controls:

Set width + height

Keep aspect ratio (like a sane human)

Resize modes:

Fit inside (contain)

Fill and crop (cover)

Stretch (if you hate yourself)

Prevent upscaling so small images don’t turn into mush

Quality slider for JPEG / WEBP

Optimization toggle for smaller file sizes

You click a checkbox.
The image resizes.
That’s it.
That’s the whole ceremony.

Proper Windows ICO Generator (This Is Important)

If you’ve ever made a Windows icon, you already know the pain.

This app:

Takes a single input image (PNG with transparency recommended)

Generates a proper multi-size .ico

Default sizes included:

16, 24, 32, 48, 64, 128, 256

Works correctly with PyInstaller

Includes previews at multiple sizes so your icon doesn’t look like a crime scene

No external websites.
No sketchy converters.
No “why does my taskbar icon look blurry”.

Drag & Drop (Because It’s Not 1998)

Drag one file

Drag ten files

Drag a whole folder

It just works

No file-picker marathons.

Preview Everything Before You Commit

See the original image

See the resized output preview

See output format, size, filename, destination

Know exactly what you’re about to get

No surprises. No “oops”.

Extras That Actually Matter

Strip EXIF metadata (privacy + smaller files)

Auto-rotate photos using EXIF (sideways photos begone)

Transparency handling:

PNG → JPG warnings

Choose background fill colour

Copy output path to clipboard

Open output folder with one click

Clear error messages when something fails

If a file breaks, it tells you which one and why.

UI Philosophy

Dark blue background

Orange highlights

No light mode

No pastel nonsense

No “friendly onboarding experience”

It’s a tool.
You already know what you want to do.
This app respects that.

What This Is NOT

Not a cloud app

Not a web service

Not AI-powered

Not subscription-based

Not trying to upsell you anything

Not tracking you

Not asking for an account

Not asking how you’re feeling today

Absolutely fuck Adobe, but also:
fuck the idea that every tiny utility needs to be a platform.

Requirements
pip install PyQt5 pillow


That’s it.
Two dependencies.
Not forty-seven.

Run It
python main.py


The app opens maximized, ready to work, no warm-up lap.

Why This Exists

Because:

resizing an image should not require a login

converting formats should not require a subscription

making an ICO should not feel like necromancy

and 4GB installers for resizing a PNG are genuinely unhinged

So again, with feeling:

Fuck Adobe.

Final Notes

This is a personal tool.
Built out of irritation.
Used daily.
Shared with friends who are also tired.

If it saves you five minutes, that’s a win.
If it saves you from opening Creative Cloud, that’s a victory.


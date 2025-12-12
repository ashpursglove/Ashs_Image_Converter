# Ash’s Image Converter

**No subscriptions. No logins. No cloud. No account.**  
Because **4GB installers for resizing a PNG are unhinged… fuck you Adobe.**

---

## What Is This?

Ash’s Image Converter is a small, fast, local desktop application for doing basic image chores without:

- subscriptions  
- accounts  
- cloud syncing  
- telemetry  
- login popups  
- “your trial ends soon” warnings  
- software that thinks it’s a lifestyle brand  

It exists because opening Photoshop to resize an image, convert a format, or generate a Windows icon is an act of unnecessary suffering.

So this app does the job and gets out of the way.

---

## What This App Does

### Image Conversion
<img width="1918" height="1017" alt="image" src="https://github.com/user-attachments/assets/bd0ca175-468f-43fd-b2b2-b301217e738b" />


Convert images between common formats without ceremony:

- Supported input formats:
  - PNG
  - JPG / JPEG
  - WEBP
  - BMP
  - TIFF
  - GIF
- Supported output formats:
  - PNG
  - JPG / JPEG
  - WEBP
  - BMP
  - TIFF

Additional features:
- Batch conversion
- Folder-level imports
- Custom output directory
- Filename handling:
  - Keep original names
  - Add prefix or suffix
  - Auto-number to avoid collisions

No “Export As”.  
No nested dialogs.  
No surprises.

---

### Resize (Optional)

Resize is fully optional and entirely under your control.

- Set width and height in pixels
- Keep or unlock aspect ratio
- Resize modes:
  - Fit inside (contain)
  - Fill and crop (cover)
  - Stretch (if you insist)
- Prevent upscaling to avoid blurry images
- Quality control for JPEG / WEBP
- Optional optimization for smaller file sizes

You enable resize, set the numbers, and move on with your life.

---

### Windows ICO Generator
<img width="1918" height="1017" alt="image" src="https://github.com/user-attachments/assets/9572e940-eeac-4252-8f20-4e7151faa925" />


This is a first-class feature, not an afterthought.

- Generate proper multi-size .ico files
- Designed to work correctly with PyInstaller
- Select exactly which sizes to include
- Default sizes:
  - 16
  - 24
  - 32
  - 48
  - 64
  - 128
  - 256
- Live preview at multiple resolutions

No web converters.  
No blurry taskbar icons.  
No ritual sacrifices.

---

### Drag & Drop

- Drag individual files
- Drag multiple files
- Drag entire folders

The app does not argue with you about this.

---

### Preview Before You Commit

- Preview the original image
- Preview resized output
- See format, dimensions, output name, and destination
- Optional before/after comparison

If something looks wrong, you see it before it gets written to disk.

---

### Useful Extras (Not Gimmicks)

- Strip EXIF metadata for privacy and smaller files
- Auto-rotate images using EXIF orientation
- Transparency handling:
  - Clear warnings when converting PNG to JPG
  - Choose background fill colour
- Copy output paths to clipboard
- Open output folder with one click
- Clear per-file error reporting during batch operations

When something fails, the app tells you exactly what and why.

---

## The EXE (Yes, I Included One)

There is a **pre-built Windows executable** included in this repo.

This means:
- No Python install required
- No virtual environments
- No dependency wrangling
- Double-click and go

This is here for:
- convenience
- friends
- people who just want the tool to work

### Important Cultural Note

Using the EXE is **technically cheating**.

OGs:
- clone the repo
- read the code
- install the dependencies
- run it from source
- nod quietly at their own competence

But it’s fine.
Not everyone has the time.
Clicking the EXE does not make you a bad person.
Just… spiritually, you know what you did.

---

## Requirements (If You’re an OG)

If you’re running from source, you’ll need:

PyQt5  
pillow  

Install them however you normally install Python things without crying.

Two dependencies.  
That’s it.

---

## Running the App

If you’re building it yourself:

python main.py

If you’re using the EXE:

Double-click it.
Enjoy your life.
No further steps.

---

## UI Philosophy

- Dark blue background
- Orange highlights
- Clean, readable text
- No light mode
- No visual noise

This is a tool, not a branding exercise.

---

## What This Is Not

- Not a web app
- Not cloud-based
- Not subscription software
- Not AI-powered
- Not telemetry-heavy
- Not interested in your email address
- Not asking how you feel today

And very specifically:

Not Adobe.

---

## Why This Exists

Because:

- resizing an image should not require a login
- converting formats should not require a monthly payment
- generating an ICO should not feel like necromancy
- and 4GB installers for resizing a PNG are objectively unhinged

So yes.

Fuck Adobe.

---

## Final Notes

This is a personal tool built out of irritation and used a lot.

Use the EXE if you want.  
Build it from source if you must.  
Judge others silently either way.

If it saves you time, good.  
If it saves you from opening Creative Cloud, even better.
If it takes buisness away from Adobe, thats a **victory!**


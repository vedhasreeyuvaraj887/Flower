# Air Flower Draw

A tiny prototype: point your webcam at yourself, pinch your thumb and index
finger together, and move your hand to "paint" a trail of flowers on
screen. Change color with number keys.

## Setup

1. Make sure you have Python 3.9–3.11 installed (MediaPipe doesn't always
   have wheels for the very latest Python versions yet — if `pip install`
   fails on your current version, try 3.10 or 3.11).
2. (Recommended) create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run

```bash
python air_flower_draw.py
```

A window will open showing your webcam feed.

## Controls

| Key   | Action                          |
|-------|----------------------------------|
| 1–8   | Change flower color              |
| c     | Clear the canvas                 |
| s     | Save a screenshot to `screenshots/` |
| q/Esc | Quit                              |

## How drawing works

Pinch your **thumb tip and index fingertip** together — that's the "pen
down" gesture. Move your hand while pinching to lay down a trail of
flowers. Let go of the pinch to lift the pen and start a new stroke
elsewhere.

## Notes / things you can tweak

- `CAM_INDEX` in the script — change if you have more than one camera.
- `PINCH_THRESHOLD` — how close thumb+index need to be to count as a pinch.
  Increase if it's not triggering, decrease if it triggers too easily.
- `MIN_FLOWER_SPACING` — how far you need to move before a new flower is
  stamped (controls trail density).
- `FLOWER_SIZE` — size of each flower.
- Colors live in the `COLORS` dict near the top of the script — add your
  own by picking a free key and a BGR color tuple.

## Troubleshooting

- **Camera doesn't open**: check OS camera permissions for your terminal
  app, and confirm no other app is using the webcam.
- **Hand not detected**: make sure your hand is well-lit and fully in
  frame; MediaPipe struggles with very dim or backlit scenes.
- **mediapipe fails to install**: it currently doesn't support every
  Python version — try running this in a Python 3.10 or 3.11 virtualenv.

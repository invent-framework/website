"""
Invent Framework website — cube animations and dark mode.

Replaces the original JavaScript with MicroPython via PyScript,
using pyscript.web for DOM queries and @when for event handling.
"""

import random
from pyscript import document, window, when, fetch
from pyscript.web import page
from pyscript.ffi import create_proxy


# Icon sprite IDs (filenames without .svg extension).
ICON_IDS = [
  "abundance", "aid-to-elderly", "alien",
  "alternate-route", "alzheimers-disease", "exit",
  "antenna", "assembly-line", "assistance-dog",
  "asteroid", "astronaut-happy", "autogyro",
  "autostop", "awareness", "banana-peel",
  "barbeque", "beach-ball", "bed-jumping",
  "bicycle-repair", "big-fish-eats-small-fish",
  "binoculars", "bird", "birthday-cake", "blood",
  "bone-fracture", "books", "boomerang", "boot",
  "brain-in-a-jar", "brainwash", "breaking-rule",
  "breaking-the-glass-ceiling", "bridge", "buoy",
  "button", "caged", "can-of-worms", "car-light",
  "cat", "cellist", "cell-phone", "cheese",
  "cherries", "clock", "coffee", "comforting",
  "computer", "conductor", "conference-call",
  "cook", "cooperation", "cow", "crank-radio",
  "crash-test-dummy", "crowd", "cruise-ship",
  "crystal-ball", "customer-satisfaction",
  "customer-support", "cyborg", "data-transfer",
  "dice", "dirigible", "dirty-hands", "disco",
  "disguise", "distracted", "diver", "diversity",
  "dj", "document", "dog", "dolphin",
  "domino-effect", "donkey", "doorbell",
  "drink-from-tap", "drone", "drummer",
  "earthquake", "edit", "ejection-seat",
  "elbow-pain", "elderly", "electric-bike",
  "electric-scooter", "elephant", "embrace",
  "ev-charger", "falling", "falling-objects",
  "falling-piano-missed", "fan", "farmer",
  "firework-display", "first-aid", "fisher",
  "fist-bump", "flight-attendant", "follower",
  "frog", "fruit-picking", "gas-mask", "gift",
  "give-and-receive", "google-glass", "government",
  "graduate", "haircut", "hammer",
  "hard-hat-worker", "head-in-the-clouds", "hello",
  "help-mechanic", "help-spanner", "help-water",
  "hetero-couple", "high-five", "hiker-female",
  "honey-bee-nest", "horse-and-cart", "hospital",
  "hoverboard", "hunger", "hydrant",
  "idea-exchange", "immersive-experience",
  "information", "intercom",
  "intergalactic-couple", "justice", "kettle",
  "key-to-happiness", "king", "knee-pain",
  "laptop", "leapfrog", "liberating", "lifting",
  "lightness", "luggage", "mail-truck", "marriage",
  "measuring", "medical-helicopter", "meditation",
  "metal-detector", "microphone", "microscope",
  "mind-blowing", "mirror", "miss", "mobile-phone",
  "mood-gauge", "mothering",
  "motorized-wheelchair", "moving-truck", "muffin",
  "musicians", "navigation-app", "notepad", "okay",
  "onewheel", "open-minded", "orange",
  "paint-palette", "parenthood", "peace-dove",
  "periscope", "person-female", "person-male",
  "pets", "pianist", "pie", "pipe",
  "planting-tree", "power", "presentation",
  "prodding", "prosthetic-arm", "prosthetic-leg",
  "qr-code", "radio", "reading-book",
  "reading-screen", "recumbent-bicycle", "reminder",
  "remote-access", "remote-control",
  "renewable-energy", "responsive-design",
  "rice-bowl", "robot", "rocket",
  "romeo-and-juliet", "safe", "sea-level-rise",
  "seedling", "segway", "shelter", "shower",
  "sick", "skull-and-crossbones", "sliders",
  "slingshot", "slipping", "smart-speaker",
  "smartwatch", "soccer-ball", "solar-panel",
  "speed-bump", "springboard", "statue", "stature",
  "strategizing", "strategy",
  "strategy-presentation", "strawberry",
  "street-vendor", "stroller", "submarine",
  "superhero", "surgical-mask", "tablet", "target",
  "taxi", "telephone", "telescope", "test-tube",
  "thinking", "thumbs-down", "thumbs-up",
  "tools-hammer", "train-stop",
  "traveler-backpacker", "truck", "tug-of-war",
  "turn-around-car", "turn-around-plane", "ufo",
  "umbrella", "unicycle", "unsustainable",
  "uphill-climb", "van", "video-camera",
  "vote-casting", "voting-machine", "waiter",
  "walking-aid", "water-filter",
  "water-temperature", "weight-lifting", "wetland",
  "wheelchair-aide", "wheelchair-racer", "whole",
  "wifi-bus", "wifi-connected", "windmill-offshore",
  "winner", "womens-empowerment", "world",
  "writing", "zipline", "zoom", "wildfire", "gears",
  "lips", "service-truck", "shipwreck",
]

# Cube face background colours.
COLORS = [
  "#FFD700", "#C9B037", "#FFA500", "#FF8C00",
  "#FF5722", "#9CCC65", "#66BB6A", "#4DD0E1",
  "#42A5F5", "#1976D2", "#283593", "#BA68C8",
  "#EC407A", "#D81B60",
]

FACES = ["front", "right", "back", "left", "top", "bottom"]

# CSS transition duration for cube rotation (ms).
ANIMATION_MS = 1000

# Per-cube animation state, keyed by data-cube attribute.
cube_states = {}


def pick_random(items):
  """Return a random element from a list."""
  return items[random.randint(0, len(items) - 1)]


def shuffle(items):
  """Return a shuffled copy of a list."""
  result = list(items)
  for i in range(len(result) - 1, 0, -1):
    j = random.randint(0, i)
    result[i], result[j] = result[j], result[i]
  return result


def get_key(cube_el):
  """Return the data-cube attribute as a unique key."""
  return cube_el.getAttribute("data-cube")


def current_face(cube_el):
  """Return the currently shown face name, or None."""
  cn = cube_el.className
  for face in FACES:
    if f"show-{face}" in cn:
      return face
  return None


def assign_colors(cube_el):
  """Assign shuffled colours to each face of a cube."""
  shuffled = shuffle(COLORS)
  for i, face in enumerate(FACES):
    el = cube_el.querySelector(f".cube__face--{face}")
    if el:
      el.style.backgroundColor = shuffled[i]


def rotate_on_hover(cube_el):
  """Rotate to a random different face.

  For non-letter cubes the incoming face's icon is also
  replaced with a random icon from the sprite.
  """
  cur = current_face(cube_el)
  if not cur:
    return
  available = [f for f in FACES if f != cur]
  new = pick_random(available)
  is_letter = "letter-cube" in cube_el.className
  # Swap the icon on the target face for icon cubes.
  if not is_letter:
    face_el = cube_el.querySelector(
      f".cube__face--{new}"
    )
    if face_el:
      use_el = face_el.querySelector("use")
      if use_el:
        use_el.setAttribute(
          "href", f"#{pick_random(ICON_IDS)}"
        )
  base = "cube letter-cube" if is_letter else "cube"
  cube_el.className = f"{base} show-{new}"


def process_queue(cube_el):
  """Drain one queued rotation for a cube."""
  key = get_key(cube_el)
  state = cube_states.get(key)
  if not state or state["animating"]:
    return
  if state["queued"]:
    state["queued"] = False
    state["animating"] = True
    rotate_on_hover(cube_el)

    def done():
      """Animation finished; check for another queued turn."""
      state["animating"] = False
      process_queue(cube_el)

    window.setTimeout(create_proxy(done), ANIMATION_MS)
  else:
    state["animating"] = False


# ── Dark mode ──────────────────────────────────────────────

saved_theme = window.localStorage.getItem("theme") or "light"
if saved_theme == "dark":
  document.body.classList.add("dark-mode")
  document.getElementById("themeIcon").textContent = "\u2600\ufe0f"


@when("click", "#themeToggle")
def toggle_theme(event):
  """Toggle between light and dark mode."""
  document.body.classList.toggle("dark-mode")
  is_dark = document.body.classList.contains("dark-mode")
  window.localStorage.setItem(
    "theme", "dark" if is_dark else "light"
  )
  icon_el = document.getElementById("themeIcon")
  icon_el.textContent = (
    "\u2600\ufe0f" if is_dark else "\U0001f319"
  )


# ── Cube hover rotation ───────────────────────────────────

def on_mouseover(event):
  """Start or queue a rotation when the pointer enters a cube."""
  cube_el = event.target.closest(".cube")
  if not cube_el:
    return
  key = get_key(cube_el)
  if key not in cube_states:
    cube_states[key] = {
      "animating": False, "queued": False,
    }
  state = cube_states[key]
  if not state["animating"] and not state["queued"]:
    state["animating"] = True
    rotate_on_hover(cube_el)

    def done():
      """Animation finished; drain queue."""
      state["animating"] = False
      process_queue(cube_el)

    window.setTimeout(
      create_proxy(done), ANIMATION_MS
    )
  elif not state["queued"]:
    state["queued"] = True


document.addEventListener(
  "mouseover", create_proxy(on_mouseover)
)


# ── Sprite loading and cube initialisation ─────────────────

response = await fetch("icons/icons-sprite.svg")
svg_text = await response.text()

# Inject the sprite into the top of <body>.
wrapper = document.createElement("div")
wrapper.innerHTML = svg_text
sprite = wrapper.firstElementChild
document.body.insertBefore(sprite, document.body.firstChild)

letter_cubes = []
icon_cubes = []

for cube_el in page.find(".cube"):
  assign_colors(cube_el._dom_element)
  random_face = pick_random(FACES)
  is_letter = "letter-cube" in cube_el.className
  base = "cube letter-cube" if is_letter else "cube"
  cube_el.className = f"{base} show-{random_face}"
  key = get_key(cube_el._dom_element)
  cube_states[key] = {
    "animating": False, "queued": False,
  }
  # Replace stale icon hrefs for non-letter cubes.
  if not is_letter:
    for face in FACES:
      face_el = cube_el._dom_element.querySelector(
        f".cube__face--{face}"
      )
      if face_el:
        use_el = face_el.querySelector("use")
        if use_el:
          use_el.setAttribute(
            "href", f"#{pick_random(ICON_IDS)}"
          )
  data = {
    "el": cube_el._dom_element,
    "current_face": random_face,
    "is_letter": is_letter,
  }
  if is_letter:
    letter_cubes.append(data)
  else:
    icon_cubes.append(data)


# ── Periodic auto-rotation ─────────────────────────────────

reduced_motion = window.matchMedia(
  "(prefers-reduced-motion: reduce)"
).matches

if not reduced_motion:

  def is_visible(cd):
    """True when the cube is rendered on screen."""
    return cd["el"].offsetParent is not None

  def get_col(cd):
    """Horizontal pixel position of the cube's scene."""
    rect = cd["el"].parentElement.getBoundingClientRect()
    return round(rect.left)

  def auto_rotate():
    """Pick a letter cube and an icon cube and queue rotations."""
    def frame(_timestamp=None):
      """Run inside requestAnimationFrame."""
      vis_l = [c for c in letter_cubes if is_visible(c)]
      vis_i = [c for c in icon_cubes if is_visible(c)]
      if not vis_l or not vis_i:
        return
      lc = pick_random(vis_l)
      lc_col = get_col(lc)
      diff = [
        ic for ic in vis_i
        if abs(get_col(ic) - lc_col) > 10
      ]
      ic = (
        pick_random(diff) if diff
        else pick_random(vis_i)
      )
      for cd in (lc, ic):
        key = get_key(cd["el"])
        state = cube_states.get(key)
        if state and not state["queued"]:
          state["queued"] = True
          process_queue(cd["el"])

    window.requestAnimationFrame(create_proxy(frame))

  window.setInterval(create_proxy(auto_rotate), 1500)

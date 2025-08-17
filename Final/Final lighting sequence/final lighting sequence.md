# 🏆 Final Sequence

As our Cadets face their final mission, Sector 536 also reaches the end of its journey. That is when 5 of our Agents from 4 teams present to you the Final Sequence. In this *Final Sequence, you will witness a **Handmade Rocket* built entirely from cardboard, wrapped in glowing *NeoPixels, brought to life with synchronized **lighting sequences* and *immersive audio. *Captain Chromaflex will have the honour to launch our *Handmade Rocket* to send us back to NYP. Here are the different elements that brought our *Final Sequence* to life.

- 🚀 [Hardware - Handmade Rocket](https://github.com/Nixx-Goh/EGL314-Project-Lumen-Team-D/blob/17852345f5a77e5acf652ab93767567bcbd8fb79/Final%20Sequence/README.md)
- 💡 [Neopixels](https://github.com/timsjt/EGL314_TEAMB/blob/main/Final%20Sequence-Neopixels/setup.md)
- ✨ [Lighting Sequences](https://github.com/YHLeong/EGL314_TeamC/tree/main/Final/Final%20lighting%20sequence/final%20lighting%20sequence.md)
- 🎶 [Immersive Audio + Button](https://github.com/Kean-en/TeamA-Egl314/tree/9e6a83c4c6c1ec6db7fd967705fbe311cad5f8f9/Code/Final%20Sequence/Final_button.md)

In this repository, we will be focusing on ✨ *Lighting Sequences*.
# Final Lighting Sequence

### System Overview

All lighting sequences are controlled from the **`GUI.py`** interface.
The GUI communicates with the **Master Server Raspberry Pi** over the local network using **OSC (Open Sound Control)** messages sent to the GrandMA3 command endpoint.

* Network target for lighting: `GMA_IP = "192.168.254.213"`, `GMA_PORT = 2000`.
* OSC client used in code: `udp_client.SimpleUDPClient(GMA_IP, GMA_PORT)`.
* Lighting commands are sent via `trigger_gma(command)`, which transmits to the GrandMA3 command address: `/gma3/cmd`.
* Relevant button mappings in `GUI.py` (Lighting tab → `gma_cues`):

  * **End Sequence** → `Go sequence 13 cue 1`
  * **End Transition** → `Go sequence 83 cue 1`
  * **End buttons** → `Go sequence 83 cue+`

This lets operators fire cues from the GUI without touching the desk: pressing a button sends an OSC command to the Master Pi, which relays it to **GrandMA3**.

---

### Design Concept

The lighting design adopts a **galaxy-inspired palette** of **blue, pink, and purple**.

To maintain audience focus on the **rocket** and the **NeoPixel display**, no complex patterns or distracting effects are used.

The intention is to create a clean, immersive atmosphere while guiding attention to key stage elements.

**Implementation Note:**
All of the cues below can be triggered directly from the **`GUI.py`** file.

---

## Sequence 13 – Finale

* Serves as the **closing sequence** of the experience.

* **Trigger Command:**
  `trigger_gma("Go sequence 13 cue 1")`

---

## Sequence 83 – Build-Up & Engagement

* **Cue 1 – Overall Lighting**
  Full-stage wash in galaxy colors to establish mood, while still maintaining the room to be well lit enough for placement of chairs.

  **Trigger Command:**
  `trigger_gma("Go sequence 83 cue 1")`

* **Cue 2 – Button Focus**
  Concentrated lighting highlighting the button to draw the audience's attention.

  **Trigger Command:**
  `trigger_gma("Go sequence 83 cue+")`

* **Cue 3 – Tension Build ("ARE YOU READY")**
  Accent lighting sequence designed to create anticipation before the game begins.

  **Trigger Command:**
  `trigger_gma("Go sequence 83 cue+")`

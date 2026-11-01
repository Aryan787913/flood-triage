flood-triage demo, voiceover script for ElevenLabs (~410 words, ~2:50 at a calm pace)

[0:00 to 0:20, PROBLEM]
Every monsoon, Indian cities ask citizens to send flood photos. Gurugram's flood portal even asks people to guess the water depth themselves. That means hundreds of photos and guesses, and someone has to decide which street needs help first.

[0:20 to 0:35, WHAT IT IS]
This is flood-triage. It reads each photo using Meta's open-weight model, Muse Spark Open, and ranks the reports worst first, so an officer sees the deepest water at the top.

[0:35 to 1:10, LIVE DEMO: ONE PHOTO]
Here's a report. Instead of guessing centimetres, it judges the water against the car itself: below the tyre, up to the door, or above the windows. Levels zero to four. It shows its evidence: where it found the vehicle and where the waterline touches it. And when a photo is too dark, blurry or has no vehicle, it says can't tell and sends it to a person, instead of guessing.

[1:10 to 1:40, LIVE DEMO: QUEUE AND AGENT]
Now the whole queue. Reports are sorted by severity and shown on a map. The agent also checks each citizen's own depth estimate against the photo, flags the ones that don't match, spots possible duplicates, and drafts a short note for the ward officer. The officer stays in charge. This is a triage hint, not a warning.

[1:40 to 2:20, RESULTS]
We tested it on 340 held-out photos from a public flooded-car dataset, tuning only on the validation set and scoring the test set once. A standard image classifier scored 0.619 macro F1. Our hybrid, where the classifier handles easy photos and Spark decides the uncertain ones, scored 0.647. More importantly, it cut the dangerous mistakes, being off by two levels or more, from 29 to 17. Spark on its own makes even fewer of those, but it tends to call water one level lower than it is.

[2:20 to 2:45, HONESTY AND OPEN WEIGHTS]
It doesn't measure depth in centimetres, vehicle sizes vary, and it was mostly tested on car photos. We also found the dataset's official split reuses the same source photos, and we report that openly. Because Spark is open weight, a city can run it on its own servers and keep citizens' photos private.

[2:45 to 2:55, CLOSE]
flood-triage. Built during the hackathon, code and results on GitHub. Thanks for watching.

ElevenLabs tips: calm, clear English voice (Indian English fits), stability ~50%, speed 1.0. Export MP3 and send it to Hark; the video gets timed to your audio, with captions from this script.

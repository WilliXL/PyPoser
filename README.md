# PyPoser!

A Probability-Driven Music Composer Written in Python

Created for Carnegie Mellon University's F16 15-112 Term Project.

[Watch the video demo submitted for the course](https://www.youtube.com/watch?v=zIM6WJvDo3k&t=20s)

## Getting Started

### External Libraries
- [PySynth](https://mdoege.github.io/PySynth/) - For generating the music
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) - For playing music
- [PyDub](http://pydub.com/) - For wrapping PyAudio so that it can create a WAV overlay for playing two WAV files at the same time

The three libraries are easily installed with pip. Once the three libraries are installed (make sure that PyDub is installed after PyAudio as it is a dependency) the program should be ready to run.
```
pip install pysynth
```
```
pip install pyaudio
```
```
pip install pydub
```

### Other Dependencies
I also use the MonkeyLearn API for its Machine Learning Algorithm. The raw data that I use for training the algorithm can be found in SongClassificationData.xlsx

## Contributing
Email [William](mailto:wxl@andrew.cmu.edu) if you would like to contribute.
Currently working on creating a better GUI as well as being able to generate sheet music that corresponds to the generated music.

## Acknowledgements
15-112. Difficult course. 10/10 would flunk it again

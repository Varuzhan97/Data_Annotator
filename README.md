# Data Annotator

This Python program simply shows a normalized sentence that must be annotated, and 3 buttons: 
  * The “Repeat” button gives the ability to record the current sentence (phrase or word) again, 
  * the “Invalid” button marks the current sentence as invalid and removes it from the sentences list. This button can be used when the sentence is not valid (e.g. grammatically incorrect words),
  * the “Next” button marks the current sentence as valid, includes transcript, recorde audio file size (in bytes) and recorded audio clip (in WAV format) in corpora and loads the next sentence for annotation.

The annotation program use voice activity detection technology to detect speech by simply distinguishing between silence and speech. This is done by using Python free “webrtcvad” module, which is a python interface to the WebRTC Voice Activity Detector (VAD) developed by Google. The application determines voice activity by a ratio of not null and null frames in 300 milliseconds. 
![alt text](https://github.com/Varuzhan97/Data_Annotator/blob/main/VAD.png)
The portion of not null frames in given milliseconds must be equal to or greater than 75%. By using voice activity detection technology recording starts when the speaker starts the speech and ends when the speaker ends the speech. This prevents including leading and trailing parts in the recorded audio clips. Leading and trailing parts in the audio clips are usually removed to counter the fact that an automated speech recognition system will recognise any sound-phoneme combination which will make background noise (even if very low) and lead to an incorrect result.
![alt text](https://github.com/Varuzhan97/Data_Annotator/blob/main/interface.png)

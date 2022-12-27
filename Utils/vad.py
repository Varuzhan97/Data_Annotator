import os, collections, queue
import numpy as np
import pyaudio
import webrtcvad
import wave

buffer_queue = queue.Queue()

def proxy_callback(in_data, frame_count, time_info, status):
    #pylint: disable=unused-argument
    buffer_queue.put(in_data)
    return (None, pyaudio.paContinue)

def write_wav(filename, data):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(data)
    wf.close()

def vad_collector(AGGRESSIVENESS, BLOCK_SIZE, RATE_PROCESS, padding_ms=300, ratio=0.75):
    """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
        Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
        Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                  |---utterence---|        |---utterence---|
    """
    vad = webrtcvad.Vad(AGGRESSIVENESS)

    num_padding_frames = padding_ms // (1000 * BLOCK_SIZE // RATE_PROCESS)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False

    while 1:
        frame = buffer_queue.get()
        if len(frame) < 640:
            return
        is_speech = vad.is_speech(frame, RATE_PROCESS)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > ratio * ring_buffer.maxlen:
                triggered = True
                for f, s in ring_buffer:
                    yield f
                ring_buffer.clear()
        else:
            yield frame
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > ratio * ring_buffer.maxlen:
                triggered = False
                yield None
                ring_buffer.clear()

def listen_audio(anim_event, save_wav_path):
    #Make PyAudio
    FORMAT = pyaudio.paInt16
    RATE_PROCESS = 16000
    CHANNELS = 1
    BLOCKS_PER_SECOND = 50
    AGGRESSIVENESS = 3
    BLOCK_SIZE = int(RATE_PROCESS / float(BLOCKS_PER_SECOND))
    BLOCK_SIZE_INPUT = int(RATE_PROCESS / float(BLOCKS_PER_SECOND))

    kwargs = {
        'format': FORMAT,
        'channels': CHANNELS,
        'rate': RATE_PROCESS,
        'input': True,
        'frames_per_buffer': BLOCK_SIZE_INPUT,
        'stream_callback': proxy_callback,
    }

    # Stream from microphone to STT using VAD

    pa = pyaudio.PyAudio()
    stream = pa.open(**kwargs)
    stream.start_stream()

    wav_data = bytearray()

    i = 0

    for frame in vad_collector(AGGRESSIVENESS, BLOCK_SIZE, RATE_PROCESS):
        if frame is not None:
            anim_event.set()

            wav_data.extend(frame)
        else:
            anim_event.clear()

            file_name = os.path.join(save_wav_path, str(i) + ".wav")
            write_wav(file_name, wav_data)
            wav_data = bytearray()

            #pause_stream
            stream.stop_stream()
            yield file_name

            i+=1
            #start stream
            stream.start_stream()

    stream.stop_stream()
    stream.close()
    pa.terminate()

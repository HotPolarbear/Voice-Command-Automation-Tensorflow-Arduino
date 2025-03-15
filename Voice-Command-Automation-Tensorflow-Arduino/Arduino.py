import serial.tools.list_ports
import sounddevice as sd
import wave
import tensorflow as tf
import numpy as np
import time

ports=serial.tools.list_ports.comports()
serialInst=serial.Serial()
labels=['eight', 'five', 'four', 'nine', 'one', 'seven', 'six', 'three','two', 'zero']




def record_audio(file_name, duration, sample_rate=16000):
    print(f"Recording for {duration} seconds...")
    
    # Record audio
    print("Recording Audio")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    print("Recording complete.")
    
    # Save the recorded audio as output to a .wav file
    with wave.open(file_name, 'wb') as wf:
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    
    print(f"Audio saved as {file_name}.")
    
def mono_16k(path):
    file_contents = tf.io.read_file(path)
    wav ,sample_rate = tf.audio.decode_wav(file_contents, desired_channels = 1)
    wav = tf.squeeze(wav, axis = -1)
    sample_rate = tf.cast(sample_rate, dtype= tf.int64)
    #wav = tfio.audio.resample(wav, rate_in = sample_rate, rate_out = 16000)
    return wav    
   
def make_spectrogram(wav, sample_rate=16000):
    # Compute STFT
    stft = tf.signal.stft(wav, frame_length=512, frame_step=256, fft_length=512)
    spectrogram = tf.abs(stft)  # Convert to magnitude

    # Convert to Mel Spectrogram (128 Mel bins)
    num_mel_bins = 128
    num_spectrogram_bins = tf.shape(spectrogram)[-1]

    # Compute Mel filterbank
    mel_filterbank = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins=num_mel_bins,
        num_spectrogram_bins=num_spectrogram_bins,
        sample_rate=sample_rate,
        lower_edge_hertz=80.0,
        upper_edge_hertz=7600.0
    )

    # Apply Mel filter
    mel_spectrogram = tf.tensordot(spectrogram, tf.cast(mel_filterbank, dtype=tf.float32), axes=(-1, 0))

    mel_spectrogram = tf.expand_dims(mel_spectrogram, axis=-1)  # Shape: (Time, Freq, 1)

    mel_spectrogram = tf.image.resize(mel_spectrogram, (128, 128))

    return mel_spectrogram




for one in ports:
    print(str(one))
    

serialInst.baudrate=9600
serialInst.port='/dev/cu.usbmodem1301'
serialInst.open()

output_file = "output.wav"
record_duration = 1  # Duration in seconds

while True:
    
    record_audio(output_file, record_duration)
    path='output.wav'
    wav=mono_16k(path)
    spectogram=make_spectrogram(wav)
    
    model=tf.keras.models.load_model('/Users/hotpolarbear/Documents/Programs/Projects/Voice Automation/Voice-Command-Automation-Tensorflow-Arduino/VCA_6M_9336.keras')
    spectogram = spectogram[tf.newaxis,...]
    prediction=model.predict(spectogram)
    
    print(max(prediction[0]))
    index = (((np.where(prediction[0] == max(prediction[0]) ))[0])[0])
    output=labels[index]
    print(output)
    if output == 'zero':
        break
    serialInst.write(output.encode('utf-8'))
    time.sleep(5)
    
    


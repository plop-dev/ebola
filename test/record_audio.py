import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    if p.get_device_info_by_host_api_device_index(0, i).get('name') == 'Microphone (Realtek(R) Audio)':
        print(i)
        break
else:
    print('device not found')

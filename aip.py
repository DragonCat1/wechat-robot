from aip.speech import AipSpeech

appId = '10749810'
apiKey='cxIvL8MP2PBVArtcLCYXZNdC'
secret = '6ef14e35f5376de5fa8b3377ccd7c4bb'


# def get_file_content(filePath):
#     with open(filePath, 'rb') as fp:
#         return fp.read()
aipSpeech = AipSpeech(appId,apiKey,secret)
vioceFile = open('vioce/180125-230730.wav','rb')
vioce = vioceFile.read()
result = aipSpeech.asr(vioce,'pcm')
print(result)
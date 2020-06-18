def initializeWaveRNN():
	import torch
	from localimport import localimport
	from TTS.utils.audio import AudioProcessor
	from TTS.utils.generic_utils import load_config, setup_model
	from TTS.utils.synthesis import synthesis
	
	use_cuda = True
	batched_wavernn = True
	#path_to_WaveRNN = "/content/WaveRNN"
	wavernn_pretrained_model = 'wavernn_models/checkpoint_433000.pth.tar'
	wavernn_pretrained_model_config = 'wavernn_models/config.json'
	tts_pretrained_model = 'tts_models/checkpoint_261000.pth.tar'
	tts_pretrained_model_config = 'tts_models/config.json'
	CONFIG = load_config(tts_pretrained_model_config)
	from TTS.utils.text.symbols import symbols, phonemes
	num_chars = len(phonemes) if CONFIG.use_phonemes else len(symbols)
	model = setup_model(num_chars, CONFIG)
	audioprocessor = AudioProcessor(**CONFIG.audio)
	cp = torch.load(tts_pretrained_model)
	model.load_state_dict(cp['model'])
	model.cuda()
	model.eval()
	model.decoder.max_decoder_steps = 2000
	VOCODER_CONFIG = load_config(wavernn_pretrained_model_config)
	#with localimport(path_to_WaveRNN) as _importer:
	from WaveRNN.models.wavernn import Model
	bits = 10
	wavernn = Model(
		rnn_dims=512,
		fc_dims=512,
		mode="mold",
		pad=2,
		upsample_factors=VOCODER_CONFIG.upsample_factors,
		feat_dims=VOCODER_CONFIG.audio["num_mels"],
		compute_dims=128,
		res_out_dims=128,
		res_blocks=10,
		hop_length=audioprocessor.hop_length,
		sample_rate=audioprocessor.sample_rate,
	).cuda()
	check = torch.load(wavernn_pretrained_model)
	wavernn.load_state_dict(check['model'])
	wavernn.cuda()
	wavernn.eval()
	TTS_Libraries = { "torch": torch, "model" : model, "config" : CONFIG, "use_cuda" : use_cuda, "audioprocessor" : audioprocessor, "synthesis" : synthesis, "wavernn" : wavernn, "batched_wavernn" : batched_wavernn }
	return TTS_Libraries

def textToSpeech(text,Library,use_gl=False):#text,torch,model,CONFIG,use_cuda,audioprocessor,synthesis,wavernn,batched_wavernn,use_gl=False):
	torch = Library["torch"]
	model = Library["model"]
	CONFIG = Library["config"]
	use_cuda = Library["use_cuda"]
	audioprocessor = Library["audioprocessor"]
	synthesis = Library["synthesis"]
	wavernn = Library["wavernn"]
	batched_wavernn = Library["batched_wavernn"]
	import sys
	sys_main_stream = sys.stdout
	sys.stdout = open("log.txt","w");
	waveform, alignment, mel_spec, mel_postnet_spec, stop_tokens = synthesis(model, text, CONFIG, use_cuda, audioprocessor, truncated=True, enable_eos_bos_chars=CONFIG.enable_eos_bos_chars)
	if CONFIG.model == "Tacotron" and not use_gl:
		mel_postnet_spec = audioprocessor.out_linear_to_mel(mel_postnet_spec.T).T
	if not use_gl:
		waveform = wavernn.generate(torch.FloatTensor(mel_postnet_spec.T).unsqueeze(0).cuda(), batched=batched_wavernn, target=11000, overlap=550)
	sys.stdout.close()
	sys.stdout = sys_main_stream
	return waveform

if __name__=="__main__":
	print("This Module is not developed for stand alone use!...")
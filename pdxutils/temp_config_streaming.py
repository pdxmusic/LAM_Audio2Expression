
weight = 'pretrained_models/lam_audio2exp_streaming.tar'
ex_vol = True
audio_input = 'assets/sample_audio/HillaryClinton_english.wav'
save_json_path = 'temp_lam_output.json'

audio_sr = 16000
fps = 30.0

movement_smooth = False
brow_movement = False
id_idx = 0

resume = False
evaluate = True
test_only = False

seed = None
save_path = "exp/audio2exp"
num_worker = 16
batch_size = 16
batch_size_val = None
batch_size_test = None
epoch = 100
eval_epoch = 100

sync_bn = False
enable_amp = False
empty_cache = False
find_unused_parameters = False

# ... rest of config stays same
momentum = 0.9
weight_decay = 0.0001
log_every = 10
checkpoint_every = 10
test_every = 30
test_at_start = True
do_ema = False
ema_decay = 0.999
warmup = True
load_weight_only = True

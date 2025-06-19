#!/usr/bin/env python3
"""
Complete pipeline to generate blendshapes from audio in the expected format.
This script combines the LAM_Audio2Expression inference with format conversion.
"""

import os
import json
import subprocess
import argparse
import sys
import tempfile

def generate_blendshapes_complete_pipeline(audio_path, output_path, cleanup_intermediate=True):
    """
    Complete pipeline to generate blendshapes from audio
    
    Steps:
    1. Run LAM_Audio2Expression inference
    2. Convert output to expected format
    3. Clean up intermediate files
    
    Args:
        audio_path: Path to input audio file
        output_path: Path to output JSON file in expected format
        cleanup_intermediate: Whether to remove intermediate LAM output file
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        # Step 1: Generate temporary config file
        temp_config = "temp_config_streaming.py"
        config_content = f'''
weight = 'pretrained_models/lam_audio2exp_streaming.tar'
ex_vol = True
audio_input = '{audio_path}'
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
'''
        
        # Write temporary config
        with open(temp_config, 'w') as f:
            f.write(config_content)
        
        print(f"🎵 Processing audio: {audio_path}")
        print(f"⚙️  Using LAM_Audio2Expression model...")
        
        # Step 2: Run LAM inference
        # Modify the streaming config temporarily
        original_config = "configs/lam_audio2exp_config_streaming.py"
        backup_config = original_config + ".backup"
        
        # Backup original config
        subprocess.run(["cp", original_config, backup_config], check=True)
        
        # Update config with our audio path
        config_update = f'''
weight = 'pretrained_models/lam_audio2exp_streaming.tar'
ex_vol = True
audio_input = '{audio_path}'
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
'''
        
        with open(original_config, 'w') as f:
            f.write(config_update)
        
        # Run LAM inference
        result = subprocess.run(
            ["python", "inference_streaming_audio.py"],
            capture_output=True,
            text=True
        )
        
        # Restore original config
        subprocess.run(["mv", backup_config, original_config], check=True)
        
        if result.returncode != 0:
            print(f"❌ LAM inference failed: {result.stderr}")
            return False
        
        # Check if LAM output was created
        lam_output = "temp_lam_output.json"
        if not os.path.exists(lam_output):
            print(f"❌ LAM output file not found: {lam_output}")
            return False
        
        print(f"✅ LAM inference completed")
        
        # Step 3: Convert to expected format
        print(f"🔄 Converting to expected format...")
        
        # Load LAM output
        with open(lam_output, 'r') as f:
            lam_data = json.load(f)
        
        # Convert to expected format
        names = lam_data['names']
        frames = lam_data['frames']
        
        values = []
        for frame in frames:
            values.append(frame['weights'])
        
        expected_data = {
            "names": names,
            "values": values
        }
        
        # Save output
        with open(output_path, 'w') as f:
            json.dump(expected_data, f, indent=2)
        
        print(f"✅ Successfully generated blendshapes!")
        print(f"📁 Output: {output_path}")
        print(f"📊 Format: {len(values)} frames × {len(names)} blendshapes")
        print(f"⏱️  Duration: {len(values)/30:.2f} seconds @ 30 FPS")
        
        # Cleanup
        if cleanup_intermediate:
            for temp_file in [lam_output, temp_config]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            print(f"🧹 Cleaned up intermediate files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate blendshapes from audio using LAM_Audio2Expression')
    parser.add_argument('audio_path', help='Path to input audio file')
    parser.add_argument('output_path', help='Path to output JSON file')
    parser.add_argument('--keep-intermediate', action='store_true', 
                       help='Keep intermediate LAM output files')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.audio_path):
        print(f"❌ Audio file not found: {args.audio_path}")
        sys.exit(1)
    
    # Generate blendshapes
    success = generate_blendshapes_complete_pipeline(
        args.audio_path,
        args.output_path,
        cleanup_intermediate=not args.keep_intermediate
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

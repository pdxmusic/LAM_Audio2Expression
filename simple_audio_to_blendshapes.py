#!/usr/bin/env python3
"""
Simple script to generate blendshapes from audio using LAM_Audio2Expression.
This uses the working approach we've tested.
"""

import os
import json
import subprocess
import argparse
import sys
import shutil

def generate_blendshapes_simple(audio_path, output_path):
    """
    Generate blendshapes using the simple working approach
    """
    
    try:
        print(f"🎵 Processing audio: {audio_path}")
        
        # Step 1: Backup and modify the streaming config
        config_file = "configs/lam_audio2exp_config_streaming.py"
        backup_file = config_file + ".backup"
        
        # Create backup
        shutil.copy2(config_file, backup_file)
        
        # Read current config
        with open(config_file, 'r') as f:
            config_content = f.read()
        
        # Update audio_input and save_json_path
        updated_content = config_content.replace(
            "audio_input = './assets/sample_audio/BarackObama_english.wav'",
            f"audio_input = '{audio_path}'"
        ).replace(
            "save_json_path = 'bsData.json'",
            "save_json_path = 'temp_output.json'"
        )
        
        # Write updated config
        with open(config_file, 'w') as f:
            f.write(updated_content)
        
        print(f"⚙️  Running LAM_Audio2Expression...")
        
        # Step 2: Run inference
        result = subprocess.run(
            ["python", "inference_streaming_audio.py"],
            capture_output=True,
            text=True
        )
        
        # Restore original config
        shutil.move(backup_file, config_file)
        
        if result.returncode != 0:
            print(f"❌ Inference failed: {result.stderr}")
            return False
        
        # Step 3: Check output and convert
        temp_output = "temp_output.json"
        if not os.path.exists(temp_output):
            print(f"❌ Output file not found: {temp_output}")
            return False
        
        print(f"🔄 Converting to expected format...")
        
        # Load and convert
        with open(temp_output, 'r') as f:
            lam_data = json.load(f)
        
        # Convert to expected format (CORRECT structure)
        names = lam_data['names']
        frames = lam_data['frames']
        
        # Define the expected blendshape order (from reference file)
        expected_blendshapes = [
            "eyeBlinkLeft", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft", 
            "eyeLookUpLeft", "eyeSquintLeft", "eyeWideLeft", "eyeBlinkRight", 
            "eyeLookDownRight", "eyeLookInRight", "eyeLookOutRight", "eyeLookUpRight", 
            "eyeSquintRight", "eyeWideRight", "jawForward", "jawLeft", "jawRight", 
            "jawOpen", "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft", 
            "mouthRight", "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", 
            "mouthFrownRight", "mouthDimpleLeft", "mouthDimpleRight", "mouthStretchLeft", 
            "mouthStretchRight", "mouthRollLower", "mouthRollUpper", "mouthShrugLower", 
            "mouthShrugUpper", "mouthPressLeft", "mouthPressRight", "mouthLowerDownLeft", 
            "mouthLowerDownRight", "mouthUpperUpLeft", "mouthUpperUpRight", "browDownLeft", 
            "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight", 
            "cheekPuff", "cheekSquintLeft", "cheekSquintRight", "noseSneerLeft", 
            "noseSneerRight", "tongueOut", "headRoll", "leftEyeRoll", "rightEyeRoll"
        ]
        
        # Create mapping from LAM names to indices
        lam_name_to_index = {name: i for i, name in enumerate(names)}
        
        # Convert to correct expected format (array of objects with time and blendshapes)
        result = []
        
        for frame in frames:
            weights = frame['weights']
            time = frame['time']
            
            # Create blendshapes object
            blendshapes = {}
            
            for blend_name in expected_blendshapes:
                if blend_name in lam_name_to_index:
                    # Use LAM value, rounded to 2 decimals
                    lam_index = lam_name_to_index[blend_name]
                    blendshapes[blend_name] = round(weights[lam_index], 2)
                else:
                    # Default to 0 for missing blendshapes (like headRoll, leftEyeRoll, rightEyeRoll)
                    blendshapes[blend_name] = 0.0
            
            # Add frame to result
            frame_data = {
                "time": round(time, 4),  # Round time to 4 decimals for precision
                "blendshapes": blendshapes
            }
            result.append(frame_data)
        
        # Save output in correct format
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Cleanup
        os.remove(temp_output)
        
        print(f"✅ Successfully generated blendshapes!")
        print(f"📁 Output: {output_path}")
        print(f"📊 Format: Array of {len(result)} frame objects")
        print(f"🎯 Blendshapes per frame: {len(expected_blendshapes)}")
        print(f"⏱️  Duration: {result[-1]['time']:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Try to restore config if something went wrong
        if os.path.exists(backup_file):
            shutil.move(backup_file, config_file)
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate blendshapes from audio')
    parser.add_argument('audio_path', help='Path to input audio file')
    parser.add_argument('output_path', help='Path to output JSON file')
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.audio_path):
        print(f"❌ Audio file not found: {args.audio_path}")
        sys.exit(1)
    
    # Generate blendshapes
    success = generate_blendshapes_simple(args.audio_path, args.output_path)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

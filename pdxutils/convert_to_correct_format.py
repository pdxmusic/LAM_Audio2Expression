#!/usr/bin/env python3
"""
Script to convert LAM_Audio2Expression output to the CORRECT expected format.
The expected format is an array of objects with time and blendshapes properties.
"""

import json
import argparse
import sys

def convert_lam_to_correct_format(input_file, output_file):
    """
    Convert LAM output format to the CORRECT expected format
    
    LAM format:
    {
        "names": ["browDownLeft", ...],
        "metadata": {...},
        "frames": [
            {"weights": [0.1, 0.2, ...], "time": 0.033, "rotation": [...]},
            ...
        ]
    }
    
    CORRECT Expected format:
    [
        {
            "time": 0,
            "blendshapes": {
                "eyeBlinkLeft": 0,
                "eyeLookDownLeft": 0,
                ...
                "headRoll": 0,
                "leftEyeRoll": 0,
                "rightEyeRoll": 0
            }
        },
        {
            "time": 0.0167,
            "blendshapes": {
                "eyeBlinkLeft": 0.05,
                ...
            }
        }
    ]
    """
    
    try:
        # Load LAM output
        with open(input_file, 'r') as f:
            lam_data = json.load(f)
        
        # Extract names and frames
        names = lam_data['names']
        frames = lam_data['frames']
        
        # Define the expected blendshape order (from your reference file)
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
        
        # Convert to expected format
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
        
        # Save to output file
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✅ Successfully converted {len(result)} frames")
        print(f"📁 Output saved to: {output_file}")
        print(f"📊 Format: Array of {len(result)} frame objects")
        print(f"🎯 Blendshapes per frame: {len(expected_blendshapes)}")
        print(f"⏱️  Duration: {result[-1]['time']:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert LAM blendshapes to CORRECT expected format')
    parser.add_argument('input_file', help='Input LAM JSON file')
    parser.add_argument('output_file', help='Output JSON file in correct expected format')
    
    args = parser.parse_args()
    
    success = convert_lam_to_correct_format(args.input_file, args.output_file)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

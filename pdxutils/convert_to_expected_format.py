#!/usr/bin/env python3
"""
Script to convert LAM_Audio2Expression output to the expected blendshapes format.
Converts from the native LAM format to the format expected in blendshapes-700x9.json
"""

import json
import argparse
import sys

def convert_lam_to_expected_format(input_file, output_file):
    """
    Convert LAM output format to expected format
    
    LAM format:
    {
        "names": ["browDownLeft", ...],
        "metadata": {...},
        "frames": [
            {"weights": [0.1, 0.2, ...], "time": 0.033, "rotation": [...]},
            ...
        ]
    }
    
    Expected format:
    {
        "names": ["browDownLeft", ...],
        "values": [
            [0.1, 0.2, ...],  # frame 1
            [0.15, 0.25, ...], # frame 2
            ...
        ]
    }
    """
    
    try:
        # Load LAM output
        with open(input_file, 'r') as f:
            lam_data = json.load(f)
        
        # Extract names and values
        names = lam_data['names']
        frames = lam_data['frames']
        
        # Convert frames to values array
        values = []
        for frame in frames:
            values.append(frame['weights'])
        
        # Create expected format
        expected_data = {
            "names": names,
            "values": values
        }
        
        # Save to output file
        with open(output_file, 'w') as f:
            json.dump(expected_data, f, indent=2)
        
        print(f"✅ Successfully converted {len(frames)} frames with {len(names)} blendshapes")
        print(f"📁 Output saved to: {output_file}")
        print(f"📊 Format: {len(values)} frames × {len(names)} blendshapes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert LAM blendshapes to expected format')
    parser.add_argument('input_file', help='Input LAM JSON file')
    parser.add_argument('output_file', help='Output JSON file in expected format')
    
    args = parser.parse_args()
    
    success = convert_lam_to_expected_format(args.input_file, args.output_file)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

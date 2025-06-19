#!/usr/bin/env python3
"""
Example usage of the blendshapes generation script.
This demonstrates how to generate blendshapes from audio files using the LAM_Audio2Expression model.
"""

import os
from generate_blendshapes import generate_blendshapes_from_audio

def main():
    # Example 1: Generate blendshapes from Barack Obama sample
    print("=== Example 1: Barack Obama Audio ===")
    audio_path = "./assets/sample_audio/BarackObama_english.wav"
    output_path = "./output_blendshapes_obama.json"
    
    if os.path.exists(audio_path):
        success = generate_blendshapes_from_audio(
            audio_path=audio_path,
            output_path=output_path,
            id_idx=153,  # Default identity
            fps=30.0     # 30 FPS like your reference file
        )
        
        if success:
            print(f"✅ Successfully generated blendshapes: {output_path}")
        else:
            print("❌ Failed to generate blendshapes")
    else:
        print(f"❌ Audio file not found: {audio_path}")
    
    print()
    
    # Example 2: Generate blendshapes from Hillary Clinton sample  
    print("=== Example 2: Hillary Clinton Audio ===")
    audio_path = "./assets/sample_audio/HillaryClinton_english.wav"
    output_path = "./output_blendshapes_hillary.json"
    
    if os.path.exists(audio_path):
        success = generate_blendshapes_from_audio(
            audio_path=audio_path,
            output_path=output_path,
            id_idx=153,
            fps=30.0
        )
        
        if success:
            print(f"✅ Successfully generated blendshapes: {output_path}")
        else:
            print("❌ Failed to generate blendshapes")
    else:
        print(f"❌ Audio file not found: {audio_path}")
    
    print()
    
    # Example 3: Custom audio file (you can replace this with your own)
    print("=== Example 3: Custom Audio File ===")
    print("To use your own audio file, call:")
    print("python generate_blendshapes.py /path/to/your/audio.wav /path/to/output.json")
    print()
    print("Or use the function directly:")
    print("""
success = generate_blendshapes_from_audio(
    audio_path="/path/to/your/audio.wav",
    output_path="/path/to/output_blendshapes.json",
    id_idx=153,
    fps=30.0
)
""")

if __name__ == "__main__":
    main()

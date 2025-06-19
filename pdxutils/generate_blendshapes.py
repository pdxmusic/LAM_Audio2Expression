#!/usr/bin/env python3
"""
Script to generate blendshapes from audio file in the exact format expected.
This script uses the LAM_Audio2Expression model to convert audio to ARKit blendshapes
and exports them in the same format as your reference blendshapes-700x9.json file.
"""

import os
import json
import numpy as np
import librosa
import torch
import torch.nn.functional as F
from typing import Dict, List

from engines.defaults import default_config_parser, default_setup
from engines.infer import INFER
from models.utils import ARKitBlendShape


def generate_blendshapes_from_audio(
    audio_path: str,
    output_path: str,
    config_path: str = 'configs/lam_audio2exp_config_streaming.py',
    id_idx: int = 0,
    fps: float = 30.0
) -> bool:
    """
    Generate blendshapes from audio file and save in the expected JSON format.
    
    Args:
        audio_path: Path to input audio file
        output_path: Path to output JSON file
        config_path: Path to model configuration file
        id_idx: Identity index for the model
        fps: Frames per second for the output
        
    Returns:
        bool: True if successful, False otherwise
    """
    
    try:
        # Load configuration
        print(f"Loading configuration from {config_path}...")
        cfg = default_config_parser(config_path, [])
        
        # Override audio input and other settings
        cfg.audio_input = audio_path
        cfg.id_idx = id_idx
        cfg.fps = fps
        cfg.save_json_path = None  # We'll handle JSON export ourselves
        
        # Setup and build model
        print("Setting up model...")
        cfg = default_setup(cfg)
        infer = INFER.build(dict(type=cfg.infer.type, cfg=cfg))
        infer.model.eval()
        
        # Load and process audio
        print(f"Loading audio from {audio_path}...")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        speech_array, ssr = librosa.load(audio_path, sr=16000)
        
        # Run inference
        print("Running inference...")
        with torch.no_grad():
            input_dict = {}
            input_dict['id_idx'] = F.one_hot(
                torch.tensor(cfg.id_idx),
                cfg.model.backbone.num_identity_classes
            ).cuda(non_blocking=True)[None, ...]
            input_dict['input_audio_array'] = torch.FloatTensor(speech_array).cuda(non_blocking=True)[None, ...]
            
            output_dict = infer.model(input_dict)
            
        # Get expression output
        out_exp = output_dict['pred_exp'].squeeze().cpu().numpy()
        
        # Apply post-processing (same as in the original inference)
        import math
        frame_length = math.ceil(speech_array.shape[0] / ssr * fps)
        volume = librosa.feature.rms(
            y=speech_array, 
            frame_length=int(1 / fps * ssr), 
            hop_length=int(1 / fps * ssr)
        )[0]
        
        if volume.shape[0] > frame_length:
            volume = volume[:frame_length]
            
        # Apply smoothing and other post-processing
        if cfg.movement_smooth:
            from models.utils import smooth_mouth_movements
            out_exp = smooth_mouth_movements(out_exp, 0, volume)
            
        if cfg.brow_movement:
            from models.utils import apply_random_brow_movement
            out_exp = apply_random_brow_movement(out_exp, volume)
            
        # Apply final blendshape post-processing
        pred_exp = infer.blendshape_postprocess(out_exp)
        
        # Convert to the expected JSON format
        print("Converting to expected JSON format...")
        json_data = convert_to_expected_format(pred_exp, fps)
        
        # Save to file
        print(f"Saving blendshapes to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
            
        print(f"Successfully generated {len(json_data)} frames of blendshapes!")
        print(f"Output saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error generating blendshapes: {str(e)}")
        return False


def convert_to_expected_format(blendshape_weights: np.ndarray, fps: float) -> List[Dict]:
    """
    Convert blendshape weights to the expected JSON format (same as your reference file).
    
    Args:
        blendshape_weights: Array of shape (num_frames, 52) containing blendshape weights
        fps: Frames per second
        
    Returns:
        List of dictionaries in the expected format
    """
    
    # ARKit blendshape names in the order expected by your format
    # This matches the order in your reference file
    expected_blendshape_names = [
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
    
    # Create mapping from ARKitBlendShape to expected format
    arkit_to_expected = {}
    for i, arkit_name in enumerate(ARKitBlendShape):
        if arkit_name in expected_blendshape_names:
            expected_idx = expected_blendshape_names.index(arkit_name)
            arkit_to_expected[i] = expected_idx
    
    # Convert to expected format
    json_data = []
    num_frames = blendshape_weights.shape[0]
    
    for frame_idx in range(num_frames):
        # Initialize blendshapes dict with zeros
        blendshapes = {name: 0.0 for name in expected_blendshape_names}
        
        # Map ARKit blendshapes to expected format
        for arkit_idx, expected_idx in arkit_to_expected.items():
            expected_name = expected_blendshape_names[expected_idx]
            blendshapes[expected_name] = float(blendshape_weights[frame_idx, arkit_idx])
        
        # Create frame data
        frame_data = {
            "time": frame_idx / fps,
            "blendshapes": blendshapes
        }
        
        json_data.append(frame_data)
    
    return json_data


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate blendshapes from audio file')
    parser.add_argument('audio_path', help='Path to input audio file')
    parser.add_argument('output_path', help='Path to output JSON file')
    parser.add_argument('--config', default='configs/lam_audio2exp_config.py', 
                       help='Path to model configuration file')
    parser.add_argument('--id_idx', type=int, default=153, 
                       help='Identity index for the model')
    parser.add_argument('--fps', type=float, default=30.0, 
                       help='Frames per second for output')
    
    args = parser.parse_args()
    
    success = generate_blendshapes_from_audio(
        audio_path=args.audio_path,
        output_path=args.output_path,
        config_path=args.config,
        id_idx=args.id_idx,
        fps=args.fps
    )
    
    if success:
        print("Blendshapes generation completed successfully!")
    else:
        print("Failed to generate blendshapes.")
        exit(1)


if __name__ == "__main__":
    main()

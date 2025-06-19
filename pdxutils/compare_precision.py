#!/usr/bin/env python3
"""
Script per confrontare i file prima e dopo l'arrotondamento
"""

import json

def compare_precision():
    print("🔍 Confronto Precisione: Prima vs Dopo Arrotondamento")
    print("=" * 60)
    
    # File con precisione originale (se esiste)
    try:
        with open('japanese_correct_format.json', 'r') as f:
            original = json.load(f)
        
        # File con arrotondamento
        with open('rounded_blendshapes.json', 'r') as f:
            rounded = json.load(f)
        
        print("📊 PRIMA (precisione originale):")
        frame = original[10]
        print(f"Time: {frame['time']}")
        count = 0
        for name, value in frame['blendshapes'].items():
            if value != 0 and count < 3:
                print(f"  {name}: {value}")
                count += 1
        
        print("\n📊 DOPO (arrotondato a 2 decimali):")
        frame = rounded[10]
        print(f"Time: {frame['time']}")
        count = 0
        for name, value in frame['blendshapes'].items():
            if value != 0 and count < 3:
                print(f"  {name}: {value}")
                count += 1
        
        # Calcola dimensioni file
        import os
        original_size = os.path.getsize('japanese_correct_format.json')
        rounded_size = os.path.getsize('rounded_blendshapes.json')
        
        print(f"\n💾 Dimensioni file:")
        print(f"  Originale: {original_size:,} bytes")
        print(f"  Arrotondato: {rounded_size:,} bytes")
        print(f"  Risparmio: {original_size - rounded_size:,} bytes ({((original_size - rounded_size) / original_size * 100):.1f}%)")
        
    except FileNotFoundError as e:
        print(f"❌ File non trovato: {e}")

if __name__ == '__main__':
    compare_precision()

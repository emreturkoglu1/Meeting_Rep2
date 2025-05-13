from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.audio import Model
from huggingface_hub import login
import whisper
import os
import ffmpeg
import tempfile
import numpy as np
import torch
import soundfile as sf
from typing import Dict, List, Any

# hugging face api access
hf_token = "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"

def normalize_audio(audio_file_path: str) -> str:
    """
    Normalize audio file to a standard format (16kHz, mono) that works well with diarization models
    
    Args:
        audio_file_path (str): Path to the original audio file
        
    Returns:
        str: Path to the normalized audio file
    """
    # Create temporary file for normalized audio
    temp_dir = tempfile.gettempdir()
    normalized_path = os.path.join(temp_dir, "normalized_audio.wav")
    
    try:
        # Use ffmpeg to normalize audio to 16kHz mono WAV
        (
            ffmpeg
            .input(audio_file_path)
            .output(normalized_path, acodec='pcm_s16le', ac=1, ar=16000)
            .overwrite_output()
            .run(quiet=True)
        )
        print(f"✅ Audio normalized to 16kHz mono format")
        return normalized_path
    except Exception as e:
        print(f"❌ Error normalizing audio: {str(e)}")
        # Return original path if normalization fails
        return audio_file_path

def process_audio_diarization(audio_file_path):
    """
    Process audio file for speaker diarization and transcription
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        list: List of dictionaries containing speaker segments with timestamps and text
    """
    print(f"\n🔍 Processing audio file: {audio_file_path}")
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    try:
        # Normalize audio to a standard format to prevent dimension mismatch errors
        normalized_audio_path = normalize_audio(audio_file_path)
        
        # Hugging Face verification
        login(token=hf_token)
        
        # Initialize Pyannote diarization pipeline
        print("🔄 Initializing diarization pipeline...")
        pipeline = SpeakerDiarization.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=hf_token
        )
        
        # Initialize Whisper model
        print("🔄 Loading Whisper model...")
        whisper_model = whisper.load_model("base")
        
        # Get diarization results
        print("🔄 Running speaker diarization...")
        diarization = pipeline(normalized_audio_path)
        
        # Get transcription
        print("🔄 Running speech-to-text transcription...")
        whisper_result = whisper_model.transcribe(normalized_audio_path)
        whisper_segments = whisper_result["segments"]
        
        # Get speaker segments
        speaker_segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker
            })
        
        # Process and combine results
        processed_segments = []
        for segment in whisper_segments:
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]
            
            # Find overlapping speaker segment
            speaker = "UNKNOWN"
            max_overlap = 0
            
            for spk_segment in speaker_segments:
                overlap_start = max(start_time, spk_segment['start'])
                overlap_end = min(end_time, spk_segment['end'])
                overlap_duration = max(0, overlap_end - overlap_start)
                
                if overlap_duration > max_overlap:
                    max_overlap = overlap_duration
                    speaker = spk_segment['speaker']
            
            processed_segments.append({
                'start_time': start_time,
                'end_time': end_time,
                'speaker': speaker,
                'text': text
            })
        
        print(f"✅ Successfully processed {len(processed_segments)} segments")
        
        # Clean up temporary file if created
        if normalized_audio_path != audio_file_path and os.path.exists(normalized_audio_path):
            try:
                os.remove(normalized_audio_path)
            except:
                pass
                
        return processed_segments
        
    except Exception as e:
        print(f"❌ Error in diarization process: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    test_audio = "test_audio.wav"
    if os.path.exists(test_audio):
        results = process_audio_diarization(test_audio)
        for segment in results:
            print(f"[{segment['start_time']:.2f} - {segment['end_time']:.2f}] {segment['speaker']}: {segment['text']}")

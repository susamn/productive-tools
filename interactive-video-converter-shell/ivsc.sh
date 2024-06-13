prompt() { read -p "$1 [$2]: " input; echo "${input:-$2}"; }

input_file=$(prompt "Enter the input file" "input.mp4")
conversion_type=$(prompt "Convert to (v)ideo or (a)udio?" "v")

if [ "$conversion_type" == "v" ]; then
  video_codec=$(prompt "Video codec (libx264, libx265, vp8, vp9, mpeg4)" "libx264")
  audio_codec=$(prompt "Audio codec (aac, mp3, vorbis, flac)" "aac")
  bitrate=$(prompt "Video bitrate (e.g., 500k, 1M)" "1M")
  framerate=$(prompt "Frame rate (e.g., 24, 30, 60)" "30")
  resolution=$(prompt "Resolution (e.g., 1280x720, 1920x1080, hd720, hd1080)" "hd720")
  output_extension="mkv"
else
  audio_codec=$(prompt "Audio codec (aac, mp3, vorbis, flac)" "mp3")
  output_extension="$audio_codec"
fi

output_name=$(prompt "Output file name (without extension)" "output")
output_file="$output_name.$output_extension"

if [ "$conversion_type" == "v" ]; then
  ffmpeg_command=(ffmpeg -i "$input_file" -c:v "$video_codec" -c:a "$audio_codec"
                  -b:v "$bitrate" -r "$framerate" -s "$resolution" "$output_file")
else
  ffmpeg_command=(ffmpeg -i "$input_file" -vn -c:a "$audio_codec" "$output_file")
fi

echo "Executing: ${ffmpeg_command[@]}"
"${ffmpeg_command[@]}"

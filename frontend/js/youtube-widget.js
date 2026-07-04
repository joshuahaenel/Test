export function playYoutubeVideo(embedUrl) {
  const frame = document.getElementById("youtube-frame");
  const empty = document.getElementById("youtube-empty");
  frame.src = `${embedUrl}?autoplay=1`;
  frame.classList.remove("hidden");
  empty.classList.add("hidden");
}

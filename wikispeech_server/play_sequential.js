const audios = Array.from(document.getElementsByTagName("audio"));

document.addEventListener('keyup', (e) => {
  if (e.keyCode === 80) { // p
    document.getElementById("toggle").click();
  }
});

let currentIndex = 0;
let currentAudio = null;
let isPlaying = false;

const toggleBtn = document.getElementById("toggle");
const stopBtn = document.getElementById("stop");

function playNext() {
  if (currentIndex >= audios.length) {
    isPlaying = false;
    toggleBtn.textContent = "Play";
    return;
  }

  currentAudio = audios[currentIndex];

  currentAudio.play().then(() => {
    isPlaying = true;
    toggleBtn.textContent = "Pause";
    if (document.getElementById("autoscroll").checked)
      currentAudio.scrollIntoView();
  }).catch(err => {
    console.warn("Playback failed:", err);
    currentIndex++;
    playNext();
  });

  currentAudio.onended = () => {
    currentIndex++;
    playNext();
  };
}

toggleBtn.addEventListener("click", () => {
  if (!currentAudio) {
    // Start fresh
    playNext();
    return;
  }

  if (isPlaying) {
    currentAudio.pause();
    isPlaying = false;
    toggleBtn.textContent = "Play All";
  } else {
    currentAudio.play();
    isPlaying = true;
    toggleBtn.textContent = "Pause";
  }
});

stopBtn.addEventListener("click", () => {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
  }

  currentIndex = 0;
  currentAudio = null;
  isPlaying = false;
  toggleBtn.textContent = "Play All";
});

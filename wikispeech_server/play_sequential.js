const audios = Array.from(document.getElementsByTagName("audio"));
const texts = Array.from(document.getElementsByClassName("text"));

document.addEventListener('keyup', (e) => {
  if (e.keyCode === 80) { // p
    document.getElementById("toggle").click();
  }
});

let currentManualPlayIndex = 0;
let currentIndex = 0;
let currentAudio = null;
let currentText = null;
let isPlaying = false;

const toggleBtn = document.getElementById("toggle");
const stopBtn = document.getElementById("stop");

function playNext() {
  if (currentIndex >= audios.length) {
    isPlaying = false;
    toggleBtn.textContent = "Play All";
    return;
  }

  currentAudio = audios[currentIndex];
  currentText = texts[currentIndex];

  currentAudio.play().then(() => {
    isPlaying = true;
    toggleBtn.textContent = "Pause";
    currentText.setAttribute("id","playing");
    if (document.getElementById("autoscroll").checked)
      currentAudio.parentElement.scrollIntoView();
  }).catch(err => {
    console.warn("Playback failed:", err);
    currentIndex++;
    playNext();
  });

  currentAudio.onended = () => {
    currentText.setAttribute("id","not_playing");
    currentIndex++;
    playNext();
  };
}

// Track which audio was last played
audios.forEach((audio, index) => {
  audio.addEventListener("play", (e) => {
    //console.log("e", e);
    currentManualPlayIndex = index;
    texts[index].setAttribute("id","playing");
  });
  audio.addEventListener("pause", (e) => {
    texts[index].setAttribute("id","not_playing");
    isPlaying = false;
    toggleBtn.textContent = "Play All";
  });
  audio.onended = (() => {
    texts[index].setAttribute("id","not_playing");
  });
});

toggleBtn.addEventListener("click", () => {
  if (currentManualPlayIndex>0 && !isPlaying) {
    //console.log("togglBtn click currentManualPlayIndex");
    currentIndex = currentManualPlayIndex;
    currentManualPlayIndex = 0;
    playNext();
    return;
  }
  if (!currentAudio) {
    //console.log("togglBtn click has currentAudio");
    // Start fresh
    playNext();
    return;
  }

  if (isPlaying) {
    //console.log("togglBtn click isPlaying");
    currentAudio.pause();
    currentText.setAttribute("id","not_playing");
    isPlaying = false;
    toggleBtn.textContent = "Play All";
  } else {
    currentAudio.play();
  }
});

stopBtn.addEventListener("click", () => {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentText.setAttribute("id","not_playing");
  }

  currentIndex = 0;
  currentAudio = null;
  currentManualPlayIndex = null;
  currentText = null;
  isPlaying = false;
  toggleBtn.textContent = "Play All";
});

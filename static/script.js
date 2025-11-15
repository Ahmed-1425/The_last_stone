// متغيرات عامة
let currentState = null; // {piles: [...], turn: "human"|"ai"|"none", ...}
let gameOver = false;
let currentStep = 0; // للأونبوردنق

// ------------------ دوال المساعدة العامة ------------------ //

function updateStatus(text) {
  const status = document.getElementById("status");
  if (status) status.textContent = text || "";
}

function renderPiles(piles) {
  const container = document.getElementById("piles");
  container.innerHTML = "";

  piles.forEach((count, index) => {
    const card = document.createElement("div");
    card.className = "pile-card";

    const title = document.createElement("h3");
    title.textContent = `كومة ${index + 1}`;
    card.appendChild(title);

    const stonesDiv = document.createElement("div");
    stonesDiv.className = "stones";
    stonesDiv.textContent = "●".repeat(count);
    card.appendChild(stonesDiv);

    const countDiv = document.createElement("div");
    countDiv.className = "count";
    countDiv.textContent = `${count} حجر${count !== 1 ? "ات" : ""}`;
    card.appendChild(countDiv);

    const btnRow = document.createElement("div");
    btnRow.className = "btn-row";

    for (let r = 1; r <= count; r++) {
      const btn = document.createElement("button");
      btn.textContent = `- ${r}`;
      btn.addEventListener("click", () => {
        if (!gameOver) {
          handleHumanMove(index, r);
        }
      });
      btnRow.appendChild(btn);
    }

    card.appendChild(btnRow);
    container.appendChild(card);
  });
}

function applyStateToUI(state) {
  currentState = state;
  gameOver = false;
  renderPiles(state.piles);

  if (state.turn === "human") {
    updateStatus("دورك – اختر كومة واحذف حجر أو أكثر.");
  } else if (state.turn === "ai") {
    updateStatus("دور الذكاء الاصطناعي…");
  } else {
    updateStatus("");
  }
}

// ------------------ الاتصالات مع الباك إند ------------------ //

async function fetchState() {
  const res = await fetch("/state");
  if (!res.ok) throw new Error("Failed to fetch state");
  const data = await res.json();
  applyStateToUI(data);
}

async function sendOptions() {
  const strategy = document.getElementById("strategy").value;
  const difficulty = document.getElementById("difficulty").value;

  const res = await fetch("/set_options", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ strategy, difficulty }),
  });

  if (!res.ok) throw new Error("Failed to set options");
  const data = await res.json();
  applyStateToUI(data);
}

async function handleHumanMove(pileIndex, removeCount) {
  if (!currentState || currentState.turn !== "human") return;

  const res = await fetch("/move/human", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pile: pileIndex, remove: removeCount }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    console.error("Human move error:", err);
    return;
  }

  const data = await res.json();
  currentState.piles = data.piles;

  if (data.winner === "human") {
    gameOver = true;
    showResultOverlay("human");
    renderPiles(data.piles);
    updateStatus("انتهت الجولة – فزت على الذكاء الاصطناعي!");
    return;
  }

  currentState.turn = "ai";
  renderPiles(data.piles);
  updateStatus("دور الذكاء الاصطناعي…");
  await handleAIMove();
}

async function handleAIMove() {
  if (!currentState || currentState.turn !== "ai") return;

  const thinking = document.getElementById("ai-thinking");
  thinking.classList.remove("hidden");

  const res = await fetch("/move/ai", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });

  thinking.classList.add("hidden");

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    console.error("AI move error:", err);
    return;
  }

  const data = await res.json();
  currentState.piles = data.piles;

  if (data.winner === "ai") {
    gameOver = true;
    showResultOverlay("ai");
    renderPiles(data.piles);
    updateStatus("انتهت الجولة – الذكاء الاصطناعي انتصر هذه المرة.");
    return;
  }

  currentState.turn = "human";
  renderPiles(data.piles);
  updateStatus("دورك – حاول تاخذ آخر حجر!");
}

// ------------------ شاشة النتيجة (Win / Lose) ------------------ //

function showResultOverlay(winner) {
  const overlay = document.getElementById("result-overlay");
  const badge = document.getElementById("result-badge");
  const title = document.getElementById("result-title");
  const subtitle = document.getElementById("result-subtitle");

  overlay.classList.remove("hidden");

  if (winner === "human") {
    badge.textContent = "فزت";
    badge.classList.add("win");
    badge.classList.remove("lose");
    title.textContent = "أخذت آخر حجر!";
    subtitle.textContent = "أحسنت، تغلبت على الذكاء الاصطناعي في هالجولة.";
  } else {
    badge.textContent = "خسرت";
    badge.classList.add("lose");
    badge.classList.remove("win");
    title.textContent = "الذكاء الاصطناعي أخذ آخر حجر.";
    subtitle.textContent = "جولة جميلة، جرّب استراتيجية مختلفة أو صعوبة أعلى وارجع حاول.";
  }
}

function hideResultOverlay() {
  const overlay = document.getElementById("result-overlay");
  overlay.classList.add("hidden");
}

// ------------------ Onboarding (شرح اللعبة) ------------------ //

function updateOnboardingView() {
  const steps = document.querySelectorAll(".onboarding-step");
  steps.forEach((step, index) => {
    step.classList.toggle("active", index === currentStep);
  });

  const backBtn = document.getElementById("onboarding-back");
  const nextBtn = document.getElementById("onboarding-next");
  const startBtn = document.getElementById("onboarding-start");

  backBtn.style.display = currentStep === 0 ? "none" : "inline-flex";
  nextBtn.style.display = currentStep === steps.length - 1 ? "none" : "inline-flex";
  startBtn.style.display = currentStep === steps.length - 1 ? "inline-flex" : "none";
}

function setupOnboarding() {
  const backBtn = document.getElementById("onboarding-back");
  const nextBtn = document.getElementById("onboarding-next");
  const startBtn = document.getElementById("onboarding-start");
  const onboarding = document.getElementById("onboarding");
  const gameScreen = document.getElementById("game-screen");

  backBtn.addEventListener("click", () => {
    if (currentStep > 0) {
      currentStep--;
      updateOnboardingView();
    }
  });

  nextBtn.addEventListener("click", () => {
    currentStep++;
    updateOnboardingView();
  });

  startBtn.addEventListener("click", () => {
    onboarding.classList.add("hidden");
    gameScreen.classList.remove("hidden");
  });

  currentStep = 0;
  updateOnboardingView();
}

// ------------------ شاشة الترحيب الشخصية ------------------ //

function setupWelcome() {
  const welcome = document.getElementById("welcomeScreen");
  const startBtn = document.getElementById("startApp");
  const onboarding = document.getElementById("onboarding");

  // أول ما يفتح الموقع: فقط شاشة الترحيب تظهر
  welcome.classList.remove("hidden");
  onboarding.classList.add("hidden");

  startBtn.addEventListener("click", () => {
    welcome.classList.add("hidden");
    onboarding.classList.remove("hidden");
  });
}

// ------------------ إعداد أزرار اللعبة ------------------ //

function setupGameControls() {
  const newGameBtn = document.getElementById("newGame");
  const strategySelect = document.getElementById("strategy");
  const difficultySelect = document.getElementById("difficulty");
  const playAgainBtn = document.getElementById("play-again");
  const closeOverlayBtn = document.getElementById("close-overlay");

  newGameBtn.addEventListener("click", async () => {
    hideResultOverlay();
    gameOver = false;
    await sendOptions();
  });

  strategySelect.addEventListener("change", async () => {
    hideResultOverlay();
    gameOver = false;
    await sendOptions();
  });

  difficultySelect.addEventListener("change", async () => {
    hideResultOverlay();
    gameOver = false;
    await sendOptions();
  });

  playAgainBtn.addEventListener("click", async () => {
    hideResultOverlay();
    gameOver = false;
    await sendOptions();
  });

  closeOverlayBtn.addEventListener("click", () => {
    hideResultOverlay();
  });
}

// ------------------ نقطة البداية ------------------ //

window.onload = async () => {
  setupWelcome();
  setupOnboarding();
  setupGameControls();

  try {
    await fetchState();
  } catch (e) {
    console.warn("Initial state fetch failed, will init on start.", e);
  }
};
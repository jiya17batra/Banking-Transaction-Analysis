// Typing Animation
const text = "BANKING TRANSACTION ANALYSIS";
const typing = document.getElementById("typing");
let i = 0;

function typeWriter() {
    if (i < text.length) {
        typing.innerHTML += text.charAt(i);
        i++;
        setTimeout(typeWriter, 70);
    }
}
typeWriter();

// Live Clock
function updateClock() {
    const now = new Date();
    document.getElementById("clock").innerHTML =
        now.toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();

// Animated Resource Bars
function animateBars() {
    document.querySelectorAll(".fill").forEach(bar => {
        bar.style.width = Math.random() * 100 + "%";
    });
}
setInterval(animateBars, 700);

// Wave Graph Animation
const canvas = document.getElementById("waveCanvas");
const ctx = canvas.getContext("2d");

canvas.width = 250;
canvas.height = 400;

let t = 0;

function drawWave() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.beginPath();

    for (let y = 0; y < canvas.height; y++) {
        let x = 125 + Math.sin(y * 0.05 + t) * 40;
        if (y === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }

    ctx.strokeStyle = "#00eaff";
    ctx.shadowBlur = 15;
    ctx.shadowColor = "#00eaff";
    ctx.stroke();

    t += 0.08;
    requestAnimationFrame(drawWave);
}
drawWave();

// Redirect Button

document.getElementById("enterBtn").addEventListener("click", () => {
    document.body.style.opacity = "0";
    document.body.style.transition = "opacity 0.8s ease";

    setTimeout(() => {
        window.location.href = "https://banking-transaction-analysis-live.streamlit.app/";
    }, 800);
});
// AI Voice Dictation Overlay App

// DOM Elements
const overlay = document.getElementById('overlay');
const recordingState = document.getElementById('recording-state');
const processingState = document.getElementById('processing-state');
const successState = document.getElementById('success-state');
const modeBadge = document.getElementById('mode-badge');
const waveformCanvas = document.getElementById('waveform');
const ctx = waveformCanvas.getContext('2d');

// State
let currentMode = 'email';
let autoPaste = false;
let waveformBars = new Array(20).fill(0);
let animationFrame = null;

// Initialize on load
document.addEventListener('DOMContentLoaded', async () => {
    // Get initial state from Python
    if (window.pywebview && window.pywebview.api) {
        try {
            const state = await window.pywebview.api.get_state();
            currentMode = state.mode;
            autoPaste = state.auto_paste;
            updateModeDisplay();
        } catch (e) {
            console.log('Could not get initial state:', e);
        }
    }
});

// Hide all states
function hideAllStates() {
    recordingState.classList.add('hidden');
    processingState.classList.add('hidden');
    successState.classList.add('hidden');
}

// Show recording state with waveform
function showRecording() {
    overlay.classList.remove('hidden', 'fade-out');
    hideAllStates();
    recordingState.classList.remove('hidden');
    updateModeDisplay();
    startWaveformAnimation();
}

// Update waveform with amplitude
function updateWaveform(amplitude) {
    // Shift bars left and add new amplitude
    waveformBars.shift();
    waveformBars.push(amplitude);
}

// Animate the waveform
function startWaveformAnimation() {
    if (animationFrame) cancelAnimationFrame(animationFrame);

    function draw() {
        // Clear canvas
        ctx.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height);

        const barWidth = waveformCanvas.width / waveformBars.length;
        const maxHeight = waveformCanvas.height * 0.8;
        const centerY = waveformCanvas.height / 2;

        // Draw bars
        waveformBars.forEach((amp, i) => {
            // Add some randomness for visual effect
            const noise = Math.random() * 0.1;
            const height = Math.max(4, (amp + noise) * maxHeight);

            // Gradient color based on amplitude
            const hue = 280 - (amp * 60); // Purple to pink
            ctx.fillStyle = `hsla(${hue}, 80%, 60%, 0.9)`;

            const x = i * barWidth + 2;
            const barH = height / 2;

            // Draw mirrored bars
            ctx.beginPath();
            ctx.roundRect(x, centerY - barH, barWidth - 4, barH * 2, 2);
            ctx.fill();
        });

        // Add subtle glow effect
        ctx.shadowBlur = 10;
        ctx.shadowColor = 'rgba(102, 126, 234, 0.3)';

        animationFrame = requestAnimationFrame(draw);
    }

    draw();
}

function stopWaveformAnimation() {
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
        animationFrame = null;
    }
}

// Show processing spinner
function showProcessing() {
    stopWaveformAnimation();
    hideAllStates();
    processingState.classList.remove('hidden');
}

// Show success and auto-hide
function showSuccess() {
    stopWaveformAnimation();
    hideAllStates();
    successState.classList.remove('hidden');

    // Auto-hide after 1 second
    setTimeout(() => {
        hideOverlay();
    }, 1000);
}

// Hide overlay with animation
function hideOverlay() {
    overlay.classList.add('fade-out');
    setTimeout(() => {
        overlay.classList.add('hidden');
        overlay.classList.remove('fade-out');
    }, 300);
}

// Update mode display
function updateModeDisplay() {
    modeBadge.textContent = currentMode.toUpperCase();
    modeBadge.classList.toggle('message', currentMode === 'message');
}

// External API for Python
function updateMode(mode) {
    currentMode = mode;
    updateModeDisplay();
}

function updateAutoPaste(enabled) {
    autoPaste = enabled;
}

// Expose functions to window for pywebview
window.showRecording = showRecording;
window.updateWaveform = updateWaveform;
window.showProcessing = showProcessing;
window.showSuccess = showSuccess;
window.hideOverlay = hideOverlay;
window.updateMode = updateMode;
window.updateAutoPaste = updateAutoPaste;

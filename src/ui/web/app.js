// AI Voice Dictation Overlay App

// DOM Elements
const overlay = document.getElementById('overlay');
const idleState = document.getElementById('idle-state');
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
    // Start in idle state
    showIdle();

    // Add click handler for mode toggle
    const idleMic = document.querySelector('.idle-mic');
    if (idleMic) {
        idleMic.addEventListener('click', toggleMode);
    }
});

// Toggle between modes
async function toggleMode() {
    const newMode = currentMode === 'email' ? 'message' : 'email';
    currentMode = newMode;

    // Update local UI
    updateModeDisplay();
    showModeChangeFeedback();

    // Update Python backend
    if (window.pywebview && window.pywebview.api) {
        try {
            await window.pywebview.api.set_mode(newMode);
        } catch (e) {
            console.log('Error setting mode:', e);
        }
    }
}

// Show brief visual feedback when mode changes (flash icon)
function showModeChangeFeedback() {
    const idleMic = document.querySelector('.idle-mic');
    if (!idleMic) return;

    // Remove existing classes to restart animation
    idleMic.classList.remove('flash-email', 'flash-message');

    // Trigger reflow
    void idleMic.offsetWidth;

    // Add flash class based on mode
    idleMic.classList.add(currentMode === 'email' ? 'flash-email' : 'flash-message');

    // Clean up after animation
    setTimeout(() => {
        idleMic.classList.remove('flash-email', 'flash-message');
    }, 800);
}

// Hide all states
function hideAllStates() {
    idleState.classList.add('hidden');
    recordingState.classList.add('hidden');
    processingState.classList.add('hidden');
    successState.classList.add('hidden');
}

// Show idle state (small persistent icon)
function showIdle() {
    stopWaveformAnimation();
    hideAllStates();
    idleState.classList.remove('hidden');

    // Contract to circle
    overlay.classList.remove('active');
    overlay.classList.remove('hidden');
    overlay.classList.remove('fade-out');
    overlay.classList.add('idle');
}

// Show recording state with waveform (expanded)
function showRecording() {
    hideAllStates();
    recordingState.classList.remove('hidden');
    updateModeDisplay();

    // Expand window
    overlay.classList.remove('idle');
    overlay.classList.remove('hidden');
    overlay.classList.add('active');

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
    // Ensure active state
    overlay.classList.remove('idle');
    overlay.classList.remove('hidden');
    overlay.classList.add('active');
}

// Show success and return to idle
function showSuccess() {
    stopWaveformAnimation();
    hideAllStates();
    successState.classList.remove('hidden');

    // Return to idle after delay
    setTimeout(() => {
        showIdle();
    }, 1500);
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
window.showIdle = showIdle;
window.showRecording = showRecording;
window.updateWaveform = updateWaveform;
window.showProcessing = showProcessing;
window.showSuccess = showSuccess;
window.updateMode = updateMode;
window.updateAutoPaste = updateAutoPaste;

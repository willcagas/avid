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
let currentMode = 'message';
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

    // Event listeners
    const idleMic = document.querySelector('.idle-mic');
    const closeMenuBtn = document.getElementById('close-menu-btn');
    const modeToggleBtn = document.getElementById('mode-toggle-btn');

    if (idleMic) {
        // Handle click manually to distinguishing drag/long-press
        let startX, startY, startTime;

        idleMic.addEventListener('mousedown', (e) => {
            startX = e.screenX;
            startY = e.screenY;
            startTime = Date.now();
        });

        idleMic.addEventListener('mouseup', (e) => {
            const diffX = Math.abs(e.screenX - startX);
            const diffY = Math.abs(e.screenY - startY);
            const duration = Date.now() - startTime;

            // Only toggle if minimal movement (not a drag) AND short duration (tap)
            if (diffX < 5 && diffY < 5 && duration < 300) {
                showMenu();
            }
        });
    }
    if (closeMenuBtn) closeMenuBtn.addEventListener('click', showIdle);
    if (modeToggleBtn) modeToggleBtn.addEventListener('click', toggleMode);
});

// Show mode selection menu
function showMenu() {
    // Notify Python to expand window
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.set_ui_state('expanded');
    }

    hideAllStates();
    document.getElementById('settings-state').classList.remove('hidden');

    overlay.classList.remove('idle');
    overlay.classList.remove('active');
    overlay.classList.add('menu-open');

    // Update menu UI labels
    updateMenuDisplay();
}

// Toggle between modes
async function toggleMode() {
    let newMode;
    if (currentMode === 'message') newMode = 'email';
    else if (currentMode === 'email') newMode = 'notes';
    else if (currentMode === 'notes') newMode = 'prompt';
    else newMode = 'message';

    currentMode = newMode;

    // Update local UI
    updateModeDisplay();
    updateMenuDisplay();

    // Update Python backend
    if (window.pywebview && window.pywebview.api) {
        try {
            await window.pywebview.api.set_mode(newMode);
        } catch (e) {
            console.log('Error setting mode:', e);
        }
    }
}

// Update menu UI elements
function updateMenuDisplay() {
    const modeLabel = document.getElementById('settings-mode-label');
    const modeControl = document.getElementById('mode-toggle-btn');

    if (modeLabel) modeLabel.textContent = currentMode.toUpperCase();

    if (modeControl) {
        modeControl.classList.remove('show-email', 'show-message', 'show-prompt', 'show-notes');
        modeControl.classList.add(`show-${currentMode}`);
    }
}

// Hide all states
function hideAllStates() {
    idleState.classList.add('hidden');
    recordingState.classList.add('hidden');
    processingState.classList.add('hidden');
    successState.classList.add('hidden');
    document.getElementById('settings-state').classList.add('hidden');
}

// Show idle state (small persistent icon)
function showIdle() {
    // Notify Python to shrink window
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.set_ui_state('idle');
    }

    stopWaveformAnimation();
    hideAllStates();
    idleState.classList.remove('hidden');

    // Contract to circle
    overlay.classList.remove('active');
    overlay.classList.remove('menu-open');
    overlay.classList.remove('hidden');
    overlay.classList.remove('fade-out');
    overlay.classList.add('idle');

    // Update idle icon display
    updateModeDisplay();
}

// Show recording state with waveform (expanded)
function showRecording() {
    // Notify Python to expand window
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.set_ui_state('expanded');
    }

    hideAllStates();
    recordingState.classList.remove('hidden');
    updateModeDisplay();

    // Expand window
    overlay.classList.remove('idle');
    overlay.classList.remove('menu-open');
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

            // Gradient color based on amplitude (Pink theme)
            // Light Pink #FFB6C1 is roughly hue 350
            // We can vary lightness or saturation based on amplitude
            const alpha = 0.6 + (amp * 0.4);
            ctx.fillStyle = `rgba(255, 182, 193, ${alpha})`;

            const x = i * barWidth + 2;
            const barH = height / 2;

            // Draw mirrored bars
            ctx.beginPath();
            ctx.roundRect(x, centerY - barH, barWidth - 4, barH * 2, 2);
            ctx.fill();
        });

        // Add subtle glow effect
        ctx.shadowBlur = 10;
        ctx.shadowColor = 'rgba(255, 182, 193, 0.5)';

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
    // Notify Python to expand window
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.set_ui_state('expanded');
    }

    stopWaveformAnimation();
    hideAllStates();
    processingState.classList.remove('hidden');
    // Ensure active state
    overlay.classList.remove('idle');
    overlay.classList.remove('menu-open');
    overlay.classList.remove('hidden');
    overlay.classList.add('active');
}

// Show success and return to idle
// Show success (skip visual confirmation as per request) and return to idle
function showSuccess() {
    // Immediately return to idle state
    showIdle();
}

// Update mode display
function updateModeDisplay() {
    if (!modeBadge) return;
    modeBadge.textContent = currentMode.toUpperCase();

    // Reset classes
    modeBadge.classList.remove('message', 'prompt', 'notes');

    // Add active class if not default (email)
    if (currentMode === 'message') modeBadge.classList.add('message');
    else if (currentMode === 'prompt') modeBadge.classList.add('prompt');
    else if (currentMode === 'notes') modeBadge.classList.add('notes');
}

// External API for Python
function updateMode(mode) {
    currentMode = mode;
    updateModeDisplay();
    updateMenuDisplay();
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

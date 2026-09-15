/**
 * AgriConnect - Interactive On-Screen IVR Phone Simulator
 * Designed for SIH Evaluators & Judges to test non-smartphone farmer voice interactions.
 * Features: Realistic Telephone Ringback, DTMF Tones, Web Speech API with Auto-Fallbacks,
 * Multi-Language Voice Modes (Hindi / Hinglish / English), and Simulated Voice Harvest Intake.
 */

class IVRPhoneSimulator {
  constructor() {
    this.callActive = false;
    this.audioCtx = null;
    this.currentMenuState = 'ROOT';
    this.voices = [];
    this.localHindiVoice = null;
    this.onlineHindiVoice = null;
    this.hindiVoice = null;
    this.indianVoice = null;
    this.defaultVoice = null;
    this.selectedVoice = null;
    this.selectedVoiceKey = 'auto';
    this.currentUtterance = null;
    this.langMode = 'hi'; // 'hi' (Hindi), 'hinglish' (Phonetic), 'en' (English)
    this.recognition = null;
    this.keepAliveInterval = null;

    this.initVoices();
    this.initKeypad();
    this.initSpeechRecognition();
  }

  unlockAudio() {
    // 1. Resume Web Audio API AudioContext
    try {
      const ctx = this.getAudioContext();
      if (ctx && ctx.state === 'suspended') {
        ctx.resume().catch(e => console.warn("[IVR Audio] AudioContext resume error:", e));
      }
    } catch (e) {
      console.warn("[IVR Audio] Unlock AudioContext failed:", e);
    }

    // 2. Prime Web Speech Synthesis inside user gesture
    try {
      if ('speechSynthesis' in window) {
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
        }
        // Prime with an empty utterance to grant autoplay rights
        const primeUtterance = new SpeechSynthesisUtterance(' ');
        primeUtterance.volume = 0.01;
        primeUtterance.rate = 10;
        window.speechSynthesis.speak(primeUtterance);
      }
    } catch (e) {
      console.warn("[IVR Audio] Prime SpeechSynthesis failed:", e);
    }
  }

  getAudioContext() {
    if (!this.audioCtx) {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.audioCtx = new AudioContext();
      } catch (e) {
        console.warn("[IVR Audio] Web Audio API not supported", e);
      }
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume().catch(() => {});
    }
    return this.audioCtx;
  }

  initVoices() {
    const updateVoices = () => {
      if (!('speechSynthesis' in window)) return;

      this.voices = window.speechSynthesis.getVoices() || [];
      if (this.voices.length === 0) return;

      // 1. Local Hindi Voice (Offline / Native SAPI)
      this.localHindiVoice = this.voices.find(v => {
        const lang = (v.lang || '').toLowerCase();
        const name = (v.name || '').toLowerCase();
        const isHindi = lang.startsWith('hi') || lang.includes('hindi') || name.includes('hindi') || name.includes('kalpana') || name.includes('hemant');
        const isLocal = v.localService === true || (!name.includes('online') && !name.includes('natural'));
        return isHindi && isLocal;
      });

      // 2. Online / Any Hindi Voice (e.g. Microsoft Swara Online in Edge)
      this.onlineHindiVoice = this.voices.find(v => {
        const lang = (v.lang || '').toLowerCase();
        const name = (v.name || '').toLowerCase();
        return lang.startsWith('hi') || lang.includes('hindi') || name.includes('hindi') || name.includes('kalpana') || name.includes('hemant') || name.includes('swara');
      });

      // Hindi voice preference: Prefer local Hindi over cloud if available, otherwise use online
      this.hindiVoice = this.localHindiVoice || this.onlineHindiVoice || null;

      // 3. Indian English Voice (Optimal for Phonetic Hinglish pronunciation)
      this.indianVoice = this.voices.find(v => {
        const lang = (v.lang || '').toLowerCase();
        const name = (v.name || '').toLowerCase();
        return lang.includes('en-in') || lang.includes('en_in') || name.includes('india') || name.includes('heera') || name.includes('veena') || name.includes('neerja') || name.includes('ravi');
      });

      // 4. Default / Fallback System Voice (David, Zira, Mark, Google US English, etc.)
      this.defaultVoice = this.voices.find(v => v.default) || 
                          this.voices.find(v => (v.lang || '').toLowerCase().startsWith('en') && v.localService === true) || 
                          this.voices.find(v => (v.lang || '').toLowerCase().startsWith('en')) || 
                          this.voices[0] || null;

      // Populate voice selector dropdown in UI if present
      this.populateVoiceSelect();
      this.updateVoiceBadge();

      console.log(`[IVR Audio] Loaded ${this.voices.length} voices. HindiLocal=${this.localHindiVoice?.name || 'None'}, HindiOnline=${this.onlineHindiVoice?.name || 'None'}, IndianEng=${this.indianVoice?.name || 'None'}, Default=${this.defaultVoice?.name || 'None'}`);
    };

    updateVoices();
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = updateVoices;
    }
  }

  populateVoiceSelect() {
    const select = document.getElementById('ivrVoiceSelect');
    if (!select || this.voices.length === 0) return;

    const currentVal = select.value || 'auto';
    select.innerHTML = '';

    // Default Auto option
    const autoOpt = document.createElement('option');
    autoOpt.value = 'auto';
    autoOpt.innerText = '⚡ Auto-Select (Smart Fallback)';
    select.appendChild(autoOpt);

    // Group voices
    const hindiGroup = document.createElement('optgroup');
    hindiGroup.label = 'Hindi Voices (हिंदी)';

    const indianEngGroup = document.createElement('optgroup');
    indianEngGroup.label = 'Indian English Voices (Best for Hinglish)';

    const otherGroup = document.createElement('optgroup');
    otherGroup.label = 'System / English Voices';

    this.voices.forEach(v => {
      const opt = document.createElement('option');
      const key = `${v.name}|${v.lang}`;
      opt.value = key;
      const isOnline = v.name.includes('Online') || v.localService === false;
      const onlineTag = isOnline ? ' [Cloud]' : ' [Local]';
      opt.innerText = `${v.name} (${v.lang})${onlineTag}`;

      const lang = (v.lang || '').toLowerCase();
      const name = (v.name || '').toLowerCase();

      if (lang.startsWith('hi') || name.includes('hindi') || name.includes('kalpana') || name.includes('hemant') || name.includes('swara')) {
        hindiGroup.appendChild(opt);
      } else if (lang.includes('en-in') || lang.includes('en_in') || name.includes('india') || name.includes('heera') || name.includes('veena') || name.includes('ravi')) {
        indianEngGroup.appendChild(opt);
      } else {
        otherGroup.appendChild(opt);
      }
    });

    if (hindiGroup.children.length > 0) select.appendChild(hindiGroup);
    if (indianEngGroup.children.length > 0) select.appendChild(indianEngGroup);
    if (otherGroup.children.length > 0) select.appendChild(otherGroup);

    // Restore selected value if still valid
    select.value = currentVal;
    if (select.selectedIndex === -1) select.value = 'auto';
  }

  changeVoice(voiceKey) {
    this.selectedVoiceKey = voiceKey;
    if (voiceKey === 'auto') {
      this.selectedVoice = null;
    } else {
      this.selectedVoice = this.voices.find(v => `${v.name}|${v.lang}` === voiceKey) || null;
    }
    this.updateVoiceBadge();
    const voiceName = this.selectedVoice ? this.selectedVoice.name : 'Auto-Selected';
    this.appendLog("System Audio", `Voice changed to: <strong>${voiceName}</strong>`, "system");
  }

  updateVoiceBadge() {
    const voiceBadge = document.getElementById('ivrVoiceLabel');
    if (!voiceBadge) return;

    if (this.selectedVoice) {
      voiceBadge.innerText = `Voice: ${this.selectedVoice.name}`;
      return;
    }

    if (this.langMode === 'en') {
      const v = this.indianVoice || this.defaultVoice;
      voiceBadge.innerText = v ? `Voice: ${v.name} (en)` : 'Voice: System TTS';
    } else if (this.langMode === 'hinglish') {
      const v = this.indianVoice || this.defaultVoice;
      voiceBadge.innerText = v ? `Voice: ${v.name} (Hinglish)` : 'Voice: System TTS';
    } else {
      // Hindi mode
      if (this.hindiVoice) {
        voiceBadge.innerText = `Voice: ${this.hindiVoice.name} (hi)`;
      } else if (this.indianVoice) {
        voiceBadge.innerText = `Voice: ${this.indianVoice.name} (Hinglish Auto)`;
      } else if (this.defaultVoice) {
        voiceBadge.innerText = `Voice: ${this.defaultVoice.name} (Hinglish Auto)`;
      } else {
        voiceBadge.innerText = `Voice: System TTS`;
      }
    }
  }

  setLanguage(mode) {
    this.langMode = mode;
    ['ivrLangHiBtn', 'ivrLangHinglishBtn', 'ivrLangEnBtn'].forEach(id => {
      const btn = document.getElementById(id);
      if (btn) {
        btn.className = 'btn btn-sm btn-outline-secondary rounded-pill px-3 py-1';
      }
    });

    const activeId = mode === 'hi' ? 'ivrLangHiBtn' : (mode === 'hinglish' ? 'ivrLangHinglishBtn' : 'ivrLangEnBtn');
    const activeBtn = document.getElementById(activeId);
    if (activeBtn) {
      activeBtn.className = 'btn btn-sm btn-success rounded-pill px-3 py-1';
    }

    this.updateVoiceBadge();

    const modeLabels = { hi: 'हिंदी (Hindi)', hinglish: 'हिंग्लिश (Phonetic)', en: 'English' };
    this.appendLog("System", `Language switched to: <strong>${modeLabels[mode]}</strong>`, "system");
  }

  playRingbackTone(callback) {
    const ctx = this.getAudioContext();
    if (!ctx) {
      if (callback) callback();
      return;
    }

    // Standard phone ringback: 400Hz + 450Hz dual tone (Louder & clear)
    const playBurst = (startTime, duration) => {
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();

      osc1.frequency.value = 400;
      osc2.frequency.value = 450;

      gain.gain.setValueAtTime(0.001, startTime);
      gain.gain.linearRampToValueAtTime(0.30, startTime + 0.05);
      gain.gain.setValueAtTime(0.30, startTime + duration - 0.05);
      gain.gain.linearRampToValueAtTime(0.001, startTime + duration);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(ctx.destination);

      osc1.start(startTime);
      osc2.start(startTime);
      osc1.stop(startTime + duration);
      osc2.stop(startTime + duration);
    };

    const now = ctx.currentTime;
    playBurst(now, 0.4);
    playBurst(now + 0.6, 0.4);

    setTimeout(() => {
      this.playConnectChime();
      if (callback) callback();
    }, 1100);
  }

  playConnectChime() {
    const ctx = this.getAudioContext();
    if (!ctx) return;
    try {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(540, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(850, ctx.currentTime + 0.14);
      gain.gain.setValueAtTime(0.25, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.18);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.18);
    } catch (e) {}
  }

  playBeep() {
    const ctx = this.getAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = 1000; // 1kHz standard voicemail beep

    const now = ctx.currentTime;
    gain.gain.setValueAtTime(0.001, now);
    gain.gain.linearRampToValueAtTime(0.30, now + 0.03);
    gain.gain.setValueAtTime(0.30, now + 0.35);
    gain.gain.linearRampToValueAtTime(0.001, now + 0.4);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.4);
  }

  playDTMFTone(key) {
    const ctx = this.getAudioContext();
    if (!ctx) return;

    // Standard DTMF frequency matrix
    const dtmfFreqs = {
      '1': [697, 1209], '2': [697, 1336], '3': [697, 1477],
      '4': [770, 1209], '5': [770, 1336], '6': [770, 1477],
      '7': [852, 1209], '8': [852, 1336], '9': [852, 1477],
      '*': [941, 1209], '0': [941, 1336], '#': [941, 1477]
    };

    const freqs = dtmfFreqs[key] || [800, 1200];
    const osc1 = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();

    osc1.frequency.value = freqs[0];
    osc2.frequency.value = freqs[1];

    const now = ctx.currentTime;
    gain.gain.setValueAtTime(0.35, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);

    osc1.connect(gain);
    osc2.connect(gain);
    gain.connect(ctx.destination);

    osc1.start(now);
    osc2.start(now);
    osc1.stop(now + 0.16);
    osc2.stop(now + 0.16);
  }

  speak(hindiText, hinglishText, englishText, isRetry = false) {
    if (!('speechSynthesis' in window)) {
      console.warn("[IVR Audio] Web Speech Synthesis not supported in this browser");
      this.appendLog("System Audio", "⚠️ Web Speech Synthesis not supported in this browser.", "system");
      return;
    }

    // 1. Resume synthesis if paused
    try {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
    } catch (e) {}

    // 2. Safely cancel ongoing speech if active
    if (window.speechSynthesis.speaking && !isRetry) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }

    // 3. Refresh voices if empty
    if (!this.voices || this.voices.length === 0) {
      this.voices = window.speechSynthesis.getVoices() || [];
    }

    // 4. Select voice & text to speak
    let textToSpeak = '';
    let voiceToUse = this.selectedVoice || null;
    let langCode = 'en-US';

    if (voiceToUse) {
      // User manually selected a specific voice from dropdown
      const voiceIsHindi = (voiceToUse.lang || '').toLowerCase().startsWith('hi');
      if (this.langMode === 'en') {
        textToSpeak = englishText || hinglishText || hindiText;
      } else if (this.langMode === 'hinglish') {
        textToSpeak = hinglishText || hindiText;
      } else {
        // Mode is 'hi'
        textToSpeak = voiceIsHindi ? (hindiText || hinglishText) : (hinglishText || hindiText);
      }
      langCode = voiceToUse.lang || (voiceIsHindi ? 'hi-IN' : 'en-US');
    } else {
      // AUTO MODE (Smart Selection with local voice priority)
      if (this.langMode === 'en') {
        textToSpeak = englishText || hinglishText || hindiText;
        voiceToUse = this.indianVoice || this.defaultVoice;
        langCode = voiceToUse ? voiceToUse.lang : 'en-US';
      } else if (this.langMode === 'hinglish') {
        textToSpeak = hinglishText || hindiText;
        voiceToUse = this.indianVoice || this.defaultVoice;
        langCode = voiceToUse ? voiceToUse.lang : 'en-IN';
      } else {
        // 'hi' (Hindi Mode)
        if (this.hindiVoice && !isRetry) {
          textToSpeak = hindiText;
          voiceToUse = this.hindiVoice;
          langCode = this.hindiVoice.lang || 'hi-IN';
        } else {
          // Device has NO Hindi voice or previous Hindi voice failed:
          // Fallback to Hinglish text with Indian or system English voice!
          textToSpeak = hinglishText || hindiText;
          voiceToUse = this.indianVoice || this.defaultVoice;
          langCode = voiceToUse ? voiceToUse.lang : 'en-IN';
        }
      }
    }

    // CRITICAL GUARD: English voices CANNOT read Devanagari Hindi characters!
    // They skip them and produce 0 sound. Always switch to Hinglish for non-Hindi voices!
    const hasDevanagari = /[\u0900-\u097F]/.test(textToSpeak);
    const isHindiCapable = voiceToUse && (voiceToUse.lang || '').toLowerCase().startsWith('hi');
    if (hasDevanagari && !isHindiCapable) {
      console.log("[IVR Audio] Selected voice does not support Devanagari. Switching text to phonetic Hinglish.");
      textToSpeak = hinglishText || hindiText;
    }

    // 5. Create Utterance
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = 0.92;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    if (voiceToUse) {
      utterance.voice = voiceToUse;
      utterance.lang = voiceToUse.lang || langCode;
    } else {
      utterance.lang = langCode;
    }

    // Keep active reference on window to prevent V8 GC bug
    window.__activeIVRUtterance = utterance;
    this.currentUtterance = utterance;

    let hasStarted = false;
    let watchdogTimer = null;

    utterance.onstart = () => {
      hasStarted = true;
      if (watchdogTimer) clearTimeout(watchdogTimer);
      this.setSpeaking(true);
      console.log(`[IVR Audio] Speaking started with [${voiceToUse ? voiceToUse.name : 'Default'}]: "${textToSpeak.slice(0, 35)}..."`);
    };

    utterance.onend = () => {
      if (watchdogTimer) clearTimeout(watchdogTimer);
      this.setSpeaking(false);
      this.currentUtterance = null;
      window.__activeIVRUtterance = null;
    };

    utterance.onerror = (err) => {
      if (watchdogTimer) clearTimeout(watchdogTimer);
      console.warn("[IVR Audio] Utterance error:", err.error, err);
      this.setSpeaking(false);
      this.currentUtterance = null;
      window.__activeIVRUtterance = null;

      if (err.error === 'canceled' || err.error === 'interrupted') {
        return; // Normal cancel
      }

      // AUTOMATIC FALLBACK: If an online cloud voice (like Microsoft Swara Online) fails over network,
      // immediately retry with local system voice using Hinglish!
      if (!isRetry) {
        console.warn("[IVR Audio] Voice synthesis failed. Retrying with local system voice (Hinglish)...");
        this.appendLog("System Audio", `⚠️ Cloud voice failed (${err.error || 'network'}). Retrying with system voice...`, "system");
        
        // Find safe local voice
        const fallbackVoice = this.voices.find(v => v.localService === true && !v.name.includes('Online')) || this.defaultVoice;
        this.selectedVoice = fallbackVoice;
        
        setTimeout(() => {
          this.speak(hindiText, hinglishText, englishText, true);
        }, 120);
      }
    };

    // Watchdog: If an online voice hangs and onstart doesn't fire within 2000ms, retry with local voice!
    const isOnlineVoice = voiceToUse && (voiceToUse.name.includes('Online') || voiceToUse.localService === false);
    if (isOnlineVoice && !isRetry) {
      watchdogTimer = setTimeout(() => {
        if (!hasStarted && this.callActive) {
          console.warn("[IVR Audio] Online voice timed out without starting. Falling back to local voice...");
          try { window.speechSynthesis.cancel(); } catch (e) {}
          const fallbackVoice = this.voices.find(v => v.localService === true && !v.name.includes('Online')) || this.defaultVoice;
          this.selectedVoice = fallbackVoice;
          this.speak(hindiText, hinglishText, englishText, true);
        }
      }, 2000);
    }

    // Keep-alive ping for Chrome 15s pause bug
    if (this.keepAliveInterval) clearInterval(this.keepAliveInterval);
    this.keepAliveInterval = setInterval(() => {
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
      } else {
        clearInterval(this.keepAliveInterval);
      }
    }, 10000);

    // Speak with small delay to prevent cancel race
    setTimeout(() => {
      try {
        if (window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
        }
        window.speechSynthesis.speak(utterance);
      } catch (e) {
        console.warn("[IVR Audio] Speech execution error:", e);
        this.setSpeaking(false);
      }
    }, 60);
  }

  setSpeaking(isSpeaking) {
    const wave = document.getElementById('ivrAudioWave');
    const idle = document.getElementById('ivrAudioIdle');
    if (wave && idle) {
      if (isSpeaking) {
        wave.classList.remove('d-none');
        idle.classList.add('d-none');
      } else {
        wave.classList.add('d-none');
        idle.classList.remove('d-none');
      }
    }
  }

  testAudio() {
    this.unlockAudio();
    this.playDTMFTone('1');

    const voiceName = this.selectedVoice ? this.selectedVoice.name : (this.hindiVoice?.name || this.indianVoice?.name || this.defaultVoice?.name || 'System Voice');
    this.appendLog("System Audio", `🔊 Testing Audio & Voice: <strong>${voiceName}</strong>...`, "system");

    setTimeout(() => {
      this.speak(
        "नमस्ते, एग्रीकनेक्ट किसान आईवीआर ऑडियो सक्रिय है।",
        "Namaste, AgriConnect Kisan IVR audio sakriya hai.",
        "Hello, AgriConnect Kisan IVR audio system is fully active."
      );
      this.setScreen("ऑडियो टेस्ट: आवाज़ सक्रिय है!\nAudio test: Voice is playing.");
    }, 250);
  }

  initKeypad() {
    this.callBtn = document.getElementById('ivrCallBtn');
    this.endCallBtn = document.getElementById('ivrEndCallBtn');
    this.callStatus = document.getElementById('ivrCallStatus');
    this.displayScreen = document.getElementById('ivrScreenText');
    this.transcriptLog = document.getElementById('ivrTranscriptLog');
    this.voiceDrawer = document.getElementById('ivrVoiceDrawer');

    if (this.callBtn) {
      this.callBtn.addEventListener('click', () => {
        this.unlockAudio();
        this.startCall();
      });
    }

    if (this.endCallBtn) {
      this.endCallBtn.addEventListener('click', () => this.endCall());
    }

    // Keypad number buttons
    document.querySelectorAll('.dtmf-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.unlockAudio();
        const key = btn.getAttribute('data-key');
        btn.classList.add('active-press');
        setTimeout(() => btn.classList.remove('active-press'), 150);
        this.handleKeyPress(key);
      });
    });
  }

  startCall() {
    this.unlockAudio();
    this.callActive = true;

    if (this.callBtn) this.callBtn.classList.add('d-none');
    if (this.endCallBtn) this.endCallBtn.classList.remove('d-none');
    if (this.voiceDrawer) this.voiceDrawer.classList.add('d-none');

    if (this.callStatus) {
      this.callStatus.className = 'badge bg-warning text-dark py-1 px-2';
      this.callStatus.innerHTML = '<i class="fa-solid fa-phone-volume me-1 fa-shake"></i> DIALING 1800-890-KISAN...';
    }
    this.setScreen("डायल किया जा रहा है...\nDialing 1800-890-KISAN (Krishi Helpline)...");

    // Play ringing tone before operator answers
    this.playRingbackTone(() => {
      if (!this.callActive) return;

      if (this.callStatus) {
        this.callStatus.className = 'badge bg-success py-1 px-2';
        this.callStatus.innerHTML = '<i class="fa-solid fa-phone me-1"></i> CONNECTED (1800-890-KISAN)';
      }

      const greetingHindi = "नमस्ते! किसान सेतु में आपका स्वागत है। दैनिक मंडी भाव के लिए 1 दबाएं। अपनी फसल बेचने के लिए 2 दबाएं। भुगतान स्थिति के लिए 3 दबाएं। ग्राम मित्र से बात करने के लिए 4 दबाएं।";
      const greetingHinglish = "Namaste! Kisan Setu me aapka swagat hai. Dainik Mandi bhav janne ke liye 1 dabayein. Apni fasal bechne ke liye 2 dabayein. Bhugtan status ke liye 3 dabayein. Gram Mitra ke liye 4 dabayein.";
      const greetingEn = "Welcome to AgriConnect Kisan Helpline. Press 1 for Mandi Rates. Press 2 to sell harvest. Press 3 for payment status. Press 4 to speak with Village Facilitator.";

      this.appendLog("AgriConnect IVR", greetingHindi, "bot");
      this.setScreen("1: मंडी भाव | 2: फसल बेचें\n3: भुगतान स्थिति | 4: ग्राम मित्र\n0: सक्रिय मांग | *: मेन्यू");
      this.speak(greetingHindi, greetingHinglish, greetingEn);
    });
  }

  endCall() {
    this.callActive = false;
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    if (this.keepAliveInterval) clearInterval(this.keepAliveInterval);
    this.setSpeaking(false);

    if (this.callBtn) this.callBtn.classList.remove('d-none');
    if (this.endCallBtn) this.endCallBtn.classList.add('d-none');
    if (this.voiceDrawer) this.voiceDrawer.classList.add('d-none');

    if (this.callStatus) {
      this.callStatus.className = 'badge bg-secondary py-1 px-2';
      this.callStatus.innerHTML = '<i class="fa-solid fa-phone-slash me-1"></i> CALL ENDED';
    }
    this.setScreen("कॉल समाप्त हो गई है।\nपुनः कॉल करने के लिए हरा बटन दबाएं।");
    this.appendLog("System", "कॉल समाप्त (Call Ended).", "system");
  }

  handleKeyPress(key) {
    this.playDTMFTone(key);

    if (!this.callActive) {
      this.setScreen(`Number [ ${key} ] pressed.\nClick GREEN call button to dial 1800-890-KISAN.`);
      return;
    }

    this.appendLog("Farmer (You)", `Pressed [ ${key} ]`, "user");

    // Close voice drawer if moving away from option 2
    if (key !== '2' && this.voiceDrawer) {
      this.voiceDrawer.classList.add('d-none');
    }

    // Fetch dynamic response from Django backend API
    fetch('/facilitator/api/ivr-action/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ key: key })
    })
    .then(res => res.json())
    .then(data => {
      let displayText = data.title;
      if (Array.isArray(data.display)) {
        displayText += "\n" + data.display.map(d => `${d.crop}: ${d.agriconnect_rate} (${d.benefit})`).join("\n");
      } else {
        displayText += `\n${data.display}`;
      }
      this.setScreen(displayText);
      this.appendLog("AgriConnect IVR", `${data.title}: ${data.speech}`, "bot");
      this.speak(data.speech, data.speech_hinglish, data.speech_en);

      // Special action: Option 2 (Voice Harvest Intake)
      if (key === '2' || data.action_required === 'voice_input') {
        if (this.voiceDrawer) {
          this.voiceDrawer.classList.remove('d-none');
        }
        // Play beep after prompt
        setTimeout(() => {
          this.playBeep();
        }, 1200);
      }
    })
    .catch(err => {
      console.error("IVR API error:", err);
      const fallbackHindi = `विकल्प [${key}] दर्ज किया गया। कृपया प्रतीक्षा करें।`;
      const fallbackHinglish = `Option ${key} darj kiya gaya. Kripya wait karein.`;
      const fallbackEn = `Option ${key} entered. Please wait.`;
      this.speak(fallbackHindi, fallbackHinglish, fallbackEn);
      this.setScreen(fallbackHindi);
    });
  }

  submitVoiceHarvest(cropName, quantity) {
    this.unlockAudio();
    this.appendLog("Farmer (Voice Input)", `बोला गया: "${quantity} किलो ${cropName}"`, "user");
    this.setScreen(`आवाज़ पहचानी:\n${quantity} kg ${cropName}\nसत्यापन जारी...`);

    fetch('/facilitator/api/ivr-action/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'register_harvest',
        crop_name: cropName,
        quantity_kg: quantity
      })
    })
    .then(res => res.json())
    .then(data => {
      this.setScreen(data.display);
      this.appendLog("AgriConnect IVR", data.speech, "bot");
      if (data.sms_text) {
        this.appendSMSLog(data.sms_text);
      }
      this.speak(data.speech, data.speech_hinglish, data.speech_en);

      if (this.voiceDrawer) {
        this.voiceDrawer.classList.add('d-none');
      }
    })
    .catch(err => {
      console.error("Harvest submit error:", err);
    });
  }

  initSpeechRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec) {
      this.recognition = new SpeechRec();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = 'hi-IN';

      this.recognition.onresult = (event) => {
        const text = event.results[0][0].transcript.toLowerCase();
        console.log("[IVR SpeechRecognition] Heard:", text);

        let crop = 'टमाटर (Tomato)';
        let qty = 500;

        if (text.includes('आलू') || text.includes('aalu') || text.includes('potato')) {
          crop = 'आलू (Potato)';
          qty = 300;
        } else if (text.includes('प्याज') || text.includes('pyaz') || text.includes('onion')) {
          crop = 'प्याज (Onion)';
          qty = 200;
        }

        const match = text.match(/\d+/);
        if (match) {
          qty = parseInt(match[0], 10);
        }

        this.submitVoiceHarvest(crop, qty);
      };

      this.recognition.onerror = (err) => {
        console.warn("[IVR SpeechRecognition] Error:", err);
      };
    }
  }

  toggleMicRecognition() {
    this.unlockAudio();
    if (!this.recognition) {
      alert("Microphone recognition is not supported in this browser. Please use the quick harvest buttons below.");
      return;
    }
    try {
      this.setScreen("माइक्रोफ़ोन सक्रिय...\nबोलें: '500 किलो टमाटर'...");
      this.recognition.start();
    } catch (e) {
      console.warn("Mic start error:", e);
    }
  }

  setScreen(text) {
    if (this.displayScreen) {
      this.displayScreen.innerText = text;
    }
  }

  appendLog(sender, text, type) {
    if (!this.transcriptLog) return;
    const bubble = document.createElement('div');
    bubble.className = `p-2 mb-2 rounded-3 small ${type === 'bot' ? 'bg-light border-start border-success border-3' : (type === 'user' ? 'bg-success bg-opacity-10 text-end' : 'text-muted text-center italic')}`;
    bubble.innerHTML = `<strong>${sender}:</strong> ${text}`;
    this.transcriptLog.appendChild(bubble);
    this.transcriptLog.scrollTop = this.transcriptLog.scrollHeight;
  }

  appendSMSLog(smsText) {
    if (!this.transcriptLog) return;
    const card = document.createElement('div');
    card.className = 'p-2 mb-2 rounded-3 small bg-dark text-white border-start border-warning border-3';
    card.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-1">
        <span class="badge bg-warning text-dark fw-bold" style="font-size: 0.65rem;">
          <i class="fa-solid fa-message me-1"></i> SIMULATED SMS DELIVERED
        </span>
        <small class="text-white-50" style="font-size: 0.65rem;">Just now</small>
      </div>
      <div style="font-family: monospace; font-size: 0.78rem; color: #FCD34D;">${smsText}</div>
    `;
    this.transcriptLog.appendChild(card);
    this.transcriptLog.scrollTop = this.transcriptLog.scrollHeight;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.ivrPhoneSimulator = new IVRPhoneSimulator();
});

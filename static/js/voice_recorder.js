/**
 * AgriConnect - Web Speech API Voice-to-Listing Engine
 * Enables village facilitators and low-literacy farmers to speak in Hindi or English
 * and automatically extracts Crop Name, Quantity, and Expected Price.
 */

class ProduceVoiceRecorder {
  constructor() {
    this.recognition = null;
    this.isRecording = false;
    this.lang = 'hi-IN'; // Default to Hindi; can toggle to en-IN

    this.initElements();
    this.initSpeechEngine();
  }

  initElements() {
    this.micBtn = document.getElementById('voiceMicBtn');
    this.statusText = document.getElementById('voiceStatusText');
    this.transcriptDisplay = document.getElementById('voiceTranscript');
    this.langToggle = document.getElementById('voiceLangToggle');

    if (this.micBtn) {
      this.micBtn.addEventListener('click', () => this.toggleRecording());
    }

    if (this.langToggle) {
      this.langToggle.addEventListener('change', (e) => {
        this.lang = e.target.value;
        if (this.recognition) {
          this.recognition.lang = this.lang;
        }
      });
    }
  }

  initSpeechEngine() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      if (this.statusText) {
        this.statusText.innerHTML = '<span class="text-danger"><i class="fa-solid fa-triangle-exclamation"></i> Speech Recognition not supported in this browser. Please use Google Chrome or Edge.</span>';
      }
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = this.lang;

    this.recognition.onstart = () => {
      this.isRecording = true;
      this.updateUI();
    };

    this.recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      const text = finalTranscript || interimTranscript;
      if (this.transcriptDisplay) {
        this.transcriptDisplay.innerText = `"${text}"`;
      }

      if (finalTranscript) {
        this.parseSpokenEntities(finalTranscript);
      }
    };

    this.recognition.onerror = (event) => {
      console.warn('Speech Recognition error:', event.error);
      this.isRecording = false;
      this.updateUI();
      if (this.statusText) {
        this.statusText.innerText = `Microphone notice: ${event.error}. You can also type directly into the form.`;
      }
    };

    this.recognition.onend = () => {
      this.isRecording = false;
      this.updateUI();
    };
  }

  toggleRecording() {
    if (!this.recognition) return;
    if (this.isRecording) {
      this.recognition.stop();
    } else {
      this.transcriptDisplay.innerText = 'Listening for harvest details... बोलिए...';
      this.recognition.lang = this.lang;
      this.recognition.start();
    }
  }

  updateUI() {
    if (!this.micBtn) return;
    if (this.isRecording) {
      this.micBtn.classList.add('recording-pulse');
      this.micBtn.innerHTML = '<i class="fa-solid fa-stop"></i> Stop Speaking';
      if (this.statusText) this.statusText.innerText = 'Listening... Speak crop name, quantity (kg), and price (₹)...';
    } else {
      this.micBtn.classList.remove('recording-pulse');
      this.micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> Click to Speak (बोलकर भरें)';
      if (this.statusText && !this.transcriptDisplay.innerText.includes('"')) {
        this.statusText.innerText = 'Ready. Click microphone and speak naturally (e.g. "500 kilo hybrid tamatar 25 rupaye")';
      }
    }
  }

  parseSpokenEntities(text) {
    const lower = text.toLowerCase();
    console.log("Parsing voice input:", text);

    // 1. Crop Detection
    const cropMappings = [
      { keys: ['tamatar', 'tomato', 'टमाटर'], name: 'Fresh Hybrid Tomatoes', emoji: '🍅', price: '25' },
      { keys: ['aloo', 'aalu', 'potato', 'आलू'], name: 'Kufri Jyoti Potatoes', emoji: '🥔', price: '18' },
      { keys: ['pyaz', 'pyaj', 'onion', 'प्याज'], name: 'Nashik Red Onions', emoji: '🧅', price: '28' },
      { keys: ['gobhi', 'gobi', 'cauliflower', 'गोभी'], name: 'Fresh Cauliflower', emoji: '🥦', price: '30' },
      { keys: ['mirch', 'chilli', 'mirchi', 'मिर्च'], name: 'Spicy Green Chillies', emoji: '🌶️', price: '60' },
      { keys: ['baingan', 'brinjal', 'eggplant', 'बैंगन'], name: 'Purple Brinjal', emoji: '🍆', price: '22' },
      { keys: ['bhindi', 'okra', 'ladyfinger', 'भिंडी'], name: 'Fresh Tender Okra', emoji: '🥬', price: '35' },
      { keys: ['aam', 'mango', 'आम'], name: 'Langra Mangoes', emoji: '🥭', price: '55' },
    ];

    let detectedCrop = null;
    for (const item of cropMappings) {
      for (const k of item.keys) {
        if (lower.includes(k)) {
          detectedCrop = item;
          break;
        }
      }
      if (detectedCrop) break;
    }

    // 2. Quantity Detection (e.g. "500 kilo", "400 kg", "200")
    let quantity = null;
    const qtyRegex = /(\d+)\s*(kilo|kg|quintel|quintal|क्विंटल|किलो)?/i;
    const qtyMatch = lower.match(qtyRegex);
    if (qtyMatch && qtyMatch[1]) {
      quantity = qtyMatch[1];
    }

    // 3. Price Detection (e.g. "25 rupaye", "bhav 28", "rate 30")
    let price = null;
    const priceRegex = /(bhav|rate|price|रुपये|रुपया|rs|₹)\s*(\d+)/i;
    const priceMatch = lower.match(priceRegex);
    if (priceMatch && priceMatch[2]) {
      price = priceMatch[2];
    } else {
      // Fallback: search for a second number in text if distinct from quantity
      const allNumbers = lower.match(/\b\d+\b/g);
      if (allNumbers && allNumbers.length >= 2 && allNumbers[0] === quantity) {
        price = allNumbers[1];
      }
    }

    // Populate Form Inputs with visual flash
    const nameInput = document.getElementById('id_name');
    const qtyInput = document.getElementById('id_quantity');
    const priceInput = document.getElementById('id_farmer_price');
    const emojiInput = document.getElementById('id_emoji');

    if (detectedCrop && nameInput) {
      nameInput.value = detectedCrop.name;
      this.flashHighlight(nameInput);
      if (emojiInput) emojiInput.value = detectedCrop.emoji;
      if (!price && detectedCrop.price && priceInput && !priceInput.value) {
        priceInput.value = detectedCrop.price;
        this.flashHighlight(priceInput);
      }
    }

    if (quantity && qtyInput) {
      qtyInput.value = quantity;
      this.flashHighlight(qtyInput);
    }

    if (price && priceInput) {
      priceInput.value = price;
      this.flashHighlight(priceInput);
    }

    if (this.statusText) {
      this.statusText.innerHTML = `<span class="text-success fw-bold"><i class="fa-solid fa-circle-check"></i> Processed: ${detectedCrop ? detectedCrop.name : 'Produce'} | ${quantity || '—'} kg | ₹${price || '—'}/kg</span>`;
    }

    // Trigger price breakdown calculation preview
    if (typeof window.calculateBreakdownPreview === 'function') {
      window.calculateBreakdownPreview();
    }
  }

  flashHighlight(element) {
    element.style.transition = 'all 0.3s';
    element.style.backgroundColor = '#D8F3DC';
    element.style.borderColor = '#2D6A4F';
    setTimeout(() => {
      element.style.backgroundColor = '';
      element.style.borderColor = '';
    }, 1500);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.produceVoiceRecorder = new ProduceVoiceRecorder();
});

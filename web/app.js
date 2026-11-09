let activeProjectId = null;
let currentProjectData = null;
let wizardGeneratedScenes = [];
let wizardGeneratedCaptions = {};

// ==================== TOP NAVIGATION ====================
const tabBtnGenerator = document.getElementById('tab-btn-generator');
const tabBtnHistory = document.getElementById('tab-btn-history');
const tabBtnSchedule = document.getElementById('tab-btn-schedule');
const tabBtnExport = document.getElementById('tab-btn-export');
const viewGenerator = document.getElementById('view-generator');
const viewHistory = document.getElementById('view-history');
const viewSchedule = document.getElementById('view-schedule');
const viewExport = document.getElementById('view-export');

tabBtnGenerator.addEventListener('click', () => switchTab('generator'));
tabBtnHistory.addEventListener('click', () => switchTab('history'));
tabBtnSchedule.addEventListener('click', () => switchTab('schedule'));
if (tabBtnExport) tabBtnExport.addEventListener('click', () => switchTab('export'));

function switchTab(tab) {
  [tabBtnGenerator, tabBtnHistory, tabBtnSchedule, tabBtnExport].forEach(b => b && b.classList.remove('active'));
  [viewGenerator, viewHistory, viewSchedule, viewExport].forEach(v => v && v.classList.remove('active'));

  if (tab === 'generator') {
    tabBtnGenerator.classList.add('active');
    viewGenerator.classList.add('active');
  } else if (tab === 'history') {
    tabBtnHistory.classList.add('active');
    viewHistory.classList.add('active');
    loadProjects();
  } else if (tab === 'schedule') {
    tabBtnSchedule.classList.add('active');
    viewSchedule.classList.add('active');
    loadScheduleData();
  } else if (tab === 'export') {
    if (tabBtnExport) tabBtnExport.classList.add('active');
    if (viewExport) viewExport.classList.add('active');
    loadExportData();
  }
}

// ==================== WIZARD STEP NAVIGATION ====================
function setWizardStep(stepNum) {
  for (let i = 1; i <= 4; i++) {
    const stepEl = document.getElementById(`wizard-step-${i}`);
    const nodeEl = document.getElementById(`node-${i}`);
    const lineEl = document.getElementById(`line-${i}`);

    if (stepEl) stepEl.classList.toggle('active', i === stepNum);
    if (nodeEl) {
      nodeEl.classList.toggle('active', i === stepNum);
      nodeEl.classList.toggle('completed', i < stepNum);
    }
    if (lineEl) {
      lineEl.classList.toggle('active', i < stepNum);
    }
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==================== STEP 1: TOPIK & COMPLEXITY CHECK ====================
const inputTopic = document.getElementById('input-topic');
const selectPartMode = document.getElementById('select-part-mode');
const complexityAlert = document.getElementById('complexity-alert');
const alertTitle = document.getElementById('alert-title');
const alertDesc = document.getElementById('alert-desc');

// Preset chips click
document.querySelectorAll('.chip-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    inputTopic.value = btn.dataset.topic;
    checkComplexity();
  });
});

inputTopic.addEventListener('blur', checkComplexity);

async function checkComplexity() {
  const topic = inputTopic.value.trim();
  if (!topic) return;

  try {
    const res = await fetch('/api/check-complexity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });
    const data = await res.json();
    if (data.needs_multi_part) {
      complexityAlert.classList.remove('hidden');
      alertTitle.textContent = '💡 Rekomendasi Manager: Format Multi-Part';
      alertDesc.textContent = data.reason;
      selectPartMode.value = 'multi';
    } else {
      complexityAlert.classList.add('hidden');
      selectPartMode.value = 'single';
    }
  } catch (e) {}
}

document.getElementById('btn-goto-step-2').addEventListener('click', async () => {
  const topic = inputTopic.value.trim();
  if (!topic) {
    showToast('Silakan isi topik terlebih dahulu!');
    return;
  }

  const btn = document.getElementById('btn-goto-step-2');
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '⏳ Meriset Naskah 5 Adegan...';

  const isMulti = selectPartMode.value === 'multi';
  const tone = document.getElementById('select-tone').value;

  try {
    const res = await fetch('/api/generate-script-only', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        tone: tone,
        part_num: isMulti ? 1 : null,
        total_parts: isMulti ? 2 : 1
      })
    });
    const data = await res.json();
    if (data.success) {
      wizardGeneratedScenes = data.scenes;
      wizardGeneratedCaptions = data.captions;
      renderScriptSceneList(data.scenes, data.total_words, data.est_seconds, isMulti);
      setWizardStep(2);
    } else {
      showToast('Gagal meriset naskah');
    }
  } catch (err) {
    showToast('Error: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalText;
  }
});

// ==================== STEP 2: REVIEW & EDIT NASKAH ====================
function renderScriptSceneList(scenes, words, seconds, isMulti) {
  document.getElementById('stat-word-count').textContent = `${words} Kata`;
  document.getElementById('stat-est-duration').textContent = `~${seconds} Detik (${seconds >= 45 && seconds <= 60 ? 'Ideal' : seconds < 45 ? 'Terlalu Singkat' : 'Mendekati Batas'})`;
  document.getElementById('stat-part-badge').innerHTML = `
    <span class="stat-label">Format:</span>
    <span class="stat-val text-cyan">${isMulti ? 'Part 1 dari 2' : 'Single Shorts'}</span>
  `;

  const container = document.getElementById('script-scene-list');
  container.innerHTML = '';

  scenes.forEach(s => {
    const card = document.createElement('div');
    card.className = 'scene-edit-card';
    card.innerHTML = `
      <div class="scene-edit-header">
        <span>Adegan ${s.id}</span>
        <small style="color:var(--text-dim);font-size:12px;">Bisa disesuaikan bahasanya</small>
      </div>
      <textarea id="scene-input-${s.id}" rows="3">${s.text}</textarea>
    `;
    container.appendChild(card);

    const txtArea = card.querySelector(`textarea`);
    txtArea.addEventListener('input', updateStatsFromInputs);
  });
}

function updateStatsFromInputs() {
  let totalWords = 0;
  wizardGeneratedScenes.forEach(s => {
    const el = document.getElementById(`scene-input-${s.id}`);
    if (el) {
      s.text = el.value.trim();
      totalWords += s.text.split(/\s+/).filter(Boolean).length;
    }
  });
  const estSeconds = Math.round(totalWords / 2.3);
  const statusStr = estSeconds >= 45 && estSeconds <= 60 ? 'Ideal' : (estSeconds < 45 ? 'Terlalu Singkat' : 'Mendekati Batas');
  document.getElementById('stat-word-count').textContent = `${totalWords} Kata`;
  document.getElementById('stat-est-duration').textContent = `~${estSeconds} Detik (${statusStr})`;
}

function parseAntigravityScript(raw) {
  // Matches [Adegan 1], Adegan 1, Scene 1
  const sceneRegex = /\[?(?:Adegan|Scene)\s*(\d+)\]?:?\s*\n?([\s\S]*?)(?=(?:\[?(?:Adegan|Scene)\s*\d+\]?)|$)/gi;
  let matches = [...raw.matchAll(sceneRegex)];
  if (matches.length >= 3) {
    return matches.map(m => ({
      id: parseInt(m[1]),
      text: m[2].trim()
    }));
  }
  // Fallback: split by double newlines
  const paragraphs = raw.split(/\n\s*\n/).map(p => p.trim()).filter(Boolean);
  if (paragraphs.length >= 3) {
    return paragraphs.slice(0, 5).map((p, idx) => ({
      id: idx + 1,
      text: p.replace(/^\[?(?:Adegan|Scene)\s*\d+\]?:?\s*/i, '').trim()
    }));
  }
  return null;
}

const btnApplyScript = document.getElementById('btn-apply-antigravity-script');
if (btnApplyScript) {
  btnApplyScript.addEventListener('click', () => {
    const raw = document.getElementById('input-antigravity-raw').value.trim();
    if (!raw) {
      showToast('⚠️ Tempel naskah dari chat Antigravity terlebih dahulu!');
      return;
    }
    const parsed = parseAntigravityScript(raw);
    if (!parsed || parsed.length === 0) {
      showToast('⚠️ Format naskah tidak dikenali. Pastikan ada tanda [Adegan 1] s/d [Adegan 5].');
      return;
    }

    wizardGeneratedScenes = parsed.map(p => {
      const existing = wizardGeneratedScenes.find(s => s.id === p.id) || {};
      return {
        ...existing,
        id: p.id,
        text: p.text
      };
    });

    const totalWords = wizardGeneratedScenes.reduce((acc, s) => acc + s.text.split(/\s+/).filter(Boolean).length, 0);
    const estSeconds = Math.round(totalWords / 2.3);
    const isMulti = document.getElementById('select-part-mode').value === 'multi';

    renderScriptSceneList(wizardGeneratedScenes, totalWords, estSeconds, isMulti);
    showToast(`✅ Naskah Antigravity diterapkan! (${totalWords} kata, ~${estSeconds} detik)`);
  });
}

document.getElementById('btn-backto-step-1').addEventListener('click', () => setWizardStep(1));

document.getElementById('btn-goto-step-3').addEventListener('click', () => {
  // Update wizardGeneratedScenes with any user edits
  wizardGeneratedScenes.forEach(s => {
    const inputEl = document.getElementById(`scene-input-${s.id}`);
    if (inputEl) s.text = inputEl.value.trim();
  });

  // Populate Teleprompter Reading Text
  const fullText = wizardGeneratedScenes.map(s => `[Adegan ${s.id}]\n${s.text}`).join('\n\n');
  document.getElementById('teleprompter-content').textContent = fullText;

  setWizardStep(3);
});

// ==================== STEP 3: AUDIO SELECTION ====================
const radioAudioModes = document.querySelectorAll('input[name="audio-mode"]');
const boxUploadFile = document.getElementById('box-upload-file');
const boxAiPicker = document.getElementById('box-ai-picker');
const fileInputStep3 = document.getElementById('step3-voice-file');
const fileLabelStep3 = document.getElementById('file-chosen-label');

radioAudioModes.forEach(r => {
  r.addEventListener('change', () => {
    if (r.value === 'custom') {
      boxUploadFile.classList.remove('hidden');
      boxAiPicker.classList.add('hidden');
    } else {
      boxUploadFile.classList.add('hidden');
      boxAiPicker.classList.remove('hidden');
    }
  });
});

fileInputStep3.addEventListener('change', (e) => {
  if (e.target.files[0]) {
    fileLabelStep3.textContent = `✅ File dipilih: ${e.target.files[0].name} (${(e.target.files[0].size/1024/1024).toFixed(1)} MB)`;
    fileLabelStep3.style.color = '#00ffaa';
  }
});

document.getElementById('btn-copy-prompter').addEventListener('click', () => {
  const text = document.getElementById('teleprompter-content').textContent;
  navigator.clipboard.writeText(text).then(() => {
    showToast('📖 Teks naskah disalin ke clipboard!');
  });
});

document.getElementById('btn-backto-step-2').addEventListener('click', () => setWizardStep(2));

// ==================== STEP 4: RENDER & SOCIAL KIT ====================
document.getElementById('btn-start-render').addEventListener('click', async () => {
  const topic = inputTopic.value.trim();
  const tone = document.getElementById('select-tone').value;
  const isMulti = selectPartMode.value === 'multi';
  const audioMode = document.querySelector('input[name="audio-mode"]:checked').value;
  
  let audioBase64 = null;
  let voiceModel = 'id-ID-ArdiNeural';

  if (audioMode === 'custom') {
    if (!fileInputStep3.files[0]) {
      showToast('⚠️ Silakan pilih file rekaman suara HP kamu terlebih dahulu, atau pilih opsi "Voiceover AI Sementara"');
      return;
    }
    audioBase64 = await toBase64(fileInputStep3.files[0]);
  } else {
    voiceModel = document.getElementById('step3-select-ai-voice').value;
  }

  setWizardStep(4);
  const progressEl = document.getElementById('wizard-render-progress');
  const resultEl = document.getElementById('wizard-render-result');
  progressEl.classList.remove('hidden');
  resultEl.classList.add('hidden');

  const titleProgress = document.getElementById('wizard-progress-title');
  const subProgress = document.getElementById('wizard-progress-sub');
  const wizFill = document.getElementById('wizard-progress-fill');
  const wizPct = document.getElementById('wizard-progress-percent');
  const wizStatus = document.getElementById('wizard-progress-status-text');

  let wizCurrent = 5;
  if (wizFill) wizFill.style.width = '5%';
  if (wizPct) wizPct.textContent = '5%';
  if (wizStatus) wizStatus.textContent = 'Memulai proses...';

  titleProgress.textContent = 'Membuat 5 Ilustrasi Visual 9:16...';
  subProgress.textContent = 'Menghasilkan gambar AI dan thumbnail "KENAPA" berkualitas tinggi.';

  const wizInterval = setInterval(() => {
    if (wizCurrent < 25) {
      wizCurrent += 3;
      if (wizStatus) wizStatus.textContent = '1/4. Meriset & menyusun naskah...';
    } else if (wizCurrent < 55) {
      wizCurrent += 2;
      if (wizStatus) wizStatus.textContent = '2/4. Membuat visual AI & stiker cover...';
      titleProgress.textContent = 'Memproses Audio & Subtitle...';
      subProgress.textContent = 'Menyesuaikan timing jeda napas pembiara.';
    } else if (wizCurrent < 85) {
      wizCurrent += 2;
      if (wizStatus) wizStatus.textContent = '3/4. Animasi Ken Burns & audio mastering...';
      titleProgress.textContent = 'Merender Video MP4 (FFmpeg)...';
      subProgress.textContent = 'Menggabungkan animasi zoom Ken Burns, audio, dan font tebal.';
    } else if (wizCurrent < 96) {
      wizCurrent += 1;
      if (wizStatus) wizStatus.textContent = '4/4. Burning subtitle & kompresi video...';
    }
    if (wizFill) wizFill.style.width = `${wizCurrent}%`;
    if (wizPct) wizPct.textContent = `${wizCurrent}%`;
  }, 600);

  try {
    const res = await fetch('/api/generate-full', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        tone: tone,
        voice: voiceModel,
        part_num: isMulti ? 1 : null,
        total_parts: isMulti ? 2 : 1,
        scenes: wizardGeneratedScenes,
        audio_base64: audioBase64
      })
    });
    const result = await res.json();
    clearInterval(wizInterval);
    if (wizFill) wizFill.style.width = '100%';
    if (wizPct) wizPct.textContent = '100%';

    progressEl.classList.add('hidden');

    if (result.success) {
      resultEl.classList.remove('hidden');
      currentProjectData = result.project;
      
      document.getElementById('result-title').textContent = result.project.title;
      
      const vid = document.getElementById('wizard-result-video');
      vid.src = `/media/${result.project_id}/output/final_shorts.mp4?t=${Date.now()}`;
      vid.load();
      vid.play().catch(() => {});

      const thumbImg = document.getElementById('wizard-result-thumb');
      thumbImg.src = `/media/${result.project_id}/thumbnail.jpg?t=${Date.now()}`;
      document.getElementById('btn-download-thumb').href = `/media/${result.project_id}/thumbnail.jpg`;

      // Set multiplatform captions
      wizardGeneratedCaptions = result.project.social_kit || {};
      setActivePlatformCaption('youtube', wizardGeneratedCaptions);
      showToast('🎉 Video shorts, Thumbnail, dan Caption berhasil dibuat!');
    } else {
      showToast('❌ Gagal render: ' + (result.error || 'Terjadi kesalahan'));
    }
  } catch (err) {
    progressEl.classList.add('hidden');
    showToast('❌ Error: ' + err.message);
  }
});

// Platform Caption Switching
const socTabBtns = document.querySelectorAll('.soc-tab-btn');
socTabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    socTabBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    setActivePlatformCaption(btn.dataset.platform, wizardGeneratedCaptions);
  });
});

function setActivePlatformCaption(platform, kit) {
  const label = document.getElementById('caption-platform-label');
  const textarea = document.getElementById('platform-caption-text');
  
  const platformNames = {
    youtube: '🔴 YouTube Shorts (Penjelasan Mendalam & SEO)',
    tiktok: '🎵 TikTok (Catchy & Poin Rangkuman)',
    instagram: '📸 Instagram Reels (Estetik & Save/Share CTA)',
    facebook: '🔵 Facebook Reels (Storytelling Komunitas)'
  };

  label.textContent = platformNames[platform] || platform;
  textarea.value = kit[platform] || '';
}

document.getElementById('btn-copy-platform-caption').addEventListener('click', () => {
  const text = document.getElementById('platform-caption-text').value;
  if (!text) return;

  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById('btn-copy-platform-caption');
    const original = btn.innerHTML;
    btn.innerHTML = '✅ Tersalin!';
    showToast('📋 Caption platform berhasil disalin!');
    setTimeout(() => btn.innerHTML = original, 2000);
  });
});

document.getElementById('btn-create-another').addEventListener('click', () => {
  inputTopic.value = '';
  complexityAlert.classList.add('hidden');
  setWizardStep(1);
});

document.getElementById('btn-add-to-schedule').addEventListener('click', () => {
  const modal = document.getElementById('modal-schedule');
  document.getElementById('sched-topic').value = currentProjectData ? currentProjectData.title : inputTopic.value;
  document.getElementById('sched-date').value = new Date().toISOString().split('T')[0];
  modal.classList.remove('hidden');
});

// ==================== TAB 2: RIWAYAT / HISTORY LOGIC ====================
async function loadProjects() {
  try {
    const res = await fetch('/api/projects');
    const projects = await res.json();
    
    document.getElementById('project-count').textContent = projects.length;
    document.getElementById('history-badge').textContent = projects.length;
    const listContainer = document.getElementById('project-list');
    listContainer.innerHTML = '';

    if (projects.length === 0) {
      listContainer.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">Belum ada project.</p>';
      return;
    }

    projects.forEach((proj, idx) => {
      const card = document.createElement('div');
      card.className = `project-card ${proj.id === activeProjectId ? 'active' : ''}`;
      card.id = `proj-card-${proj.id}`;
      
      const statusTag = proj.has_video 
        ? '<span class="tag-ready">● Siap Tonton</span>'
        : '<span class="tag-pending">○ Draft</span>';

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
          <h4 style="margin:0; flex:1;">${proj.title}</h4>
          <button class="btn-card-del" title="Hapus project ini" onclick="event.stopPropagation(); confirmDeleteProject('${proj.id}')" style="background:none; border:none; color:rgba(255,255,255,0.3); cursor:pointer; font-size:14px; padding:2px 4px; border-radius:4px;" onmouseover="this.style.color='#ff5252'" onmouseout="this.style.color='rgba(255,255,255,0.3)'">🗑️</button>
        </div>
        <div class="project-meta">
          <span>${proj.scenes_count} Scene</span>
          ${statusTag}
        </div>
      `;

      card.addEventListener('click', () => selectProject(proj.id));
      listContainer.appendChild(card);

      if (idx === 0 && !activeProjectId) {
        selectProject(proj.id);
      }
    });
  } catch (err) {
    showToast('Gagal memuat daftar project: ' + err.message);
  }
}

async function confirmDeleteProject(projectId) {
  if (!confirm(`Hapus project '${projectId}' secara permanen? Data video, gambar, dan naskah akan dibersihkan.`)) {
    return;
  }
  try {
    const res = await fetch(`/api/projects/${projectId}/delete`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(`🗑️ Project '${projectId}' berhasil dibersihkan!`);
      if (activeProjectId === projectId) {
        activeProjectId = null;
        document.getElementById('hero-title').textContent = 'Pilih Project di Sisi Kiri';
        document.getElementById('hero-desc').textContent = 'Buka project untuk meninjau adegan, mendengarkan audio, atau ganti dengan suara sendiri.';
        document.getElementById('btn-history-render').disabled = true;
        document.getElementById('btn-history-upload-voice').disabled = true;
        const delBtn = document.getElementById('btn-history-delete');
        if (delBtn) delBtn.disabled = true;
        const video = document.getElementById('video-player');
        video.style.display = 'none';
        document.getElementById('player-placeholder').classList.remove('hidden');
        document.getElementById('scene-container').innerHTML = '';
      }
      loadProjects();
    } else {
      showToast('❌ Gagal menghapus: ' + (data.error || 'Terjadi kesalahan'));
    }
  } catch (err) {
    showToast('❌ Error: ' + err.message);
  }
}

async function selectProject(projectId) {
  activeProjectId = projectId;

  document.querySelectorAll('.project-card').forEach(el => el.classList.remove('active'));
  const activeCard = document.getElementById(`proj-card-${projectId}`);
  if (activeCard) activeCard.classList.add('active');

  try {
    const res = await fetch(`/api/projects/${projectId}`);
    const data = await res.json();

    document.getElementById('hero-topic').textContent = data.topic || 'Sains & Overthinking';
    document.getElementById('hero-title').textContent = data.title;
    document.getElementById('hero-desc').textContent = `ID Project: ${data.id} | Voice: ${data.voice || 'id-ID-ArdiNeural'}`;
    document.getElementById('scenes-badge').textContent = `${data.scenes ? data.scenes.length : 0} Adegan`;

    const renderBtn = document.getElementById('btn-history-render');
    renderBtn.disabled = false;
    renderBtn.onclick = () => triggerRenderHistory(projectId);

    const uploadVoiceBtn = document.getElementById('btn-history-upload-voice');
    uploadVoiceBtn.disabled = false;
    uploadVoiceBtn.onclick = () => document.getElementById('history-voice-file-input').click();

    const deleteBtn = document.getElementById('btn-history-delete');
    if (deleteBtn) {
      deleteBtn.disabled = false;
      deleteBtn.onclick = () => confirmDeleteProject(projectId);
    }

    // Video Player
    const video = document.getElementById('video-player');
    const placeholder = document.getElementById('player-placeholder');
    video.src = `/media/${projectId}/output/final_shorts.mp4?t=${Date.now()}`;
    video.style.display = 'block';
    placeholder.classList.add('hidden');
    video.load();

    // Thumbnail
    const thumbEl = document.getElementById('history-thumb-img');
    thumbEl.src = `/media/${projectId}/thumbnail.jpg?t=${Date.now()}`;

    // Captions in History
    setupHistoryCaptions(data.social_kit || {});

    // Scenes
    const sceneContainer = document.getElementById('scene-container');
    sceneContainer.innerHTML = '';
    (data.scenes || []).forEach(scene => {
      const sceneCard = document.createElement('div');
      sceneCard.className = 'scene-card';
      const thumbUrl = `/media/${projectId}/${scene.image}`;
      let subChips = (scene.subtitles || []).map(sub => `
        <span class="sub-chip ${sub.highlight ? 'highlight' : ''}">
          ${sub.text.replace(/\\n/g, ' ')}
        </span>
      `).join('');

      sceneCard.innerHTML = `
        <div class="scene-thumb"><img src="${thumbUrl}" alt="Scene ${scene.id}"></div>
        <div class="scene-body">
          <div class="scene-header"><span class="scene-tag">Scene ${scene.id}</span></div>
          <p class="scene-text">"${scene.text}"</p>
          <div class="subtitle-chips">${subChips}</div>
        </div>
      `;
      sceneContainer.appendChild(sceneCard);
    });

  } catch (err) {
    showToast('Gagal memuat detail project: ' + err.message);
  }
}

function setupHistoryCaptions(kit) {
  const tabs = document.querySelectorAll('#history-social-tabs .soc-tab-btn');
  const label = document.getElementById('history-caption-label');
  const textarea = document.getElementById('history-caption-text');

  function updateView(platform) {
    label.textContent = platform.toUpperCase();
    textarea.value = kit[platform] || '';
  }

  tabs.forEach(btn => {
    btn.onclick = () => {
      tabs.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      updateView(btn.dataset.platform);
    };
  });

  updateView('youtube');

  document.getElementById('btn-history-copy-caption').onclick = () => {
    navigator.clipboard.writeText(textarea.value).then(() => {
      showToast('📋 Caption disalin!');
    });
  };
}

// Progress Bar Controller for History Render & Voice Upload
function startHistoryProgress(statusTitle = 'Processing...') {
  const box = document.getElementById('history-render-progress');
  const fill = document.getElementById('history-progress-fill');
  const txt = document.getElementById('history-progress-text');
  const pct = document.getElementById('history-progress-percent');
  const btnRender = document.getElementById('btn-history-render');
  const btnVoice = document.getElementById('btn-history-upload-voice');

  if (!box) return { finish: () => {}, fail: () => {} };

  box.classList.remove('hidden');
  if (btnRender) btnRender.disabled = true;
  if (btnVoice) btnVoice.disabled = true;

  let currentPct = 5;
  fill.style.width = '5%';
  pct.textContent = '5%';
  txt.textContent = statusTitle;

  const interval = setInterval(() => {
    if (currentPct < 25) {
      currentPct += 4;
      txt.textContent = 'Membersihkan noise & potong 2s hening...';
    } else if (currentPct < 55) {
      currentPct += 3;
      txt.textContent = 'Mendeteksi jeda napas & auto-sync adegan...';
    } else if (currentPct < 85) {
      currentPct += 2;
      txt.textContent = 'Merender animasi visual & Ken Burns...';
    } else if (currentPct < 96) {
      currentPct += 1;
      txt.textContent = 'Burning subtitle & mixing audio MP4...';
    }
    fill.style.width = `${currentPct}%`;
    pct.textContent = `${currentPct}%`;
  }, 500);

  return {
    finish: (msg = '🎉 Selesai!') => {
      clearInterval(interval);
      fill.style.width = '100%';
      pct.textContent = '100%';
      txt.textContent = msg;
      setTimeout(() => {
        box.classList.add('hidden');
        fill.style.width = '0%';
        if (btnRender) btnRender.disabled = false;
        if (btnVoice) btnVoice.disabled = false;
      }, 1500);
    },
    fail: (errMsg = 'Gagal') => {
      clearInterval(interval);
      fill.style.width = '100%';
      fill.style.background = '#ff4d4d';
      pct.textContent = 'Error';
      txt.textContent = '❌ ' + errMsg;
      setTimeout(() => {
        box.classList.add('hidden');
        fill.style.width = '0%';
        fill.style.background = '';
        if (btnRender) btnRender.disabled = false;
        if (btnVoice) btnVoice.disabled = false;
      }, 4000);
    }
  };
}

// Upload Voice and Auto-Sync in History
document.getElementById('history-voice-file-input').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file || !activeProjectId) return;

  const progress = startHistoryProgress('Mengupload rekaman suara...');
  showToast('🎙️ Mengupload rekaman suara & memproses audio...');
  try {
    const base64 = await toBase64(file);
    const res = await fetch(`/api/upload-voice/${activeProjectId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename: file.name, audio_base64: base64 })
    });
    const data = await res.json();
    if (data.success) {
      progress.finish('🎉 Selesai! Memuat ulang halaman...');
      showToast('🎉 Suara berhasil diganti & disinkronkan! Memperbarui halaman...');
      sessionStorage.setItem('activeProjectId', activeProjectId);
      setTimeout(() => {
        window.location.reload();
      }, 1200);
    } else {
      progress.fail(data.error || 'Gagal memproses audio');
      showToast('❌ Error: ' + (data.error || 'Gagal'));
    }
  } catch (err) {
    progress.fail(err.message);
    showToast('❌ Error: ' + err.message);
  }
});

async function triggerRenderHistory(projectId) {
  const progress = startHistoryProgress('Merender ulang video...');
  showToast('⏳ Merender ulang video...');
  try {
    const res = await fetch(`/api/render/${projectId}`, { method: 'POST' });
    const result = await res.json();
    if (result.success) {
      progress.finish('🎉 Selesai! Memuat ulang halaman...');
      showToast('🎉 Video berhasil dirender! Memperbarui halaman...');
      sessionStorage.setItem('activeProjectId', projectId);
      setTimeout(() => {
        window.location.reload();
      }, 1200);
    } else {
      progress.fail(result.error || 'Gagal merender');
      showToast('❌ ' + (result.error || 'Gagal merender'));
    }
  } catch (err) {
    progress.fail(err.message);
    showToast('❌ Error: ' + err.message);
  }
}

// ==================== TAB 3: JADWAL & MANAGER LOGIC ====================
async function loadScheduleData() {
  try {
    const res = await fetch('/api/schedule');
    const data = await res.json();
    const list = document.getElementById('schedule-items-list');
    list.innerHTML = '';

    if (!data.items || data.items.length === 0) {
      list.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">Belum ada jadwal konten terencana.</p>';
      return;
    }

    data.items.forEach(it => {
      const card = document.createElement('div');
      card.className = 'schedule-item-card';

      let statusBadge = '<span class="schedule-status-badge status-ready">Siap Post</span>';
      if (it.status === 'posted') {
        statusBadge = '<span class="schedule-status-badge status-posted">Sudah Terposting</span>';
      } else if (it.status === 'planned') {
        statusBadge = '<span class="schedule-status-badge status-planned">Rencana</span>';
      }

      card.innerHTML = `
        <div class="schedule-item-info">
          <h4>${it.topic}</h4>
          <p>📅 ${it.target_date} &bull; ⏰ ${it.target_time} &bull; ${it.platforms.join(', ')}</p>
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
          ${statusBadge}
          ${it.status !== 'posted' ? `<button class="btn-ghost-small" onclick="markPosted('${it.id}')">Tandai Terposting</button>` : ''}
        </div>
      `;
      list.appendChild(card);
    });
  } catch (err) {
    showToast('Gagal memuat jadwal: ' + err.message);
  }
}

async function markPosted(itemId) {
  try {
    await fetch('/api/schedule/update-status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId, status: 'posted' })
    });
    showToast('✅ Status konten diperbarui: Sudah Terposting');
    loadScheduleData();
  } catch (e) {}
}

// Schedule Modal
const schedModal = document.getElementById('modal-schedule');
document.getElementById('btn-add-schedule-modal').addEventListener('click', () => {
  document.getElementById('sched-date').value = new Date().toISOString().split('T')[0];
  schedModal.classList.remove('hidden');
});
document.getElementById('btn-close-schedule-modal').addEventListener('click', () => schedModal.classList.add('hidden'));
document.getElementById('btn-cancel-schedule').addEventListener('click', () => schedModal.classList.add('hidden'));

document.getElementById('form-schedule').addEventListener('submit', async (e) => {
  e.preventDefault();
  const topic = document.getElementById('sched-topic').value;
  const target_date = document.getElementById('sched-date').value;
  const target_time = document.getElementById('sched-time').value;

  try {
    await fetch('/api/schedule/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, target_date, target_time })
    });
    showToast('📅 Berhasil ditambahkan ke Jadwal Posting!');
    schedModal.classList.add('hidden');
    switchTab('schedule');
  } catch (err) {
    showToast('Error: ' + err.message);
  }
});

// Utilities
function toBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = error => reject(error);
  });
}

function showToast(message) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 4000);
}

document.getElementById('btn-refresh').addEventListener('click', () => {
  loadProjects();
  loadScheduleData();
  loadExportData();
  showToast('Data diperbarui');
});

// ==================== TAB 4: EXPORT KE HP LOGIC ====================
let exportProjectsData = [];
let selectedExportIds = new Set();
let cachedPhoneInfo = null;

async function loadExportData() {
  const listEl = document.getElementById('export-projects-list');
  const badgeEl = document.getElementById('export-badge');
  const phoneAlert = document.getElementById('export-phone-alert');
  const phoneTitle = document.getElementById('export-phone-title');
  const phoneDesc = document.getElementById('export-phone-desc');
  const phoneBadge = document.getElementById('export-phone-status-badge');
  const destInput = document.getElementById('export-dest-input');

  if (!listEl) return;

  try {
    const res = await fetch('/api/exporter/status');
    const data = await res.json();
    cachedPhoneInfo = data.phone;
    exportProjectsData = data.projects || [];

    if (badgeEl) badgeEl.textContent = exportProjectsData.length;
    const totalCountEl = document.getElementById('total-export-count');
    if (totalCountEl) totalCountEl.textContent = exportProjectsData.length;

    // Update Phone Connection UI
    if (data.phone && data.phone.connected) {
      if (phoneBadge) {
        phoneBadge.className = 'status-pill ready';
        phoneBadge.innerHTML = '<span class="dot"></span> HP Terhubung';
      }
      if (phoneTitle) phoneTitle.textContent = `🟢 Terdeteksi: ${data.phone.phone_name}`;
      if (phoneDesc) phoneDesc.textContent = `Folder tujuan HP siap di: ${data.phone.target_path}`;
      if (destInput && (!destInput.value || destInput.value.includes('export_siap_posting'))) {
        destInput.value = data.phone.target_path;
      }
    } else {
      if (phoneBadge) {
        phoneBadge.className = 'status-pill';
        phoneBadge.style.color = '#ffaa00';
        phoneBadge.innerHTML = '<span class="dot" style="background:#ffaa00"></span> Belum Tercolok';
      }
      if (phoneTitle) phoneTitle.textContent = '⚠️ HP Android (MTP) Belum Terhubung via USB (MTP)';
      if (phoneDesc) phoneDesc.textContent = 'Colokkan HP via USB dengan mode "Transfer File", atau kamu bisa tetap gunakan path tujuan di bawah ini / folder lokal.';
      if (destInput && !destInput.value) {
        destInput.value = data.phone?.target_path || data.phone?.local_fallback;
      }
    }

    // Default select all projects if empty
    if (selectedExportIds.size === 0) {
      exportProjectsData.forEach(p => selectedExportIds.add(p.id));
    }

    renderExportProjects();
  } catch (err) {
    if (listEl) listEl.innerHTML = `<div class="error-state">Gagal memuat status export: ${err.message}</div>`;
  }
}

function renderExportProjects() {
  const listEl = document.getElementById('export-projects-list');
  const searchInput = document.getElementById('export-search-input');
  const query = (searchInput?.value || '').toLowerCase().trim();

  if (!listEl) return;

  const filtered = exportProjectsData.filter(p => {
    return p.id.toLowerCase().includes(query) || (p.title || '').toLowerCase().includes(query);
  });

  if (filtered.length === 0) {
    listEl.innerHTML = '<div class="empty-state">Tidak ada project yang cocok dengan pencarian.</div>';
    updateExportSummary();
    return;
  }

  listEl.innerHTML = filtered.map(p => {
    const isSelected = selectedExportIds.has(p.id);
    const memesCount = p.files ? p.files.filter(f => f.is_meme).length : 0;
    const captionsCount = p.files ? p.files.filter(f => f.is_caption).length : 0;

    return `
      <div class="export-project-item ${isSelected ? 'selected' : ''}" data-id="${p.id}">
        <input type="checkbox" class="export-checkbox" ${isSelected ? 'checked' : ''} data-id="${p.id}">
        <div class="export-info">
          <div class="export-item-id">ID: ${p.id}</div>
          <div class="export-item-title" title="${p.title}">${p.title}</div>
          <div class="export-item-badges">
            <span class="export-mini-badge">🎬 1 Video</span>
            <span class="export-mini-badge">🖼️ ${memesCount} Meme</span>
            <span class="export-mini-badge">📝 ${captionsCount} Caption</span>
            <span class="export-mini-badge size">💾 ${p.size_mb} MB</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Attach click listeners to cards & checkboxes
  listEl.querySelectorAll('.export-project-item').forEach(item => {
    item.addEventListener('click', (e) => {
      const pid = item.dataset.id;
      const chk = item.querySelector('.export-checkbox');
      if (e.target !== chk) {
        chk.checked = !chk.checked;
      }
      if (chk.checked) {
        selectedExportIds.add(pid);
        item.classList.add('selected');
      } else {
        selectedExportIds.delete(pid);
        item.classList.remove('selected');
      }
      updateExportSummary();
    });
  });

  updateExportSummary();
}

function updateExportSummary() {
  let count = 0;
  let totalBytes = 0;

  exportProjectsData.forEach(p => {
    if (selectedExportIds.has(p.id)) {
      count++;
      totalBytes += (p.size_bytes || 0);
    }
  });

  const totalMb = (totalBytes / (1024 * 1024)).toFixed(1);
  const summaryText = `${count} project dipilih (${totalMb} MB)`;

  const sumEl = document.getElementById('export-selected-summary');
  if (sumEl) sumEl.textContent = summaryText;

  const floatCountEl = document.getElementById('export-floating-count');
  if (floatCountEl) floatCountEl.textContent = `${count} Project`;

  const floatSizeEl = document.getElementById('export-floating-size');
  if (floatSizeEl) floatSizeEl.textContent = `(${totalMb} MB)`;

  const runBtn = document.getElementById('btn-run-export');
  if (runBtn) {
    runBtn.disabled = count === 0;
  }
}

// Search & filter
const exportSearchInput = document.getElementById('export-search-input');
if (exportSearchInput) {
  exportSearchInput.addEventListener('input', renderExportProjects);
}

// Select / Deselect All
const btnSelectAll = document.getElementById('btn-select-all-export');
if (btnSelectAll) {
  btnSelectAll.addEventListener('click', () => {
    exportProjectsData.forEach(p => selectedExportIds.add(p.id));
    renderExportProjects();
  });
}

const btnDeselectAll = document.getElementById('btn-deselect-all-export');
if (btnDeselectAll) {
  btnDeselectAll.addEventListener('click', () => {
    selectedExportIds.clear();
    renderExportProjects();
  });
}

// Reset destination buttons
const btnResetPhone = document.getElementById('btn-reset-phone-dest');
if (btnResetPhone) {
  btnResetPhone.addEventListener('click', () => {
    const destInput = document.getElementById('export-dest-input');
    if (cachedPhoneInfo && destInput) {
      destInput.value = cachedPhoneInfo.target_path;
      showToast('Path tujuan di-reset ke HP Android (MTP)');
    }
  });
}

const btnUseLocal = document.getElementById('btn-use-local-dest');
if (btnUseLocal) {
  btnUseLocal.addEventListener('click', () => {
    const destInput = document.getElementById('export-dest-input');
    if (cachedPhoneInfo && destInput) {
      destInput.value = cachedPhoneInfo.local_fallback;
      showToast('Path tujuan diatur ke folder lokal komputer');
    }
  });
}

// Run 1-Click Export
const btnRunExport = document.getElementById('btn-run-export');
if (btnRunExport) {
  btnRunExport.addEventListener('click', async () => {
    const destInput = document.getElementById('export-dest-input');
    const destination = (destInput?.value || '').trim();

    if (selectedExportIds.size === 0) {
      showToast('Pilih minimal 1 project untuk diexport!');
      return;
    }

    if (!destination) {
      showToast('Folder tujuan tidak boleh kosong!');
      return;
    }

    const progressPanel = document.getElementById('export-progress-panel');
    const progressBar = document.getElementById('export-progress-bar');
    const progressPct = document.getElementById('export-progress-pct');
    const progressTitle = document.getElementById('export-progress-title');
    const logBox = document.getElementById('export-log-box');

    progressPanel.classList.remove('hidden');
    progressBar.style.width = '10%';
    progressPct.textContent = 'Memulai...';
    progressTitle.textContent = `⏳ Menyalin ${selectedExportIds.size} project ke HP...`;
    logBox.innerHTML = `<div>🚀 Memulai pengiriman ke: <code>${destination}</code></div>`;
    btnRunExport.disabled = true;

    try {
      progressBar.style.width = '40%';
      const res = await fetch('/api/exporter/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_ids: Array.from(selectedExportIds),
          destination: destination
        })
      });

      const report = await res.json();

      if (!res.ok || !report.success) {
        throw new Error(report.error || 'Terjadi kesalahan saat menyalin file');
      }

      progressBar.style.width = '100%';
      progressPct.textContent = '100% Selesai';
      progressTitle.textContent = `🎉 Berhasil! ${report.total_projects} Project Disalin ke HP`;

      let logHtml = `<div class="log-success">✅ Berhasil menyalin ${report.total_projects} project (${report.total_files} file / ${report.total_mb} MB)!</div>`;
      logHtml += `<div>📁 Lokasi: <code>${report.destination}</code></div><br>`;

      report.details.forEach(d => {
        if (d.success) {
          logHtml += `<div class="log-success">✓ [${d.data.project_id}]: ${d.data.copied_count} file (${d.data.total_mb} MB) siap posting</div>`;
        } else {
          logHtml += `<div class="log-err">✗ [${d.project_id}]: Gagal - ${d.error}</div>`;
        }
      });

      logBox.innerHTML = logHtml;
      showToast(`🎉 Sukses! ${report.total_files} file siap diposting langsung dari HP!`);
    } catch (err) {
      progressBar.style.width = '100%';
      progressBar.style.background = '#ff5252';
      progressPct.textContent = 'Gagal';
      progressTitle.textContent = '❌ Pengiriman Gagal';
      logBox.innerHTML += `<div class="log-err">Error: ${err.message}</div>`;
      showToast('Export gagal: ' + err.message);
    } finally {
      btnRunExport.disabled = false;
    }
  });
}

// Initial load & restore active project if reloaded
(async function init() {
  const savedProjectId = sessionStorage.getItem('activeProjectId');
  if (savedProjectId) {
    activeProjectId = savedProjectId;
    sessionStorage.removeItem('activeProjectId');
    switchTab('history');
  }
  await loadProjects();
  if (savedProjectId) {
    selectProject(savedProjectId);
  }
})();

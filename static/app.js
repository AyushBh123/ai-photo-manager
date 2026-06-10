const outputArea = document.getElementById('outputArea');
const healthButton = document.getElementById('healthButton');
const scanButton = document.getElementById('scanButton');
const googlePhotosButton = document.getElementById('googlePhotosButton');
const searchButton = document.getElementById('searchButton');
const imagesButton = document.getElementById('imagesButton');
const duplicatesButton = document.getElementById('duplicatesButton');
const facesButton = document.getElementById('facesButton');
const scanPathInput = document.getElementById('scanPath');
const googleClientSecretsPathInput = document.getElementById('googleClientSecretsPath');
const googleTokenPathInput = document.getElementById('googleTokenPath');
const searchQueryInput = document.getElementById('searchQuery');

const actionButtons = [
  healthButton,
  scanButton,
  googlePhotosButton,
  searchButton,
  imagesButton,
  duplicatesButton,
  facesButton,
].filter(Boolean);

function renderOutput(data) {
  outputArea.textContent = JSON.stringify(data, null, 2);
}

function renderError(error) {
  outputArea.textContent = `Error: ${error.message || error}`;
}

function setBusy(button, busy, label) {
  if (!button) {
    return;
  }
  button.disabled = busy;
  button.textContent = busy ? label : button.dataset.defaultLabel || label;
}

function setAllButtonsBusy(busy, activeButton, label) {
  actionButtons.forEach((button) => {
    if (!button) {
      return;
    }
    if (!button.dataset.defaultLabel) {
      button.dataset.defaultLabel = button.textContent || '';
    }
    if (button === activeButton) {
      setBusy(button, busy, label);
      return;
    }
    button.disabled = busy;
  });
}

async function callApi(path, options = {}, busyButton = null, busyLabel = 'Working…') {
  outputArea.textContent = busyLabel;
  setAllButtonsBusy(true, busyButton, busyLabel);
  try {
    const response = await fetch(path, options);
    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`${response.status} ${response.statusText}: ${errorBody}`);
    }
    const data = await response.json();
    renderOutput(data);
  } catch (error) {
    renderError(error);
  } finally {
    setAllButtonsBusy(false, busyButton, busyLabel);
  }
}

healthButton?.addEventListener('click', () => callApi('/health', {}, healthButton, 'Checking health…'));
scanButton?.addEventListener('click', () => {
  const path = scanPathInput.value.trim();
  if (!path) {
    renderError(new Error('Please enter a folder path to scan.'));
    return;
  }
  callApi('/scan/local', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ paths: [path] }),
  }, scanButton, 'Scanning folder…');
});

googlePhotosButton?.addEventListener('click', () => {
  const clientSecretsPath = googleClientSecretsPathInput.value.trim();
  const tokenPath = googleTokenPathInput.value.trim() || 'data/google_photos_token.json';
  if (!clientSecretsPath) {
    renderError(new Error('Please enter a Google Photos client secrets path.'));
    return;
  }
  callApi('/connect/google-photos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_secrets_path: clientSecretsPath,
      token_path: tokenPath,
    }),
  }, googlePhotosButton, 'Syncing Google Photos…');
});

searchButton?.addEventListener('click', () => {
  const query = searchQueryInput.value.trim();
  if (!query) {
    renderError(new Error('Please enter a search query.'));
    return;
  }
  callApi('/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_n: 10 }),
  }, searchButton, 'Searching…');
});
imagesButton?.addEventListener('click', () => callApi('/images?limit=20', {}, imagesButton, 'Loading images…'));
duplicatesButton?.addEventListener('click', () => callApi('/duplicates', {}, duplicatesButton, 'Finding duplicates…'));
facesButton?.addEventListener('click', () => callApi('/face-groups', {}, facesButton, 'Grouping faces…'));

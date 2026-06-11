const search = document.querySelector("#search");
const groupFilter = document.querySelector("#groupFilter");
const countryFilter = document.querySelector("#countryFilter");
const channelsEl = document.querySelector("#channels");
const summaryEl = document.querySelector("#summary");
const playlistUrl = document.querySelector("#playlistUrl");
const video = document.querySelector("#video");
const nowTitle = document.querySelector("#nowTitle");
const nowMeta = document.querySelector("#nowMeta");
const copyUrl = document.querySelector("#copyUrl");

let playlist = { channels: [] };
let currentUrl = "";

async function loadPlaylist() {
  const response = await fetch(playlistUrl.value);
  if (!response.ok) throw new Error(`Failed to load playlist: ${response.status}`);
  playlist = await response.json();
  populateFilters();
  render();
}

function populateFilters() {
  const groups = [...new Set(playlist.channels.map((channel) => channel["group-title"] || channel.group_title || "").filter(Boolean))].sort();
  const countries = [...new Set(playlist.channels.map((channel) => channel.country || "").filter(Boolean))].sort();

  groupFilter.innerHTML = '<option value="">All groups</option>' + groups.map((group) => `<option>${group}</option>`).join("");
  countryFilter.innerHTML = '<option value="">All countries</option>' + countries.map((country) => `<option>${country}</option>`).join("");
}

function filteredChannels() {
  const query = search.value.trim().toLowerCase();
  const group = groupFilter.value;
  const country = countryFilter.value;

  return playlist.channels.filter((channel) => {
    const haystack = `${channel.name} ${channel["group-title"] || channel.group_title || ""} ${channel.country || ""} ${channel.language || ""}`.toLowerCase();
    return (!query || haystack.includes(query)) && (!group || (channel["group-title"] || channel.group_title) === group) && (!country || channel.country === country);
  });
}

function render() {
  const channels = filteredChannels();
  summaryEl.textContent = `${channels.length} of ${playlist.channels.length} channels shown`;
  channelsEl.innerHTML = channels.map((channel) => `
    <button class="channel ${channel.url === currentUrl ? "active" : ""}" type="button" data-url="${channel.url}">
      <strong>${channel.name}</strong>
      <small>${channel["group-title"] || channel.group_title || "Uncategorized"}${channel.country ? " · " + channel.country : ""}${channel.valid === false ? " · offline" : channel.valid === true ? " · online" : ""}</small>
    </button>
  `).join("");

  channelsEl.querySelectorAll(".channel").forEach((button) => {
    button.addEventListener("click", () => play(button.dataset.url));
  });
}

function play(url) {
  currentUrl = url;
  const channel = playlist.channels.find((item) => item.url === url);

  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(url);
    hls.attachMedia(video);
  } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
    video.src = url;
  } else {
    nowTitle.textContent = "HLS playback not supported";
    nowMeta.textContent = "This browser needs HLS.js support.";
    return;
  }

  nowTitle.textContent = channel?.name || "Selected channel";
  nowMeta.textContent = `${channel?.["group-title"] || channel?.group_title || "Uncategorized"} · ${channel?.country || "INT"} · ${url}`;
  video.play().catch(() => {});
  render();
}

copyUrl.addEventListener("click", async () => {
  await navigator.clipboard.writeText(currentUrl);
});

[search, groupFilter, countryFilter].forEach((control) => control.addEventListener("input", render));
playlistUrl.addEventListener("change", () => loadPlaylist().catch((error) => { summaryEl.textContent = error.message; }));

loadPlaylist().catch((error) => { summaryEl.textContent = error.message; });

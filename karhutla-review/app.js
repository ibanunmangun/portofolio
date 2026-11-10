(() => {
  const asset = (name) => `../data/karhutla-kalteng/processed/${name}`;
  const state = document.getElementById('map-state');
  const detailHeading = document.getElementById('detail-heading');
  const detailCopy = document.getElementById('detail-copy');
  const detailList = document.getElementById('detail-list');
  const showState = (message, isError = false) => {
    state.hidden = false;
    state.textContent = message;
    state.style.color = isError ? '#ffcbc3' : '';
  };
  const hideState = () => { state.hidden = true; };
  const fetchJson = async (name) => {
    const response = await fetch(asset(name));
    if (!response.ok) throw new Error(`${name} could not be loaded`);
    return response.json();
  };
  const formatTimestamp = (value) => new Date(value).toLocaleString('en-GB', {
    dateStyle: 'medium', timeStyle: 'short', timeZone: 'UTC'
  }) + ' UTC';
  const displayCluster = (feature) => {
    const p = feature.properties;
    detailHeading.textContent = p.cluster_id;
    detailCopy.textContent = p.interpretation_note;
    const entries = [
      ['Review status', p.review_status],
      ['Signal count', String(p.signal_count)],
      ['High-confidence signals', String(p.high_confidence_count)],
      ['First seen', formatTimestamp(p.first_seen_utc)],
      ['Last seen', formatTimestamp(p.last_seen_utc)],
      ['Kabupaten context', p.kabupaten || 'Not available']
    ];
    detailList.replaceChildren();
    for (const [term, value] of entries) {
      const row = document.createElement('div');
      const label = document.createElement('dt');
      const content = document.createElement('dd');
      label.textContent = term;
      content.textContent = value;
      row.append(label, content);
      detailList.append(row);
    }
    detailList.hidden = false;
  };
  const markerElement = (className, label) => {
    const node = document.createElement('button');
    node.className = className;
    node.type = 'button';
    node.setAttribute('aria-label', label);
    return node;
  };
  const init = async () => {
    try {
      showState('Loading snapshot layers.');
      const [admin, clusters, signals] = await Promise.all([
        fetchJson('kalteng-admin2.geojson'),
        fetchJson('clusters-review.geojson'),
        fetchJson('signals-high.geojson')
      ]);
      if (!admin.features.length || !clusters.features.length) {
        showState('This snapshot does not contain displayable review units.');
        return;
      }
      const map = L.map('map', { zoomControl: true, attributionControl: true });
      map.attributionControl.setPrefix(false);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);
      const adminLayer = L.geoJSON(admin, {
        style: { color: '#d6ded1', weight: 1, opacity: 0.6, fillOpacity: 0 }
      }).addTo(map);
      const signalLayer = L.geoJSON(signals, {
        pointToLayer: (feature, latlng) => L.marker(latlng, {
          icon: L.divIcon({ className: '', html: '<span class="signal-marker" aria-hidden="true"></span>', iconSize: [7, 7], iconAnchor: [3, 3] }),
          keyboard: false, interactive: false
        })
      }).addTo(map);
      const clusterLayer = L.geoJSON(clusters, {
        pointToLayer: (feature, latlng) => {
          const label = `${feature.properties.cluster_id}, ${feature.properties.signal_count} signals`;
          return L.marker(latlng, {
            icon: L.divIcon({ className: '', html: markerElement('cluster-marker', label).outerHTML, iconSize: [16, 16], iconAnchor: [8, 8] }),
            title: label, keyboard: true
          });
        },
        onEachFeature: (feature, layer) => {
          layer.on('click keypress', (event) => {
            if (event.type !== 'keypress' || event.originalEvent.key === 'Enter' || event.originalEvent.key === ' ') displayCluster(feature);
          });
        }
      }).addTo(map);
      const bounds = adminLayer.getBounds();
      map.fitBounds(bounds, { padding: [20, 20] });
      document.getElementById('reset-map').addEventListener('click', () => map.fitBounds(bounds, { padding: [20, 20] }));
      const layerToggle = (id, layer) => document.getElementById(id).addEventListener('change', (event) => {
        if (event.target.checked) layer.addTo(map); else map.removeLayer(layer);
      });
      layerToggle('toggle-admin', adminLayer);
      layerToggle('toggle-clusters', clusterLayer);
      layerToggle('toggle-signals', signalLayer);
      hideState();
      document.getElementById('map').setAttribute('aria-busy', 'false');
    } catch (error) {
      console.error(error);
      showState('The map snapshot could not be loaded. Refresh the page or return to the portfolio home.', true);
      document.getElementById('map').setAttribute('aria-busy', 'false');
    }
  };
  window.addEventListener('DOMContentLoaded', init);
})();

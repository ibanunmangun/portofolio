(() => {
  const asset = (name) => `../data/aceh-tamiang-flood/processed/${name}`;
  const state = document.getElementById('map-state');
  const heading = document.getElementById('detail-heading');
  const copy = document.getElementById('detail-copy');
  const details = document.getElementById('detail-list');
  const list = document.getElementById('area-list');
  const showState = (message, error = false) => { state.hidden = false; state.textContent = message; state.classList.toggle('error', error); };
  const hideState = () => { state.hidden = true; };
  const getJson = async (name) => {
    const response = await fetch(asset(name));
    if (!response.ok) throw new Error(`${name} could not be loaded`);
    return response.json();
  };
  const setDetails = (feature) => {
    const p = feature.properties;
    const named = p.report_state === 'named_in_report';
    heading.textContent = p.subdistrict;
    copy.textContent = named
      ? 'This subdistrict was named in the 16 November 2026 report snapshot.'
      : 'This subdistrict was not named in the 16 November report snapshot. That does not establish that it was unaffected.';
    const entries = [
      ['Report status', named ? 'Named in report snapshot' : 'Not named in this snapshot'],
      ['Regency', p.regency],
      ['Report date', p.report_date],
      ['Map meaning', named ? 'Reported administrative footprint' : 'Administrative reference context'],
    ];
    details.replaceChildren();
    entries.forEach(([term, value]) => {
      const row = document.createElement('div');
      const dt = document.createElement('dt');
      const dd = document.createElement('dd');
      dt.textContent = term;
      dd.textContent = value;
      row.append(dt, dd);
      details.append(row);
    });
    details.hidden = false;
  };
  const init = async () => {
    try {
      showState('Loading report footprint.');
      const [admin, report] = await Promise.all([getJson('aceh-tamiang-admin3.geojson'), getJson('reported-impact-footprint.geojson')]);
      if (!admin.features.length || !report.features.length) return showState('This report snapshot has no displayable administrative areas.');
      const map = L.map('map', { zoomControl: true, attributionControl: true });
      map.attributionControl.setPrefix(false);
      const adminLayer = L.geoJSON(admin, {
        style: { color: '#718071', weight: 1, fillColor: '#1b241c', fillOpacity: 0.42 },
        onEachFeature: (feature, layer) => layer.on('click', () => setDetails(feature)),
      }).addTo(map);
      const reportLayer = L.geoJSON(report, {
        style: { color: '#ffd59b', weight: 2, fillColor: '#cc653f', fillOpacity: 0.7 },
        onEachFeature: (feature, layer) => {
          layer.on('click', () => setDetails(feature));
          const tooltip = document.createElement('span');
          tooltip.textContent = feature.properties.subdistrict;
          layer.bindTooltip(tooltip, { sticky: true, direction: 'top' });
        },
      }).addTo(map);
      const bounds = adminLayer.getBounds();
      map.fitBounds(bounds, { padding: [20, 20] });
      document.getElementById('reset-map').addEventListener('click', () => map.fitBounds(bounds, { padding: [20, 20] }));
      report.features.sort((a, b) => a.properties.subdistrict.localeCompare(b.properties.subdistrict)).forEach((feature) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = feature.properties.subdistrict;
        button.addEventListener('click', () => {
          setDetails(feature);
          const layer = reportLayer.getLayers().find((item) => item.feature.properties.admin_id === feature.properties.admin_id);
          if (layer) map.fitBounds(layer.getBounds(), { padding: [35, 35], maxZoom: 10 });
        });
        list.append(button);
      });
      hideState();
      document.getElementById('map').setAttribute('aria-busy', 'false');
    } catch (error) {
      console.error(error);
      showState('The report footprint could not be loaded. Refresh the page or return to the portfolio home.', true);
      document.getElementById('map').setAttribute('aria-busy', 'false');
    }
  };
  window.addEventListener('DOMContentLoaded', init);
})();
